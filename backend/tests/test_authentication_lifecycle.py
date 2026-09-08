from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from sqlalchemy import func, select

from backend.app.models.user import User, UserRole
from backend.app.models.refresh_session import RefreshSession
from backend.app.services import otp as otp_service
from backend.app.services import registration as registration_service
from backend.app.services.authentication import (
    create_authenticated_session,
    logout,
    record_authenticated_activity,
    refresh_access_token,
)
from backend.app.services.password import hash_password
from backend.app.services.token import (
    JWT_ALGORITHM,
    _get_jwt_secret,
    create_access_token,
    decode_access_token,
)
from backend.app.api.dependencies import get_current_user


def _session_for_access_token(db, access_token: str) -> RefreshSession:
    session_id = decode_access_token(access_token)["sid"]
    return db.scalar(
        select(RefreshSession).where(RefreshSession.id == session_id)
    )


def test_login_access_token_contains_session_id(db, normal_user):
    access_token, _ = create_authenticated_session(db, normal_user)

    payload = decode_access_token(access_token)

    assert payload["sub"] == normal_user.id
    assert payload["sid"] == _session_for_access_token(db, access_token).id


def test_access_token_without_sid_is_invalid(normal_user):
    token = jwt.encode(
        {
            "sub": str(normal_user.id),
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        _get_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )

    try:
        decode_access_token(token)
    except ValueError:
        pass
    else:
        raise AssertionError("access token without sid must be rejected")


def test_valid_session_allows_authenticated_request(client, db, normal_user):
    access_token, _ = create_authenticated_session(db, normal_user)

    response = client.get(
        "/api/v1/topics",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200


def test_revoked_session_rejects_existing_access_token(client, db, normal_user):
    access_token, _ = create_authenticated_session(db, normal_user)
    session = _session_for_access_token(db, access_token)
    session.revoked_at = datetime.now(timezone.utc)
    db.commit()

    response = client.get(
        "/api/v1/topics",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401


def test_idle_expiry_rejects_and_revokes_session(client, db, normal_user):
    access_token, _ = create_authenticated_session(db, normal_user)
    session = _session_for_access_token(db, access_token)
    session.last_activity_at = datetime.now(timezone.utc) - timedelta(hours=72)
    db.commit()

    response = client.get(
        "/api/v1/topics",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    db.refresh(session)
    assert response.status_code == 401
    assert session.revoked_at is not None


def test_successful_request_extends_activity(client, db, normal_user):
    access_token, _ = create_authenticated_session(db, normal_user)
    session = _session_for_access_token(db, access_token)
    previous_activity = datetime.now(timezone.utc) - timedelta(hours=1)
    session.last_activity_at = previous_activity
    db.commit()

    response = client.get(
        "/api/v1/topics",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    db.refresh(session)
    assert response.status_code == 200
    assert session.last_activity_at > previous_activity


def test_failed_request_does_not_extend_activity(client, db, normal_user):
    access_token, _ = create_authenticated_session(db, normal_user)
    session = _session_for_access_token(db, access_token)
    previous_activity = datetime.now(timezone.utc) - timedelta(hours=1)
    session.last_activity_at = previous_activity
    db.commit()

    response = client.get(
        "/api/v1/topics/999999",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    db.refresh(session)
    assert response.status_code == 404
    assert session.last_activity_at == previous_activity


def test_refresh_preserves_activity_and_binds_successor_sid(
    db,
    normal_user,
):
    access_token, refresh_token = create_authenticated_session(db, normal_user)
    predecessor = _session_for_access_token(db, access_token)
    previous_activity = datetime.now(timezone.utc) - timedelta(hours=1)
    predecessor.last_activity_at = previous_activity
    db.commit()

    successor_access, successor_refresh = refresh_access_token(
        db,
        refresh_token,
    )
    successor = _session_for_access_token(db, successor_access)

    assert successor_refresh
    assert successor.id != predecessor.id
    assert successor.last_activity_at == previous_activity
    assert decode_access_token(successor_access)["sid"] == successor.id
    assert predecessor.revoked_at is not None

    try:
        refresh_access_token(db, refresh_token)
    except ValueError as exc:
        assert str(exc) == "Invalid refresh token"
    else:
        raise AssertionError("revoked predecessor must not refresh")


def test_refresh_at_idle_boundary_fails_and_revokes_predecessor(
    db,
    normal_user,
):
    _, refresh_token = create_authenticated_session(db, normal_user)
    session = db.scalar(
        select(RefreshSession).where(
            RefreshSession.user_id == normal_user.id,
            RefreshSession.revoked_at.is_(None),
        )
    )
    database_now = db.scalar(select(func.clock_timestamp()))
    session.last_activity_at = database_now - timedelta(hours=72)
    db.commit()

    try:
        refresh_access_token(db, refresh_token)
    except ValueError as exc:
        assert str(exc) == "Invalid refresh token"
    else:
        raise AssertionError("refresh at the idle boundary must fail")

    db.refresh(session)
    assert session.revoked_at is not None


def test_refresh_after_idle_boundary_fails(
    db,
    normal_user,
):
    _, refresh_token = create_authenticated_session(db, normal_user)
    session = db.scalar(
        select(RefreshSession).where(
            RefreshSession.user_id == normal_user.id,
            RefreshSession.revoked_at.is_(None),
        )
    )
    database_now = db.scalar(select(func.clock_timestamp()))
    session.last_activity_at = database_now - timedelta(hours=72, seconds=1)
    db.commit()

    try:
        refresh_access_token(db, refresh_token)
    except ValueError as exc:
        assert str(exc) == "Invalid refresh token"
    else:
        raise AssertionError("refresh after the idle boundary must fail")


def test_refresh_at_and_after_credential_expiry_fail(db, normal_user):
    for offset in (timedelta(0), -timedelta(seconds=1)):
        _, refresh_token = create_authenticated_session(db, normal_user)
        session = db.scalar(
            select(RefreshSession)
            .where(
                RefreshSession.user_id == normal_user.id,
                RefreshSession.revoked_at.is_(None),
            )
            .order_by(RefreshSession.id.desc())
        )
        database_now = db.scalar(select(func.clock_timestamp()))
        session.expires_at = database_now + offset
        db.commit()

        try:
            refresh_access_token(db, refresh_token)
        except ValueError as exc:
            assert str(exc) == "Invalid refresh token"
        else:
            raise AssertionError("expired refresh credential must fail")


def test_cross_user_session_id_is_rejected(client, db, normal_user):
    other_user = User(
        first_name="Other",
        last_name="User",
        username="other_user",
        email="other_user@example.com",
        password_hash=hash_password("TestPassword123!"),
        role=UserRole.USER,
        email_verified=True,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    other_access, _ = create_authenticated_session(db, other_user)
    other_session = _session_for_access_token(db, other_access)
    normal_access, _ = create_authenticated_session(db, normal_user)
    normal_payload = decode_access_token(normal_access)

    cross_user_token = jwt.encode(
        {
            **normal_payload,
            "sub": str(normal_user.id),
            "sid": str(other_session.id),
        },
        _get_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )

    response = client.get(
        "/api/v1/topics",
        headers={"Authorization": f"Bearer {cross_user_token}"},
    )

    assert response.status_code == 401


def test_logout_revokes_session_and_existing_access_token(
    client,
    db,
    normal_user,
):
    access_token, refresh_token = create_authenticated_session(db, normal_user)

    logout(db, refresh_token)

    response = client.get(
        "/api/v1/topics",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401


def test_registration_completion_issues_session_bound_access_token(
    db,
    monkeypatch,
):
    email = "slice-b-registration@example.com"
    monkeypatch.setattr(otp_service, "generate_otp", lambda: "123456")
    monkeypatch.setattr(registration_service, "send_otp_email", lambda **_: None)

    registration_service.start_registration(db, "Jane", "Doe", email)
    proof = registration_service.verify_registration_otp(db, email, "123456")
    user, access_token, refresh_token = registration_service.complete_registration(
        db,
        email,
        "registered1",
        "longenough1A!",
        proof,
    )

    session = _session_for_access_token(db, access_token)
    payload = decode_access_token(access_token)

    assert user.email_verified is True
    assert refresh_token
    assert session.user_id == user.id
    assert payload["sub"] == user.id
    assert payload["sid"] == session.id
    assert session.last_activity_at is not None


def test_atomic_activity_update_never_moves_timestamp_backwards(
    db,
    normal_user,
):
    access_token, _ = create_authenticated_session(db, normal_user)
    session = _session_for_access_token(db, access_token)
    newer_activity = datetime.now(timezone.utc)
    session.last_activity_at = newer_activity
    db.commit()

    assert record_authenticated_activity(db, session.id) == 1
    db.refresh(session)
    assert session.last_activity_at >= newer_activity


def test_missing_session_is_rejected_by_dependency(db, normal_user):
    access_token = create_access_token(normal_user.id, 999999999)

    try:
        get_current_user(
            request=type("Request", (), {"state": type("State", (), {})()})(),
            credentials=type(
                "Credentials",
                (),
                {"scheme": "Bearer", "credentials": access_token},
            )(),
            db=db,
        )
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("unknown session must be rejected")

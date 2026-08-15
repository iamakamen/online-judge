import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://online_judge:dev_password_change_me"
    "@127.0.0.1:5432/online_judge_test",
)

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from backend.app.db.base import Base
from backend.app.db.session import engine, get_db
from backend.app.main import app
from backend.app.models.problem import Problem
from backend.app.models.refresh_session import RefreshSession
from backend.app.models.test_case import TestCase
from backend.app.models.topic import Topic
from backend.app.models.user import User, UserRole
from backend.app.models.user_problem_progress import UserProblemProgress
from backend.app.services.password import hash_password
from backend.app.services.token import create_access_token


TestSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def clean_database(db: Session) -> Generator[None, None, None]:
    db.execute(delete(UserProblemProgress))
    db.execute(delete(TestCase))
    db.execute(delete(Problem))
    db.execute(delete(Topic))
    db.execute(delete(RefreshSession))
    db.execute(delete(User))
    db.commit()

    yield

    db.rollback()
    db.execute(delete(UserProblemProgress))
    db.execute(delete(TestCase))
    db.execute(delete(Problem))
    db.execute(delete(Topic))
    db.execute(delete(RefreshSession))
    db.execute(delete(User))
    db.commit()


@pytest.fixture()
def admin_user(db: Session) -> User:
    user = User(
        first_name="Test",
        last_name="Admin",
        username="test_admin",
        email="test_admin@example.com",
        password_hash=hash_password("TestPassword123!"),
        role=UserRole.ADMIN,
        email_verified=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture()
def normal_user(db: Session) -> User:
    user = User(
        first_name="Test",
        last_name="User",
        username="test_user",
        email="test_user@example.com",
        password_hash=hash_password("TestPassword123!"),
        role=UserRole.USER,
        email_verified=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture()
def admin_token(admin_user: User) -> str:
    return create_access_token(admin_user.id)


@pytest.fixture()
def user_token(normal_user: User) -> str:
    return create_access_token(normal_user.id)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    def override_get_db():
        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers(admin_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {admin_token}",
    }


@pytest.fixture()
def user_headers(user_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {user_token}",
    }

from backend.app.models.problem import Difficulty, Problem
from backend.app.models.topic import Topic
from backend.app.models.user_problem_progress import UserProblemProgress


def test_dashboard_requires_authentication(client):
    response = client.get("/api/v1/dashboard")

    assert response.status_code == 401


def test_authenticated_dashboard_returns_v1_statistics(
    client,
    user_headers,
):
    response = client.get(
        "/api/v1/dashboard",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "first_name": "Test",
        "solved_count": 0,
        "day_streak": 0,
        "global_rank": "N/A",
    }


def test_dashboard_counts_only_current_users_solved_progress(
    client,
    user_headers,
    normal_user,
    admin_user,
    db,
):
    topic = Topic(name="Test Topic", slug="test-topic", display_order=1)
    db.add(topic)
    db.flush()

    solved_problem = Problem(
        topic_id=topic.id,
        title="Solved Problem",
        slug="solved-problem",
        statement="Statement",
        constraints="Constraints",
        difficulty=Difficulty.EASY,
        tags=["test"],
        starter_code={"python": "", "cpp": ""},
        time_limit_ms=1000,
        memory_limit_mb=128,
    )
    other_users_problem = Problem(
        topic_id=topic.id,
        title="Other User Problem",
        slug="other-user-problem",
        statement="Statement",
        constraints="Constraints",
        difficulty=Difficulty.EASY,
        tags=["test"],
        starter_code={"python": "", "cpp": ""},
        time_limit_ms=1000,
        memory_limit_mb=128,
    )
    db.add_all([solved_problem, other_users_problem])
    db.flush()
    db.add_all(
        [
            UserProblemProgress(
                user_id=normal_user.id,
                problem_id=solved_problem.id,
                solved=True,
            ),
            UserProblemProgress(
                user_id=admin_user.id,
                problem_id=other_users_problem.id,
                solved=True,
            ),
        ]
    )
    db.commit()

    response = client.get("/api/v1/dashboard", headers=user_headers)

    assert response.status_code == 200
    assert response.json()["solved_count"] == 1

import sqlite3
import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    database = tmp_path / "test_tasks.db"

    app = create_app({
        "TESTING": True,
        "DATABASE": str(database),
    })

    with app.test_client() as test_client:
        yield test_client


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"My To-Do List" in response.data


def test_add_task(client):
    response = client.post(
        "/add",
        data={"title": "Study Python"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Study Python" in response.data


def test_empty_task_is_not_added(client):
    response = client.post(
        "/add",
        data={"title": "   "},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"No tasks yet" in response.data


def test_complete_task(client):
    client.post("/add", data={"title": "Test application"})

    with sqlite3.connect(client.application.config["DATABASE"]) as db:
        task_id = db.execute(
            "SELECT id FROM tasks"
        ).fetchone()[0]

    response = client.post(
        f"/complete/{task_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"completed" in response.data


def test_delete_task(client):
    client.post("/add", data={"title": "Delete this task"})

    with sqlite3.connect(client.application.config["DATABASE"]) as db:
        task_id = db.execute(
            "SELECT id FROM tasks"
        ).fetchone()[0]

    response = client.post(
        f"/delete/{task_id}",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Delete this task" not in response.data
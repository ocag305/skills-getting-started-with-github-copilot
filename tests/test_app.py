from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


orig_activities = deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: reset the in-memory activities before each test
    activities.clear()
    activities.update(deepcopy(orig_activities))
    yield


def test_get_activities():
    # Arrange (fixture provides client and activities)
    # Act
    res = client.get("/activities")
    # Assert
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "test_user@example.com"

    # Act
    res = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert res.status_code == 200
    assert res.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = "dup_user@example.com"
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    # Act
    res = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert res.status_code == 400
    assert "already signed up" in res.json().get("detail", "")


def test_signup_not_found():
    # Arrange
    email = "noone@example.com"

    # Act
    res = client.post("/activities/NoSuchActivity/signup", params={"email": email})

    # Assert
    assert res.status_code == 404

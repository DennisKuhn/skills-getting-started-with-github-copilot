import copy
import pytest
from fastapi.testclient import TestClient
import src.app as app_module
from src.app import app

INITIAL_ACTIVITIES = None


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict to its original state before each test."""
    global INITIAL_ACTIVITIES
    if INITIAL_ACTIVITIES is None:
        INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_all(client):
    # Arrange: client is ready, activities pre-loaded

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_get_activities_has_expected_fields(client):
    # Arrange: client is ready, activities pre-loaded

    # Act
    response = client.get("/activities")

    # Assert
    chess = response.json()["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess


# --- POST /activities/{activity_name}/signup ---

def test_signup_success(client):
    # Arrange
    email = "new@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant(client):
    # Arrange
    email = "new@mergington.edu"
    activity = "Chess Club"

    # Act
    client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange: michael is already registered
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    email = "test@mergington.edu"
    activity = "Unknown Activity"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


# --- DELETE /activities/{activity_name}/unregister ---

def test_unregister_success(client):
    # Arrange: michael is already registered
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant(client):
    # Arrange: michael is already registered
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_unregister_not_registered_returns_404(client):
    # Arrange
    email = "nobody@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    email = "michael@mergington.edu"
    activity = "Unknown Activity"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

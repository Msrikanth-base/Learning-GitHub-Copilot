from fastapi.testclient import TestClient
import copy
import pytest

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities after each test to avoid cross-test pollution."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # A few known activities should exist
    assert "Chess Club" in data
    assert "Science Club" in data


def test_signup_unregister_flow():
    activity = "Science Club"
    email = "test.user@mergington.edu"

    # ensure not present initially
    assert email not in app_module.activities[activity]["participants"]

    # sign up
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # signing up again should return 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # unregister
    r3 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r3.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # unregistering again should fail
    r4 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r4.status_code == 400


def test_missing_activity_errors():
    email = "who@nowhere.edu"
    r = client.post("/activities/Nonexistent%20Activity/signup?email={}".format(email))
    assert r.status_code == 404

    r2 = client.post("/activities/Nonexistent%20Activity/unregister?email={}".format(email))
    assert r2.status_code == 404

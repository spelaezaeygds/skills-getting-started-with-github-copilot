from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)


def test_root_redirects_to_index():
    # ask TestClient not to follow redirects so we can inspect location header
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 308)
    assert "/static/index.html" in response.headers.get("location", "")


def test_get_activities_structure():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # each value should have expected keys
    for activity, details in data.items():
        assert set(details.keys()) == {"description", "schedule", "max_participants", "participants"}
        assert isinstance(details["participants"], list)


def test_signup_success():
    email = "new@mergington.edu"
    resp = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]
    # verify participant added
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_nonexistent_activity():
    resp = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_signup_duplicate_email():
    email = app_module.activities["Chess Club"]["participants"][0]
    resp = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert resp.status_code == 400


def test_signup_at_capacity():
    # artificially set max_participants to current count
    act = app_module.activities["Gym Class"]
    act["max_participants"] = len(act["participants"])
    resp = client.post("/activities/Gym%20Class/signup", params={"email": "full@mergington.edu"})
    assert resp.status_code == 400
    assert "capacity" in resp.json()["detail"].lower()


def test_remove_success():
    email = app_module.activities["Chess Club"]["participants"][0]
    resp = client.delete(f"/activities/Chess%20Club/participants/{email}")
    assert resp.status_code == 200
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_activity():
    resp = client.delete("/activities/Fake/participants/test@a.com")
    assert resp.status_code == 404


def test_remove_nonexistent_participant():
    resp = client.delete("/activities/Chess%20Club/participants/notfound@a.com")
    assert resp.status_code == 404

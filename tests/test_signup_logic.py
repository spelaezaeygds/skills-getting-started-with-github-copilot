import pytest

from src import app as app_module
from fastapi import HTTPException


@pytest.fixture(autouse=True)
def reset_state():
    # reuse conftest fixture by importing activities again
    import copy
    app_module.activities = copy.deepcopy(app_module.activities)


def test_signup_duplicate_raises():
    # use first participant from Chess Club
    email = app_module.activities["Chess Club"]["participants"][0]
    with pytest.raises(HTTPException) as excinfo:
        app_module.signup_for_activity("Chess Club", email)
    assert excinfo.value.status_code == 400


def test_signup_capacity_raises():
    act = app_module.activities["Gym Class"]
    act["max_participants"] = len(act["participants"])
    with pytest.raises(HTTPException) as excinfo:
        app_module.signup_for_activity("Gym Class", "extra@a.com")
    assert excinfo.value.status_code == 400


def test_remove_nonexistent_participant_raises():
    with pytest.raises(HTTPException) as excinfo:
        app_module.remove_participant("Chess Club", "nope@a.com")
    assert excinfo.value.status_code == 404


def test_remove_success_logic():
    email = app_module.activities["Chess Club"]["participants"][0]
    resp = app_module.remove_participant("Chess Club", email)
    assert "Removed" in resp["message"]
    assert email not in app_module.activities["Chess Club"]["participants"]

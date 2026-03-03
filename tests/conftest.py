import copy
import pytest

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """Deep-copy the original activities dict before each test.
    This ensures tests run in isolation and mutations don't leak.
    """
    original = copy.deepcopy(app_module.activities)
    app_module.activities = original
    yield
    # after test the fixture scope ends; we don't need to restore since each test does its own copy

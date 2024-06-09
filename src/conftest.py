import pytest

from app.conf import get_app_settings

pytest_plugins = [
    "app.fixtures",
    "storage.fixtures",
]


@pytest.fixture
def settings():
    return get_app_settings()

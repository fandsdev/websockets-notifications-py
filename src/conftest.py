import pytest

from app.conf import Settings, get_app_settings

pytest_plugins = [
    "app.fixtures",
    "storage.fixtures",
]


@pytest.fixture
def settings() -> Settings:
    return get_app_settings()

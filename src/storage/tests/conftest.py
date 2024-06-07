import pytest

from storage import SubscriptionStorage


@pytest.fixture
def storage():
    return SubscriptionStorage()

import pytest

from app.testing import MockedWebSocketServerProtocol
from storage import SubscriptionStorage


@pytest.fixture
def storage():
    return SubscriptionStorage()


@pytest.fixture
def ws():
    return MockedWebSocketServerProtocol()

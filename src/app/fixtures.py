import pytest

from app.testing import MockedWebSocketServerProtocol


@pytest.fixture
def ws():
    return MockedWebSocketServerProtocol()


@pytest.fixture
def ya_ws():
    return MockedWebSocketServerProtocol()

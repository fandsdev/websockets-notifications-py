import pytest

from app.testing import MockedWebSocketServerProtocol


@pytest.fixture
def create_ws():
    return lambda: MockedWebSocketServerProtocol()


@pytest.fixture
def ws(create_ws):
    return create_ws()


@pytest.fixture
def ya_ws(create_ws):
    return create_ws()

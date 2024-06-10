import pytest
from collections.abc import Callable

from app.testing import MockedWebSocketServerProtocol


@pytest.fixture
def create_ws() -> Callable[[], MockedWebSocketServerProtocol]:
    return lambda: MockedWebSocketServerProtocol()


@pytest.fixture
def ws(create_ws) -> MockedWebSocketServerProtocol:
    return create_ws()


@pytest.fixture
def ya_ws(create_ws) -> MockedWebSocketServerProtocol:
    return create_ws()

import pytest

from handlers.dto import AuthMessage, SubscribeMessage, UnsubscribeMessage
from handlers.messages_handler import WebSocketMessagesHandler

pytestmark = [
    pytest.mark.usefixtures("set_jwt_public_key"),
]


@pytest.fixture
def message_handler(storage):
    return WebSocketMessagesHandler(storage=storage)


@pytest.fixture
def auth_message(jwt_user_valid_token):
    return AuthMessage(message_id=23, message_type="Authenticate", params={"token": jwt_user_valid_token})


@pytest.fixture
def subscribe_message():
    return SubscribeMessage(message_id=24, message_type="Subscribe", params={"event": "channel1"})


@pytest.fixture
def unsubscribe_message():
    return UnsubscribeMessage(message_id=25, message_type="Unsubscribe", params={"event": "channel1"})

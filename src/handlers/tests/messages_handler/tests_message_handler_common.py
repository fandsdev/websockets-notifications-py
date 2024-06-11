import pytest

from handlers.messages_handler import WebSocketMessagesHandler


@pytest.fixture
def get_message_handler(storage):
    return lambda: WebSocketMessagesHandler(storage)


@pytest.mark.usefixtures("set_jwt_public_key")
def test_message_handler_call_auth_handler_on_auth_message(get_message_handler, auth_message, mocker, ws):
    spy_auth_handler = mocker.spy(WebSocketMessagesHandler, "handle_auth_message")

    get_message_handler().handle_message(ws, auth_message)

    spy_auth_handler.assert_called_once()


def test_message_handler_call_subscribe_handler_on_subscribe_message(get_message_handler, subscribe_message, mocker, ws_registered):
    spy_subscribe_handler = mocker.spy(WebSocketMessagesHandler, "handle_subscribe_message")

    get_message_handler().handle_message(ws_registered, subscribe_message)

    spy_subscribe_handler.assert_called_once()


def test_message_handler_call_unsubscribe_handler_on_unsubscribe_message(get_message_handler, unsubscribe_message, mocker, ws_subscribed):
    spy_unsubscribe_handler = mocker.spy(WebSocketMessagesHandler, "handle_unsubscribe_message")

    get_message_handler().handle_message(ws_subscribed, unsubscribe_message)

    spy_unsubscribe_handler.assert_called_once()

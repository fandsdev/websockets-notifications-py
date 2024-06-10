import pytest

from handlers.messages_handler import WebSocketMessagesHandler


@pytest.fixture
def get_message_handler(storage):
    return lambda: WebSocketMessagesHandler(storage)


def test_message_handler_jwk_client_settings(message_handler):
    assert message_handler.jwk_client.jwks_url == "https://auth.clowns.com/auth/realms/clowns-realm/protocol/openid-connect/certs"
    assert message_handler.jwk_client.supported_signing_algorithms == ["RS256"]


@pytest.mark.usefixtures("force_token_validation")
async def test_message_handler_call_auth_handler_on_auth_message(get_message_handler, auth_message, mocker, ws):
    spy_auth_handler = mocker.spy(WebSocketMessagesHandler, "handle_auth_message")

    await get_message_handler().handle_message(ws, auth_message)

    spy_auth_handler.assert_awaited_once()


async def test_message_handler_call_subscribe_handler_on_subscribe_message(get_message_handler, subscribe_message, mocker, ws_registered):
    spy_subscribe_handler = mocker.spy(WebSocketMessagesHandler, "handle_subscribe_message")

    await get_message_handler().handle_message(ws_registered, subscribe_message)

    spy_subscribe_handler.assert_awaited_once()


async def test_message_handler_call_unsubscribe_handler_on_unsubscribe_message(get_message_handler, unsubscribe_message, mocker, ws_subscribed):
    spy_unsubscribe_handler = mocker.spy(WebSocketMessagesHandler, "handle_unsubscribe_message")

    await get_message_handler().handle_message(ws_subscribed, unsubscribe_message)

    spy_unsubscribe_handler.assert_awaited_once()

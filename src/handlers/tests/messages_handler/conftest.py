import pytest

from handlers.dto import AuthMessage, SubscribeMessage, UnsubscribeMessage
from handlers.messages_handler import WebSocketMessagesHandler


@pytest.fixture(autouse=True)
def settings(settings):
    settings.AUTH_JWKS_URL = "https://auth.clowns.com/auth/realms/clowns-realm/protocol/openid-connect/certs"
    settings.AUTH_SUPPORTED_SIGNING_ALGORITHMS = ["RS256"]
    return settings


@pytest.fixture
def force_token_validation(mocker, valid_token):
    return mocker.patch("a12n.jwk_client.AsyncJWKClient.decode", return_value=valid_token)


@pytest.fixture
def message_handler(storage):
    return WebSocketMessagesHandler(storage=storage)


@pytest.fixture
def auth_message():
    return AuthMessage(message_id=23, message_type="Authenticate", params={"token": "some-valid-token-value"})


@pytest.fixture
def subscribe_message():
    return SubscribeMessage(message_id=24, message_type="Subscribe", params={"event": "channel1"})


@pytest.fixture
def unsubscribe_message():
    return UnsubscribeMessage(message_id=25, message_type="Unsubscribe", params={"event": "channel1"})

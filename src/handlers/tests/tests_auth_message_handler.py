import pytest

from a12n.jwk_client import AsyncJWKClientException
from app.types import DecodedValidToken
from handlers.dto import AuthMessage
from handlers.dto import SuccessResponseMessage
from handlers.exceptions import WebsocketMessageException
from handlers import WebsocketAuthMessageHandler
from storage.storage_updaters import StorageWebSocketRegister


@pytest.fixture(autouse=True)
def settings(settings):
    settings.AUTH_JWKS_URL = "https://auth.clowns.com/auth/realms/clowns-realm/protocol/openid-connect/certs"
    settings.AUTH_SUPPORTED_SIGNING_ALGORITHMS = ["RS256"]
    return settings


@pytest.fixture
def decoded_valid_token():
    return DecodedValidToken(sub="user1", exp="4852128170")  # 2123 year


@pytest.fixture
def ya_user_decoded_valid_token():
    return DecodedValidToken(sub="ya_user", exp="4852128170")


@pytest.fixture(autouse=True)
def set_token_validation(mocker, decoded_valid_token):
    return mocker.patch("a12n.jwk_client.AsyncJWKClient.decode", return_value=decoded_valid_token)


@pytest.fixture
def auth_message():
    return AuthMessage(message_id=23, message_type="Authenticate", params={"token": "some-valid-token-value"})


@pytest.fixture
def register_ws(storage):
    return lambda ws, decoded_valid_token: StorageWebSocketRegister(storage, ws, decoded_valid_token)()


@pytest.fixture
def auth_message_handler(storage):
    return WebsocketAuthMessageHandler(storage=storage)


@pytest.fixture
def handle(auth_message_handler, ws):
    def get_handler(message):
        return auth_message_handler.handle_message(ws, message)

    return get_handler


def test_auth_handler_jwk_client_settings(auth_message_handler):
    assert auth_message_handler.jwk_client.jwks_url == "https://auth.clowns.com/auth/realms/clowns-realm/protocol/openid-connect/certs"
    assert auth_message_handler.jwk_client.supported_signing_algorithms == ["RS256"]


async def test_auth_handler_response_on_correct_authenticate(handle, auth_message):
    auth_response = await handle(auth_message)

    assert isinstance(auth_response, SuccessResponseMessage)
    assert auth_response.message_type == "SuccessResponse"
    assert auth_response.incoming_message == auth_message


async def test_auth_handler_register_websocket_in_storage(handle, ws, auth_message, mocker, storage, decoded_valid_token):
    spy_websocket_register = mocker.spy(StorageWebSocketRegister, "__call__")

    await handle(auth_message)

    assert storage.is_websocket_registered(ws) is True
    spy_websocket_register.assert_called_once()
    called_service = spy_websocket_register.call_args.args[0]
    assert called_service.storage == storage
    assert called_service.websocket == ws
    assert called_service.validated_token == decoded_valid_token


async def test_auth_handler_raise_if_user_send_token_for_different_user(handle, auth_message, storage, ws, register_ws, ya_user_decoded_valid_token):
    register_ws(ws, ya_user_decoded_valid_token)

    with pytest.raises(WebsocketMessageException) as exc_info:
        await handle(auth_message)  # send valid user1 token while connection registered with ya_user

    raised_exception = exc_info.value
    assert raised_exception.error_detail == "The user has different public id"
    assert raised_exception.incoming_message == auth_message
    assert storage.is_websocket_registered(ws) is True, "The existed connection should not be touched"


async def test_auth_handler_raise_if_user_try_to_auth_with_expired_token(handle, ws, auth_message, set_token_validation, storage):
    set_token_validation.side_effect = AsyncJWKClientException("The token is expired")

    with pytest.raises(WebsocketMessageException) as exc_info:
        await handle(auth_message)

    raised_exception = exc_info.value
    assert raised_exception.error_detail == "The token is expired"
    assert raised_exception.incoming_message == auth_message
    assert storage.is_websocket_registered(ws) is False, "The ws should not be added to registered websockets"

import pytest

from app.types import DecodedValidToken
from app.testing import MockedWebSocketServerProtocol
from storage.storage_updaters.storage_connection_register import StorageConnectionRegister
from storage.storage_updaters.storage_user_subscriber import StorageUserSubscriber
from storage.types import SubscriptionFullQualifiedIdentifier


@pytest.fixture
def valid_token():
    return DecodedValidToken(sub="user1", exp=4700000000)  # year of expiration 2118


@pytest.fixture
def ya_valid_token():
    return DecodedValidToken(sub="user1", exp=5700000000)


@pytest.fixture
def ya_user_valid_token():
    return DecodedValidToken(sub="user2", exp=7700000000)


@pytest.fixture
def ws_connection():
    return MockedWebSocketServerProtocol()


@pytest.fixture
def ya_ws_connection():
    return MockedWebSocketServerProtocol()


@pytest.fixture
def authenticate_ws(storage):
    def authenticate(ws_connection, token):
        StorageConnectionRegister(storage, ws_connection, token)()

    return authenticate


@pytest.fixture
def ws_authenticated(ws_connection, valid_token, authenticate_ws):
    authenticate_ws(ws_connection, valid_token)
    return ws_connection


@pytest.fixture
def event():
    return "omniNotification"


@pytest.fixture
def event_subscription_key():
    return ("userId",)


@pytest.fixture
def event_subscription_identifier():
    return ("userX",)


@pytest.fixture
def subscription_fqi(event, event_subscription_key, event_subscription_identifier):
    return SubscriptionFullQualifiedIdentifier(
        event=event,
        subscription_key=event_subscription_key,
        subscription_identifier=event_subscription_identifier,
    )


@pytest.fixture
def subscribe_ws(storage):
    def subscribe(ws_connection, subscription_fqi):
        StorageUserSubscriber(
            storage=storage,
            websocket=ws_connection,
            subscription_fqi=subscription_fqi,
        )()

    return subscribe

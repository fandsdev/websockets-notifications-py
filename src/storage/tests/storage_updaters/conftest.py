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
def ws():
    return MockedWebSocketServerProtocol()


@pytest.fixture
def ya_ws():
    return MockedWebSocketServerProtocol()


@pytest.fixture
def register_ws(storage):
    def register(ws, token):
        StorageConnectionRegister(storage, ws, token)()

    return register


@pytest.fixture
def ws_registered(ws, valid_token, register_ws):
    register_ws(ws, valid_token)
    return ws


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
    def subscribe(ws, subscription_fqi):
        StorageUserSubscriber(
            storage=storage,
            websocket=ws,
            subscription_fqi=subscription_fqi,
        )()

    return subscribe


@pytest.fixture
def ws_subscribed(ws_registered, subscribe_ws, subscription_fqi):
    subscribe_ws(ws_registered, subscription_fqi)
    return ws_registered

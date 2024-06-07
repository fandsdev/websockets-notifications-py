import pytest

from storage.exceptions import StorageOperationException
from storage.storage_updaters import StorageUserSubscriber


@pytest.fixture
def same_user_ya_ws_registered(ya_ws, ya_valid_token, register_ws):
    register_ws(ya_ws, ya_valid_token)
    return ya_ws


@pytest.fixture
def ya_user_ws_registered(ya_ws, ya_user_valid_token, register_ws):
    register_ws(ya_ws, ya_user_valid_token)
    return ya_ws


@pytest.fixture
def subscribe(storage):
    def subscribe(ws, event):
        StorageUserSubscriber(storage=storage, websocket=ws, event=event)()

    return subscribe


def test_create_subscription_in_storage_subscriptions(ws_registered, subscribe, storage, event):
    subscribe(ws_registered, event)

    assert event in storage.subscriptions, "Event should be created in storage"
    assert storage.subscriptions[event] == {"user1"}, "User id should be added to subscription"
    assert storage.user_connections["user1"].user_subscriptions == {event}, "Subscription should be added to user subscriptions"


def test_subscription_with_same_params_idempotent(ws_registered, subscribe, storage, event):
    subscribe(ws_registered, event)
    subscribe(ws_registered, event)

    assert len(storage.subscriptions) == 1
    assert storage.subscriptions[event] == {"user1"}
    assert storage.user_connections["user1"].user_subscriptions == {event}


def test_subscription_same_user_other_websocket_idempotent(ws_registered, same_user_ya_ws_registered, subscribe, storage, event):
    subscribe(ws_registered, event)

    subscribe(same_user_ya_ws_registered, event)

    assert len(storage.subscriptions) == 1
    assert storage.subscriptions[event] == {"user1"}
    assert storage.user_connections["user1"].user_subscriptions == {event}


def test_subscription_other_event(ws_registered, subscribe, storage, event, ya_event):
    subscribe(ws_registered, event)

    subscribe(ws_registered, ya_event)

    assert len(storage.subscriptions) == 2
    assert storage.subscriptions[event] == {"user1"}
    assert storage.subscriptions[ya_event] == {"user1"}
    assert storage.user_connections["user1"].user_subscriptions == {event, ya_event}


def test_other_user_with_same_fqi_subscribe_ok(ws_registered, ya_user_ws_registered, subscribe, storage, event):
    subscribe(ws_registered, event)

    subscribe(ya_user_ws_registered, event)

    assert storage.subscriptions[event] == {"user1", "user2"}
    assert storage.user_connections["user1"].user_subscriptions == {event}
    assert storage.user_connections["user2"].user_subscriptions == {event}


def test_other_user_subscription_to_other_event_ok(ws_registered, ya_user_ws_registered, subscribe, storage, event, ya_event):
    subscribe(ws_registered, event)

    subscribe(ya_user_ws_registered, ya_event)

    assert len(storage.subscriptions) == 2
    assert storage.subscriptions[event] == {"user1"}
    assert storage.subscriptions[ya_event] == {"user2"}
    assert storage.user_connections["user1"].user_subscriptions == {event}
    assert storage.user_connections["user2"].user_subscriptions == {ya_event}


def test_raise_if_ws_connection_not_registered(ws, subscribe, storage, event):
    with pytest.raises(StorageOperationException, match="The user is not registered"):
        subscribe(ws, event)

    assert storage.subscriptions == {}
    assert storage.user_connections == {}

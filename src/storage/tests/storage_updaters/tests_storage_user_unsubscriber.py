import pytest
from contextlib import nullcontext as does_not_raise

from storage.exceptions import StorageOperationException
from storage.storage_updaters import StorageUserUnsubscriber


@pytest.fixture
def unsubscribe(storage):
    def unsubscribe_user(ws, event):
        StorageUserUnsubscriber(storage=storage, websocket=ws, event=event)()

    return unsubscribe_user


def test_unsubscribe_user_and_clear_subscriptions(unsubscribe, ws_subscribed, storage, event):
    unsubscribe(ws_subscribed, event)

    assert storage.subscriptions == {}, "Subscription keys and all internal structures should be removed"
    assert storage.user_connections["user1"].user_subscriptions == set(), "User subscriptions should be removed"


def test_unsubscribe_user_from_event_not_touch_other_events(unsubscribe, ws_subscribed, storage, subscribe_ws, event, ya_event):
    subscribe_ws(ws_subscribed, ya_event)  # subscribe to another event

    unsubscribe(ws_subscribed, event)

    assert len(storage.subscriptions) == 1
    assert storage.subscriptions[ya_event] == {"user1"}
    assert storage.user_connections["user1"].user_subscriptions == {ya_event}


def test_do_nothing_if_unsubscribe_from_not_subscribed_event(unsubscribe, ws_registered, storage, event):
    with does_not_raise():
        unsubscribe(ws_registered, event)


@pytest.mark.usefixtures("ws_subscribed")
def test_raise_if_user_not_registered(unsubscribe, ya_ws, storage, event):
    with pytest.raises(StorageOperationException, match="The user is not registered"):
        unsubscribe(ya_ws, event)

    assert len(storage.subscriptions) == 1, "Should not changed"
    assert len(storage.user_connections["user1"].user_subscriptions) == 1, "Should not changed"

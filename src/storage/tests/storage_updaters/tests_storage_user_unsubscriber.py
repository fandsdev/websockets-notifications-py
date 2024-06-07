import pytest

from storage.exceptions import StorageOperationException
from storage.storage_updaters import StorageUserUnsubscriber
from storage.types import SubscriptionFullQualifiedIdentifier


@pytest.fixture
def unsubscribe(storage):
    def unsubscribe_user(ws, subscription_fqi):
        StorageUserUnsubscriber(
            storage=storage,
            websocket=ws,
            subscription_fqi=subscription_fqi,
        )()

    return unsubscribe_user


def test_unsubscribe_user_and_clear_subscriptions(unsubscribe, ws_subscribed, storage, subscription_fqi):
    unsubscribe(ws_subscribed, subscription_fqi)

    assert storage.subscriptions == {}, "Subscription keys and all internal structures should be removed"
    assert storage.user_connections["user1"].user_subscriptions == set(), "User subscriptions should be removed"


def test_user_unsubscribe_same_event_other_identifier(unsubscribe, subscribe_ws, ws_subscribed, storage, subscription_fqi, event, event_subscription_key):
    same_event_ya_identifier_fqi = SubscriptionFullQualifiedIdentifier(event, event_subscription_key, ("userY",))
    subscribe_ws(ws_subscribed, same_event_ya_identifier_fqi)

    unsubscribe(ws_subscribed, subscription_fqi)

    assert len(storage.subscriptions) == 1
    assert len(storage.subscriptions[event]) == 1
    assert storage.subscriptions[event][("userY"),] == {"user1"}
    assert storage.user_connections["user1"].user_subscriptions == {same_event_ya_identifier_fqi}


def test_same_user_other_subscription_key_unsubscribe_ok(unsubscribe, subscribe_ws, ws_subscribed, storage, subscription_fqi):
    other_event_fqi = SubscriptionFullQualifiedIdentifier("classifierId", ("entityId", "userId"), (100500, "userZ"))
    subscribe_ws(ws_subscribed, other_event_fqi)

    unsubscribe(ws_subscribed, subscription_fqi)

    assert len(storage.subscriptions) == 1
    assert "classifierId" in storage.subscriptions
    assert storage.subscriptions["classifierId"][100500, "userZ"] == {"user1"}
    assert storage.user_connections["user1"].user_subscriptions == {other_event_fqi}


@pytest.mark.usefixtures("ws_subscribed")
def test_raise_if_user_not_registered(unsubscribe, ya_ws, storage, subscription_fqi):
    with pytest.raises(StorageOperationException, match="The user is not registered"):
        unsubscribe(ya_ws, subscription_fqi)

    assert len(storage.subscriptions) == 1, "Should not changed"
    assert len(storage.user_connections["user1"].user_subscriptions) == 1, "Should not changed"

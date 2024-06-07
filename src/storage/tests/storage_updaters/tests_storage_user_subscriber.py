import pytest

from storage.exceptions import StorageOperationException
from storage.storage_updaters import StorageUserSubscriber
from storage.types import SubscriptionFullQualifiedIdentifier


@pytest.fixture
def ya_ws_same_user_authenticated(ya_ws_connection, ya_valid_token, authenticate_ws):
    authenticate_ws(ya_ws_connection, ya_valid_token)
    return ya_ws_connection


@pytest.fixture
def ya_user_ws_authenticated(ya_ws_connection, ya_user_valid_token, authenticate_ws):
    authenticate_ws(ya_ws_connection, ya_user_valid_token)
    return ya_ws_connection


@pytest.fixture
def subscribe(storage):
    def subscribe_user(ws, subscription_fqi):
        return StorageUserSubscriber(
            storage=storage,
            websocket=ws,
            subscription_fqi=subscription_fqi,
        )()

    return subscribe_user


def test_create_subscription_in_storage_subscriptions(ws_authenticated, subscribe, storage, event, event_subscription_identifier, subscription_fqi):
    subscribe(ws_authenticated, subscription_fqi)

    assert event in storage.subscriptions, "Event should be created in storage"
    assert event_subscription_identifier in storage.subscriptions[event], "Identifier should be created"
    assert storage.subscriptions[event][event_subscription_identifier] == {"user1"}, "User id should be added to subscription"
    assert storage.user_connections["user1"].user_subscriptions == {subscription_fqi}, "Subscription should be added to user subscriptions"


def test_subscription_with_same_params_idempotent(ws_authenticated, subscribe, storage, subscription_fqi, event, event_subscription_identifier):
    subscribe(ws_authenticated, subscription_fqi)
    subscribe(ws_authenticated, subscription_fqi)

    assert len(storage.subscriptions) == 1
    assert len(storage.subscriptions[event]) == 1
    assert len(storage.subscriptions[event][event_subscription_identifier]) == 1
    assert storage.subscriptions[event][event_subscription_identifier] == {"user1"}
    assert len(storage.user_connections["user1"].user_subscriptions) == 1


def test_subscription_same_user_other_connection_idempotent(
    ws_authenticated, ya_ws_same_user_authenticated, subscribe, storage, subscription_fqi, event, event_subscription_identifier
):
    subscribe(ws_authenticated, subscription_fqi)

    subscribe(ya_ws_same_user_authenticated, subscription_fqi)

    assert len(storage.subscriptions) == 1
    assert len(storage.subscriptions[event]) == 1
    assert storage.subscriptions[event][event_subscription_identifier] == {"user1"}
    assert len(storage.user_connections["user1"].user_subscriptions) == 1


def test_subscription_to_same_event_other_identifier(ws_authenticated, subscribe, storage, event, event_subscription_key, subscription_fqi):
    same_event_fqi = SubscriptionFullQualifiedIdentifier(event, event_subscription_key, ("userY",))
    subscribe(ws_authenticated, subscription_fqi)

    subscribe(ws_authenticated, same_event_fqi)

    assert len(storage.subscriptions) == 1
    assert len(storage.subscriptions[event]) == 2
    assert storage.subscriptions[event][("userX",)] == {"user1"}
    assert storage.subscriptions[event][("userY",)] == {"user1"}
    assert storage.user_connections["user1"].user_subscriptions == {subscription_fqi, same_event_fqi}


def test_subscription_two_different_events(ws_authenticated, subscribe, storage, subscription_fqi, event, event_subscription_identifier):
    other_event_fqi = SubscriptionFullQualifiedIdentifier("classifierId", ("userId", "projectUrn"), ("user008", "some-urn"))
    subscribe(ws_authenticated, subscription_fqi)

    subscribe(ws_authenticated, other_event_fqi)

    assert len(storage.subscriptions) == 2
    assert storage.subscriptions[event][event_subscription_identifier] == {"user1"}
    assert storage.subscriptions["classifierId"][("user008", "some-urn")] == {"user1"}
    assert storage.user_connections["user1"].user_subscriptions == {subscription_fqi, other_event_fqi}


def test_other_user_with_same_fqi_subscribe_ok(
    ws_authenticated, ya_user_ws_authenticated, subscribe, storage, subscription_fqi, event, event_subscription_identifier
):
    subscribe(ws_authenticated, subscription_fqi)

    subscribe(ya_user_ws_authenticated, subscription_fqi)

    assert storage.subscriptions[event][event_subscription_identifier] == {"user1", "user2"}
    assert storage.user_connections["user1"].user_subscriptions == {subscription_fqi}
    assert storage.user_connections["user2"].user_subscriptions == {subscription_fqi}


def test_other_user_subscription_to_other_event_ok(
    ws_authenticated, ya_user_ws_authenticated, subscribe, storage, subscription_fqi, event, event_subscription_identifier
):
    ya_subscribe_fqi = SubscriptionFullQualifiedIdentifier("classifierId", ("entityId"), (100500,))
    subscribe(ws_authenticated, subscription_fqi)

    subscribe(ya_user_ws_authenticated, ya_subscribe_fqi)

    assert len(storage.subscriptions) == 2
    assert storage.subscriptions[event][event_subscription_identifier] == {"user1"}
    assert storage.subscriptions["classifierId"][(100500,)] == {"user2"}
    assert storage.user_connections["user1"].user_subscriptions == {subscription_fqi}
    assert storage.user_connections["user2"].user_subscriptions == {ya_subscribe_fqi}


def test_raise_if_ws_connection_not_authenticated(ws_connection, subscribe, storage, subscription_fqi):
    with pytest.raises(StorageOperationException, match="The user is not authenticated"):
        subscribe(ws_connection, subscription_fqi)

    assert storage.subscriptions == {}
    assert storage.user_connections == {}

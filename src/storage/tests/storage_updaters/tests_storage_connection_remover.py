from contextlib import nullcontext as does_not_raise
import pytest

from storage.storage_updaters import StorageConnectionRemover


@pytest.fixture
def ws_subscribed(ws_authenticated, subscribe_ws, subscription_fqi):
    subscribe_ws(ws_authenticated, subscription_fqi)
    return ws_authenticated


@pytest.fixture
def ya_user_ws_authenticated(ya_ws_connection, ya_user_valid_token, authenticate_ws):
    authenticate_ws(ya_ws_connection, ya_user_valid_token)
    return ya_ws_connection


@pytest.fixture
def remove(storage):
    return lambda ws_connection: StorageConnectionRemover(storage, ws_connection)()


def test_remove_connection_and_subscriptions_from_storage(remove, ws_subscribed, storage):
    remove(ws_subscribed)

    assert storage.authenticated_connections == {}
    assert storage.user_connections == {}
    assert storage.subscriptions == {}


def test_do_not_remove_subscriptions_if_other_user_connections_exist(remove, ws_subscribed, ya_ws_connection, storage, ya_valid_token, authenticate_ws):
    authenticate_ws(ya_ws_connection, ya_valid_token)  # same user, other ws connection

    remove(ws_subscribed)

    assert len(storage.authenticated_connections) == 1
    assert ya_ws_connection in storage.authenticated_connections
    assert storage.user_connections["user1"].connections == [ya_ws_connection]
    assert storage.user_connections["user1"].user_subscriptions
    assert len(storage.subscriptions) == 1


def test_do_not_remove_subscriptions_other_user(remove, ws_subscribed, ya_user_ws_authenticated, storage):
    remove(ya_user_ws_authenticated)

    assert ya_user_ws_authenticated not in storage.authenticated_connections
    assert ws_subscribed in storage.authenticated_connections
    assert storage.user_connections["user1"].connections == [ws_subscribed]
    assert storage.user_connections["user1"].user_subscriptions
    assert len(storage.subscriptions) == 1


def test_do_not_fail_if_ws_connection_not_authenticated(remove, ws_connection):
    with does_not_raise():
        remove(ws_connection)

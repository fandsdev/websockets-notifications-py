from contextlib import nullcontext as does_not_raise
import pytest

from storage.storage_updaters import StorageConnectionRemover


@pytest.fixture
def ya_user_ws_registered(ya_ws, ya_user_valid_token, register_ws):
    register_ws(ya_ws, ya_user_valid_token)
    return ya_ws


@pytest.fixture
def remove(storage):
    return lambda ws: StorageConnectionRemover(storage, ws)()


def test_remove_websocket_and_user_subscriptions_from_storage(remove, ws_subscribed, storage):
    remove(ws_subscribed)

    assert storage.registered_websockets == {}
    assert storage.user_connections == {}
    assert storage.subscriptions == {}


def test_do_not_remove_subscriptions_if_other_user_websockets_exist(remove, ws_subscribed, ya_ws, storage, ya_valid_token, register_ws):
    register_ws(ya_ws, ya_valid_token)  # same user, other ws connection

    remove(ws_subscribed)

    assert len(storage.registered_websockets) == 1
    assert ya_ws in storage.registered_websockets
    assert storage.user_connections["user1"].websockets == [ya_ws]
    assert storage.user_connections["user1"].user_subscriptions
    assert len(storage.subscriptions) == 1


def test_do_not_remove_subscriptions_other_user(remove, ws_subscribed, ya_user_ws_registered, storage):
    remove(ya_user_ws_registered)

    assert ya_user_ws_registered not in storage.registered_websockets
    assert ws_subscribed in storage.registered_websockets
    assert storage.user_connections["user1"].websockets == [ws_subscribed]
    assert storage.user_connections["user1"].user_subscriptions
    assert len(storage.subscriptions) == 1


def test_do_not_fail_if_ws_connection_not_registered(remove, ws):
    with does_not_raise():
        remove(ws)

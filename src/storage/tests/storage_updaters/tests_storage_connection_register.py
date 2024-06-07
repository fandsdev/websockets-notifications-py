import pytest

from storage.exceptions import StorageOperationException
from storage.storage_updaters import StorageConnectionRegister
from storage.subscription_storage import SubscriptionStorage
from storage.types import ConnectedUserMeta
from storage.types import WebSocketMeta


@pytest.fixture
def register(storage: SubscriptionStorage):
    return lambda ws_connection, token: StorageConnectionRegister(
        storage=storage,
        websocket=ws_connection,
        validated_token=token,
    )()


def test_register_new_websocket_in_storage(storage, register, ws_connection, valid_token):
    register(ws_connection, valid_token)

    assert ws_connection in storage.registered_websockets
    assert storage.registered_websockets[ws_connection] == WebSocketMeta(user_id="user1", expiration_timestamp=4700000000)
    assert storage.user_connections["user1"] == ConnectedUserMeta(websockets=[ws_connection], user_subscriptions=set())


def test_if_existed_connection_then_update_connection_expiration_time(register, ws_connection, valid_token, ya_valid_token, storage):
    register(ws_connection, valid_token)

    register(ws_connection, ya_valid_token)

    assert ws_connection in storage.registered_connections
    assert storage.registered_connections[ws_connection] == WebSocketMeta(user_id="user1", expiration_timestamp=5700000000)


def test_raise_if_update_connection_with_token_from_another_user(register, storage, ws_connection, valid_token, ya_user_valid_token):
    register(ws_connection, valid_token)

    with pytest.raises(StorageOperationException, match="The user has different public id"):
        register(ws_connection, ya_user_valid_token)

    assert storage.registered_connections[ws_connection] == WebSocketMeta(
        user_id="user1", expiration_timestamp=4700000000
    ), "Existed connection should not change"


def test_user_registration_do_not_touch_other_user_connections(register, ws_connection, ya_ws_connection, storage, valid_token, ya_user_valid_token):
    register(ws_connection, valid_token)

    register(ya_ws_connection, ya_user_valid_token)

    assert storage.registered_connections[ws_connection] == WebSocketMeta(user_id="user1", expiration_timestamp=4700000000)
    assert storage.registered_connections[ya_ws_connection] == WebSocketMeta(user_id="user2", expiration_timestamp=7700000000)
    assert storage.user_connections["user1"] == ConnectedUserMeta([ws_connection], set())
    assert storage.user_connections["user2"] == ConnectedUserMeta([ya_ws_connection], set())


def test_same_user_other_websocket_added_ok(register, ws_connection, ya_ws_connection, storage, valid_token, ya_valid_token):
    register(ws_connection, valid_token)

    register(ya_ws_connection, ya_valid_token)

    assert storage.user_connections["user1"] == ConnectedUserMeta([ws_connection, ya_ws_connection], set())
    assert storage.registered_connections[ws_connection] == WebSocketMeta(user_id="user1", expiration_timestamp=4700000000)
    assert storage.registered_connections[ya_ws_connection] == WebSocketMeta(user_id="user1", expiration_timestamp=5700000000)

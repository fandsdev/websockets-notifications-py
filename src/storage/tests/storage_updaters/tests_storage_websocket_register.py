import pytest

from storage.exceptions import StorageOperationException
from storage.storage_updaters import StorageWebSocketRegister
from storage.subscription_storage import SubscriptionStorage
from storage.types import ConnectedUserMeta
from storage.types import WebSocketMeta


@pytest.fixture
def register(storage: SubscriptionStorage):
    return lambda ws, token: StorageWebSocketRegister(
        storage=storage,
        websocket=ws,
        validated_token=token,
    )()


def test_register_new_websocket_in_storage(storage, register, ws, valid_token):
    register(ws, valid_token)

    assert ws in storage.registered_websockets
    assert storage.registered_websockets[ws] == WebSocketMeta(user_id="user1", expiration_timestamp=4700000000)
    assert storage.user_connections["user1"] == ConnectedUserMeta(websockets=[ws], user_subscriptions=set())


def test_if_existed_websocket_then_update_its_expiration_time(register, ws, valid_token, ya_valid_token, storage):
    register(ws, valid_token)

    register(ws, ya_valid_token)

    assert ws in storage.registered_websockets
    assert storage.registered_websockets[ws] == WebSocketMeta(user_id="user1", expiration_timestamp=5700000000)


def test_raise_if_update_websocket_with_token_from_another_user(register, storage, ws, valid_token, ya_user_valid_token):
    register(ws, valid_token)

    with pytest.raises(StorageOperationException, match="The user has different public id"):
        register(ws, ya_user_valid_token)

    assert storage.registered_websockets[ws] == WebSocketMeta(user_id="user1", expiration_timestamp=4700000000), "Should not change registered meta"


def test_user_registration_do_not_touch_other_users(register, ws, ya_ws, storage, valid_token, ya_user_valid_token):
    register(ws, valid_token)

    register(ya_ws, ya_user_valid_token)

    assert storage.registered_websockets[ws] == WebSocketMeta(user_id="user1", expiration_timestamp=4700000000)
    assert storage.registered_websockets[ya_ws] == WebSocketMeta(user_id="user2", expiration_timestamp=7700000000)
    assert storage.user_connections["user1"] == ConnectedUserMeta([ws], set())
    assert storage.user_connections["user2"] == ConnectedUserMeta([ya_ws], set())


def test_user_registered_with_second_websocket_ok(register, ws, ya_ws, storage, valid_token, ya_valid_token):
    register(ws, valid_token)

    register(ya_ws, ya_valid_token)

    assert storage.user_connections["user1"] == ConnectedUserMeta([ws, ya_ws], set())
    assert storage.registered_websockets[ws] == WebSocketMeta(user_id="user1", expiration_timestamp=4700000000)
    assert storage.registered_websockets[ya_ws] == WebSocketMeta(user_id="user1", expiration_timestamp=5700000000)

import asyncio
import json
import pytest
from datetime import datetime

from app.types import DecodedValidToken
from handlers.session_expiration_checker import SessionExpirationChecker
from storage.storage_updaters import StorageUserSubscriber, StorageWebSocketRegister

pytestmark = [
    pytest.mark.slow,
]


@pytest.fixture(autouse=True)
def mock_broadcast(mocker):
    return mocker.patch("websockets.broadcast")


@pytest.fixture
def give_expiration_checker_enough_time():
    return lambda: asyncio.sleep(0.4)


@pytest.fixture
def expiration_checker(storage):
    return SessionExpirationChecker(storage=storage, check_interval=0.1)


@pytest.fixture(autouse=True)
async def expiration_checker_as_task(expiration_checker):
    stop_signal = asyncio.get_event_loop().create_future()
    runner_task = asyncio.create_task(expiration_checker.run(stop_signal))

    yield runner_task

    stop_signal.set_result(None)


@pytest.fixture(autouse=True)
def ws_subscribed(ws, storage, event):
    token_expiration_timestamp = int(datetime.fromisoformat("2023-01-01 12:23:00Z").timestamp())

    valid_token = DecodedValidToken(sub="user1", exp=token_expiration_timestamp)

    StorageWebSocketRegister(storage, ws, valid_token)()
    StorageUserSubscriber(storage, ws, event)()

    return ws


def test_expiration_checker_monitor_and_manage_access_remove_expired_websockets(expiration_checker, storage, ws_subscribed):
    expiration_checker.monitor_and_manage_access()

    registered_websockets = storage.get_registered_websockets()
    assert registered_websockets == []


async def test_remove_expired_websockets_from_storage(give_expiration_checker_enough_time, storage, mock_broadcast, ws_subscribed, mocker):
    await give_expiration_checker_enough_time()

    registered_websockets = storage.get_registered_websockets()
    assert registered_websockets == []
    assert ws_subscribed.closed is False, "Do not close connection when token expired, just remove from storage"
    mock_broadcast.assert_called_once_with(websockets=[ws_subscribed], message=mocker.ANY)


async def test_expiration_checker_broadcasted_message(give_expiration_checker_enough_time, mock_broadcast):
    await give_expiration_checker_enough_time()

    broadcasted_message_as_json = json.loads(mock_broadcast.call_args.kwargs["message"])
    assert len(broadcasted_message_as_json) == 2
    assert broadcasted_message_as_json["message_type"] == "ErrorResponse"
    assert broadcasted_message_as_json["errors"] == ["Token expired, user subscriptions disabled or removed"]


@pytest.mark.freeze_time("2023-01-01 12:22:55Z", tick=True)  # 5 seconds before expiration
async def test_expiration_checker_not_remove_active_connections(give_expiration_checker_enough_time, storage, ws_subscribed, mock_broadcast):
    await give_expiration_checker_enough_time()

    registered_websockets = storage.get_registered_websockets()
    assert registered_websockets == [ws_subscribed]
    mock_broadcast.assert_not_called()

import asyncio
from datetime import datetime
import json
import pytest

from app.types import DecodedValidToken
from handlers.websockets_access_guardian import WebSocketsAccessGuardian
from storage.storage_updaters import StorageWebSocketRegister
from storage.storage_updaters import StorageUserSubscriber

pytestmark = [
    pytest.mark.slow,
]


@pytest.fixture(autouse=True)
def mock_broadcast(mocker):
    return mocker.patch("websockets.broadcast")


@pytest.fixture
def get_guardian_enough_time_to_do_its_job():
    return lambda: asyncio.sleep(0.4)


@pytest.fixture
def guardian(storage):
    return WebSocketsAccessGuardian(storage=storage, check_interval=0.1)


@pytest.fixture(autouse=True)
async def guardian_as_task(guardian):
    # event_loop = asyncio.get_event_loop()

    stop_signal = asyncio.get_event_loop().create_future()
    runner_task = asyncio.create_task(guardian.run(stop_signal))

    yield runner_task

    stop_signal.set_result(None)


@pytest.fixture(autouse=True)
def ws_subscribed(ws, storage, event):
    token_expiration_timestamp = int(datetime.fromisoformat("2023-01-01 12:23:00Z").timestamp())

    valid_token = DecodedValidToken(sub="user1", exp=token_expiration_timestamp)

    StorageWebSocketRegister(storage, ws, valid_token)()
    StorageUserSubscriber(storage, ws, event)()

    return ws


def test_guardian_monitor_and_manage_access_remove_expired_websockets(guardian, storage, ws_subscribed):
    guardian.monitor_and_manage_access()

    registered_websockets = storage.get_registered_websockets()
    assert registered_websockets == []


async def test_remove_expired_websockets_from_storage(get_guardian_enough_time_to_do_its_job, storage, mock_broadcast, ws_subscribed, mocker):
    await get_guardian_enough_time_to_do_its_job()

    registered_websockets = storage.get_registered_websockets()
    assert registered_websockets == []
    assert ws_subscribed.closed is False, "Do not close connection when token expired, just remove from storage"
    mock_broadcast.assert_called_once_with(websockets=[ws_subscribed], message=mocker.ANY)


async def test_broadcasted_message(get_guardian_enough_time_to_do_its_job, mock_broadcast):
    await get_guardian_enough_time_to_do_its_job()

    broadcasted_message_as_json = json.loads(mock_broadcast.call_args.kwargs["message"])
    assert len(broadcasted_message_as_json) == 2
    assert broadcasted_message_as_json["message_type"] == "ErrorResponse"
    assert broadcasted_message_as_json["errors"] == ["Token expired, user subscriptions disabled or removed"]


@pytest.mark.freeze_time("2023-01-01 12:22:55Z", tick=True)  # 5 seconds before expiration
async def test_do_not_remove_not_expired_connections(get_guardian_enough_time_to_do_its_job, storage, ws_subscribed, mock_broadcast):
    await get_guardian_enough_time_to_do_its_job()

    registered_websockets = storage.get_registered_websockets()
    assert registered_websockets == [ws_subscribed]
    mock_broadcast.assert_not_called()

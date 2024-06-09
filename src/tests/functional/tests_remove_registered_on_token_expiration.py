import asyncio
import pytest

pytestmark = [
    pytest.mark.rabbitmq,
]


@pytest.fixture
def set_storage_connections_expired(storage):
    def set_expired():
        for _, websocket_meta in storage.registered_websockets.items():
            websocket_meta.expiration_timestamp = 1000  # far in the past

    return set_expired


async def test_expired_connections_removed_from_active_connections(ws_client_authenticated, ws_client_recv_decoded, set_storage_connections_expired):
    set_storage_connections_expired()
    await asyncio.sleep(1.1)  # give enough time to validator to do its job

    received = await ws_client_recv_decoded(ws_client_authenticated)

    assert len(received) == 2
    assert received["message_type"] == "ErrorResponse"
    assert received["errors"] == ["Token expired, user subscriptions disabled or removed"]

import json
import pytest

pytestmark = [
    pytest.mark.rabbitmq,
]


@pytest.fixture
def subscribe_message_data():
    return {
        "message_id": 100500,
        "message_type": "Subscribe",
        "params": {"event": "boobs"},
    }


@pytest.fixture
def subscribe_message(subscribe_message_data):
    return json.dumps(subscribe_message_data)


async def test_fail_if_subscribe_without_authentication(ws_client, ws_client_recv_decoded, subscribe_message, subscribe_message_data):
    await ws_client.send(subscribe_message)

    message = await ws_client_recv_decoded(ws_client)

    assert len(message) == 2
    assert message["message_type"] == "ErrorResponse"
    assert len(message["errors"]) > 0


async def test_subscribe_successfully_if_authenticated(ws_client_authenticated, ws_client_recv_decoded, subscribe_message, subscribe_message_data):
    await ws_client_authenticated.send(subscribe_message)

    message = await ws_client_recv_decoded(ws_client_authenticated)

    assert len(message) == 2
    assert message["message_type"] == "SuccessResponse"
    assert message["incoming_message"] == subscribe_message_data

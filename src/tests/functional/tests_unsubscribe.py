import json
import pytest

pytestmark = [
    pytest.mark.rabbitmq,
]


@pytest.fixture
def unsubscribe_message_data():
    return {
        "message_id": 777,
        "message_type": "Unsubscribe",
        "params": {"event": "boobs"},
    }


@pytest.fixture
def unsubscribe_message(unsubscribe_message_data):
    return json.dumps(unsubscribe_message_data)


@pytest.fixture
def subscribe_message():
    return json.dumps(
        {
            "message_id": 100500,
            "message_type": "Subscribe",
            "params": {"event": "boobs"},
        }
    )


@pytest.fixture
async def ws_client_subscribed(ws_client_authenticated, ws_client_send_and_recv, subscribe_message):
    await ws_client_send_and_recv(ws_client_authenticated, subscribe_message)
    return ws_client_authenticated


async def test_fail_if_subscribe_without_authentication(ws_client, ws_client_recv_decoded, unsubscribe_message, unsubscribe_message_data):
    await ws_client.send(unsubscribe_message)

    message = await ws_client_recv_decoded(ws_client)

    assert len(message) == 2
    assert message["message_type"] == "ErrorResponse"
    assert message["errors"] is not None


async def test_unsubscribe_successfully_if_authenticated(ws_client_subscribed, ws_client_recv_decoded, unsubscribe_message, unsubscribe_message_data):
    await ws_client_subscribed.send(unsubscribe_message)

    message = await ws_client_recv_decoded(ws_client_subscribed)

    assert len(message) == 2
    assert message["message_type"] == "SuccessResponse"
    assert message["incoming_message"] == unsubscribe_message_data

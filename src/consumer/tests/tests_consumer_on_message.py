import json
import pytest
from contextlib import nullcontext as does_not_raise

from consumer.tests.conftest import MockedIncomingMessage


@pytest.fixture(autouse=True)
def mock_broadcast(mocker):
    return mocker.patch("websockets.broadcast")


def python_to_bytes(data: dict) -> bytes:
    return json.dumps(data).encode()


@pytest.fixture
def broker_message_data(event):
    return {
        "event": event,
        "size": 3,
        "quantity": 2,
    }


@pytest.fixture
def ya_ws_subscribed(create_ws, ya_valid_token, ws_register_and_subscribe, event):
    return ws_register_and_subscribe(create_ws(), ya_valid_token, event)


@pytest.fixture
def ya_user_ws_subscribed(create_ws, ya_user_valid_token, ws_register_and_subscribe, event):
    return ws_register_and_subscribe(create_ws(), ya_user_valid_token, event)


@pytest.fixture
def consumed_message(broker_message_data):
    return MockedIncomingMessage(body=python_to_bytes(broker_message_data))


@pytest.fixture
def on_message(consumer, consumed_message):
    return lambda message=consumed_message: consumer.on_message(message)


async def test_broadcast_message_to_subscriber_websockets(on_message, ws_subscribed, mock_broadcast, mocker):
    await on_message()

    mock_broadcast.assert_called_once_with(websockets=[ws_subscribed], message=mocker.ANY)


async def test_broadcast_message_to_all_subscribers_websockets(on_message, mock_broadcast, ws_subscribed, ya_ws_subscribed, ya_user_ws_subscribed, mocker):
    await on_message()

    mock_broadcast.assert_called_once()
    broadcasted_websockets = mock_broadcast.call_args.kwargs["websockets"]
    assert len(broadcasted_websockets) == 3
    assert set(broadcasted_websockets) == {ws_subscribed, ya_ws_subscribed, ya_user_ws_subscribed}


async def test_log_and_do_nothing_if_message_not_expected_format(on_message, ws_subscribed, mock_broadcast, consumed_message, caplog):
    consumed_message.body = b"invalid-json"

    with does_not_raise():
        await on_message(consumed_message)

    assert "Consumed message not in expected format" in caplog.text
    mock_broadcast.assert_not_called()

import json
import pytest

import aio_pika

pytestmark = [
    pytest.mark.rabbitmq,
]


@pytest.fixture
def broker_message_data(event):
    return {
        "event": event,
        "size": 3,
        "quantity": 2,
    }


@pytest.fixture
def subscribe_message(event):
    return json.dumps(
        {
            "message_id": 170,
            "message_type": "Subscribe",
            "params": {
                "event": event,
            },
        }
    )


@pytest.fixture
async def exchange(settings):
    connection = await aio_pika.connect_robust(url=str(settings.BROKER_URL))

    async with connection:
        channel = await connection.channel(publisher_confirms=False)
        exchange = await channel.declare_exchange(
            settings.BROKER_EXCHANGE,
            aio_pika.ExchangeType.DIRECT,
        )
        yield exchange


@pytest.fixture
def publish_event(exchange, settings, broker_message_data):
    routing_key = settings.BROKER_ROUTING_KEYS_CONSUME_FROM[0]

    message = aio_pika.Message(
        body=json.dumps(broker_message_data).encode(),
    )

    return exchange.publish(message=message, routing_key=routing_key)


@pytest.fixture
async def ws_client_subscribed(ws_client_authenticated, ws_client_send_and_recv, subscribe_message):
    await ws_client_send_and_recv(ws_client_authenticated, subscribe_message)
    return ws_client_authenticated


async def test_notify_subscribed_ws_consumed_event(ws_client_subscribed, publish_event, ws_client_recv_decoded, event, broker_message_data):
    await publish_event

    message = await ws_client_recv_decoded(ws_client_subscribed)

    assert len(message) == 2
    assert message["message_type"] == "EventNotification"
    assert message["payload"] == broker_message_data

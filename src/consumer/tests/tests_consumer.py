import asyncio
import pytest


@pytest.fixture
def run_consume_task(consumer):
    def run(stop_signal: asyncio.Future):
        return asyncio.create_task(consumer.consume(stop_signal))

    return run


def test_consumer_attributes(consumer):
    assert consumer.broker_url == "amqp://guest:guest@localhost/"
    assert consumer.exchange == "test-exchange"
    assert consumer.queue == "test-queue"
    assert consumer.routing_keys_consume_from == [
        "event-routing-key",
        "ya-event-routing-key",
    ]


async def test_consumer_correctly_stopped_on_stop_signal(run_consume_task):
    stop_signal = asyncio.get_running_loop().create_future()
    consumer_task = run_consume_task(stop_signal)

    stop_signal.set_result(None)

    await asyncio.sleep(0.1)  # get enough time to stop the task
    assert consumer_task.done() is True

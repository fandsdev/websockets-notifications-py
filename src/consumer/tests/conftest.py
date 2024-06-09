import pytest

from consumer.consumer import Consumer
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncGenerator


@pytest.fixture(autouse=True)
def _adjust_settings(settings):
    settings.BROKER_URL = "amqp://guest:guest@localhost/"
    settings.BROKER_EXCHANGE = "test-exchange"
    settings.BROKER_QUEUE = "test-queue"
    settings.BROKER_ROUTING_KEYS_CONSUME_FROM = [
        "event-routing-key",
        "ya-event-routing-key",
    ]


@pytest.fixture
def consumer(storage) -> Consumer:
    return Consumer(storage=storage)


@dataclass
class MockedIncomingMessage:
    """The simplest Incoming message class that represent incoming amqp message.

    The safer choice is to use 'aio_pika.abc.AbstractIncomingMessage,' but the test setup will be significantly more challenging.
    """

    body: bytes

    @asynccontextmanager
    async def process(self) -> AsyncGenerator:
        """Do nothing, just for compatibility with aio_pika.abc.AbstractIncomingMessage."""
        yield None

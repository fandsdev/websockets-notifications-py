import pytest
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from consumer.consumer import Consumer


@pytest.fixture(autouse=True)
def _adjust_settings(settings):
    settings.BROKER_QUEUE = None  # force consumer to create a queue with a random name


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

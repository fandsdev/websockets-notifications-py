import asyncio
import logging
from dataclasses import dataclass
from typing import Protocol

import aio_pika
import websockets
from pydantic import ValidationError

from app import conf
from consumer.dto import ConsumedMessage, OutgoingMessage
from storage.subscription_storage import SubscriptionStorage

logger = logging.getLogger(__name__)


class ConsumerProtocol(Protocol):
    async def consume(self) -> None:
        pass


@dataclass
class Consumer:
    storage: SubscriptionStorage

    def __post_init__(self) -> None:
        settings = conf.get_app_settings()

        self.broker_url: str = str(settings.BROKER_URL)
        self.exchange: str = settings.BROKER_EXCHANGE
        self.queue: str | None = settings.BROKER_QUEUE
        self.routing_keys_consume_from: list[str] = settings.BROKER_ROUTING_KEYS_CONSUME_FROM

    async def consume(self, stop_signal: asyncio.Future) -> None:
        connection = await aio_pika.connect_robust(self.broker_url)

        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(self.exchange, type=aio_pika.ExchangeType.DIRECT)
            queue = await channel.declare_queue(name=self.queue, exclusive=True)

            for routing_key in self.routing_keys_consume_from:
                await queue.bind(exchange=exchange, routing_key=routing_key)

            await queue.consume(self.on_message)

            await stop_signal

    async def on_message(self, raw_message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with raw_message.process():
            processed_messages = self.parse_message(raw_message)

            if processed_messages:
                self.broadcast_subscribers(self.storage, processed_messages)

    @staticmethod
    def parse_message(raw_message: aio_pika.abc.AbstractIncomingMessage) -> ConsumedMessage | None:
        try:
            return ConsumedMessage.model_validate_json(raw_message.body)
        except ValidationError as exc:
            logger.error("Consumed message not in expected format. Errors: %s", exc.errors())  # noqa: TRY400
            return None

    @staticmethod
    def broadcast_subscribers(storage: SubscriptionStorage, message: ConsumedMessage) -> None:
        websockets_to_broadcast = storage.get_event_subscribers_websockets(message.event)

        if websockets_to_broadcast:
            outgoing_message = OutgoingMessage.model_construct(payload=message)
            websockets.broadcast(websockets=websockets_to_broadcast, message=outgoing_message.model_dump_json())

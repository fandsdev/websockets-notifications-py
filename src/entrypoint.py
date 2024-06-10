import asyncio
import logging
import signal

import websockets

from app import conf
from consumer import Consumer
from handlers import WebSocketsAccessGuardian, WebSocketsHandler
from storage.subscription_storage import SubscriptionStorage

logging.basicConfig(level=logging.INFO)


def create_stop_signal() -> asyncio.Future[None]:
    loop = asyncio.get_running_loop()
    stop_signal = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop_signal.set_result, None)
    return stop_signal


async def app_runner(
    settings: conf.Settings,
    websockets_handler: WebSocketsHandler,
    access_guardian: WebSocketsAccessGuardian,
    consumer: Consumer,
    stop_signal: asyncio.Future,
) -> None:
    async with (
        websockets.serve(
            ws_handler=websockets_handler.websockets_handler,
            host=settings.WEBSOCKETS_HOST,
            port=settings.WEBSOCKETS_PORT,
        ),
        asyncio.TaskGroup() as task_group,
    ):
        task_group.create_task(access_guardian.run(stop_signal))
        task_group.create_task(consumer.consume(stop_signal))


async def main() -> None:
    settings = conf.get_app_settings()
    stop_signal = create_stop_signal()

    storage = SubscriptionStorage()
    websockets_handler = WebSocketsHandler(storage=storage)
    access_guardian = WebSocketsAccessGuardian(storage=storage, check_interval=60.0)
    consumer = Consumer(storage=storage)

    await app_runner(
        settings=settings,
        websockets_handler=websockets_handler,
        access_guardian=access_guardian,
        consumer=consumer,
        stop_signal=stop_signal,
    )


if __name__ == "__main__":
    asyncio.run(main())

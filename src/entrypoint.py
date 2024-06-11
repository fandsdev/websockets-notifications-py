import asyncio
import logging
import signal

import websockets

from app import conf
from consumer import Consumer
from handlers import SessionExpirationChecker, WebSocketsHandler
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
    session_expiration_checker: SessionExpirationChecker,
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
        task_group.create_task(session_expiration_checker.run(stop_signal))
        task_group.create_task(consumer.consume(stop_signal))


async def main() -> None:
    settings = conf.get_app_settings()
    stop_signal = create_stop_signal()

    storage = SubscriptionStorage()
    websockets_handler = WebSocketsHandler(storage=storage)
    session_expiration_checker = SessionExpirationChecker(storage=storage, check_interval=60.0)
    consumer = Consumer(storage=storage)

    await app_runner(
        settings=settings,
        websockets_handler=websockets_handler,
        session_expiration_checker=session_expiration_checker,
        consumer=consumer,
        stop_signal=stop_signal,
    )


if __name__ == "__main__":
    asyncio.run(main())

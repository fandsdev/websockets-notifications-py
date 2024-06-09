import asyncio
import signal

import websockets
import logging

from app import conf
from handlers import WebSocketsHandler
from handlers import WebSocketsAccessGuardian
from storage.subscription_storage import SubscriptionStorage

logging.basicConfig(level=logging.INFO)


def create_stop_signal() -> asyncio.Future[None]:
    loop = asyncio.get_running_loop()
    stop_signal = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop_signal.set_result, None)
    return stop_signal


async def app_runner(settings: conf.Settings, websockets_handler: WebSocketsHandler, access_guardian: WebSocketsAccessGuardian) -> None:
    async with websockets.serve(
        ws_handler=websockets_handler.websockets_handler,
        host=settings.WEBSOCKETS_HOST,
        port=settings.WEBSOCKETS_PORT,
    ):
        await access_guardian.run()


async def main() -> None:
    settings = conf.get_app_settings()
    stop_signal = create_stop_signal()

    storage = SubscriptionStorage()
    websockets_handler = WebSocketsHandler(storage=storage)
    access_guardian = WebSocketsAccessGuardian(storage=storage, check_interval=60.0, stop_signal=stop_signal)

    await app_runner(
        settings=settings,
        websockets_handler=websockets_handler,
        access_guardian=access_guardian,
    )


if __name__ == "__main__":
    asyncio.run(main())

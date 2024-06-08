import asyncio
import signal

import websockets

from app import conf
from handlers.websockets_handler import WebSocketsHandler
from storage.subscription_storage import SubscriptionStorage


def create_stop_signal() -> asyncio.Future[None]:
    loop = asyncio.get_running_loop()
    stop_signal = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop_signal.set_result, None)
    return stop_signal


async def app_runner(settings: conf.Settings, websockets_handler: WebSocketsHandler) -> None:
    stop_signal = create_stop_signal()

    async with websockets.serve(
        ws_handler=websockets_handler.websockets_handler,
        host=settings.WEBSOCKETS_HOST,
        port=settings.WEBSOCKETS_PORT,
    ):
        await stop_signal


async def main() -> None:
    settings = conf.get_app_settings()
    storage = SubscriptionStorage()
    websockets_handler = WebSocketsHandler(storage=storage)

    await app_runner(
        settings=settings,
        websockets_handler=websockets_handler,
    )


if __name__ == "__main__":
    asyncio.run(main())

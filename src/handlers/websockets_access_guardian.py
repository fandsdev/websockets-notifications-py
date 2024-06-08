import asyncio
from dataclasses import dataclass, field
import logging

import websockets

from handlers.dto import ErrorResponseMessage
from storage.storage_updaters import StorageWebSocketRemover
from storage.subscription_storage import SubscriptionStorage

logger = logging.getLogger(__name__)


@dataclass
class WebSocketsAccessGuardian:
    storage: SubscriptionStorage
    check_interval: float = 60.0  # in seconds
    stop_signal: asyncio.Future[None] = field(default_factory=asyncio.Future)  # default feature will run forever

    async def run(self) -> None:
        while True:
            await asyncio.sleep(self.check_interval)

            self.monitor_and_manage_access()

    def monitor_and_manage_access(self) -> None:
        expired_websockets = self.storage.get_expired_websockets()

        if expired_websockets:
            logger.warning("Notify and remove from storage for expired websockets: '%s'", (", ").join([str(websocket.id) for websocket in expired_websockets]))

            self.broadcast_authentication_expired(expired_websockets)
            self.remove_expired_websockets(expired_websockets)

        e = self.storage.get_expired_websockets()
        assert e is not None

    def broadcast_authentication_expired(self, expired_websockets: list[websockets.WebSocketServerProtocol]) -> None:
        error_message = ErrorResponseMessage(errors=["Token expired, user subscriptions disabled or removed"], incoming_message=None)
        websockets.broadcast(websockets=expired_websockets, message=error_message.model_dump_json(exclude_none=True))

    def remove_expired_websockets(self, expired_websockets: list[websockets.WebSocketServerProtocol]) -> None:
        for websocket in expired_websockets:
            StorageWebSocketRemover(storage=self.storage, websocket=websocket)()

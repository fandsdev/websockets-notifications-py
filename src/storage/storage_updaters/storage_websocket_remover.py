from dataclasses import dataclass
import logging
from typing import cast

from websockets.server import WebSocketServerProtocol
from functools import cached_property

from app.services import BaseService
from app.types import UserId
from storage.storage_updaters.storage_user_unsubscriber import StorageUserSubscriptionRemover
from storage.subscription_storage import SubscriptionStorage

logger = logging.getLogger(__name__)


@dataclass
class StorageWebSocketRemover(BaseService):
    """ "Remove connection from storage.

    If websocket is not registered then nothing to do.
    If websocket is registered and it's last connection then unsubscribe user from all subscriptions.
    If websocket is registered and other user websocket exists then just remove the websocket from user connections and keep user subscriptions.
    """

    storage: SubscriptionStorage
    websocket: WebSocketServerProtocol

    @cached_property
    def websocket_user_id(self) -> UserId:
        return cast(UserId, self.storage.get_websocket_user_id(self.websocket))

    def act(self) -> None:
        if not self.storage.is_websocket_registered(self.websocket):
            return None

        if self.is_last_user_websocket():
            self.remove_user_subscriptions()
            self.remove_user_connections()
        else:
            self.remove_websocket_from_user_connections()

        self.remove_websocket_from_registered_websockets()

    def is_last_user_websocket(self) -> bool:
        return len(self.storage.user_connections[self.websocket_user_id].websockets) == 1

    def remove_user_subscriptions(self) -> None:
        user_connection_fqis = self.storage.user_connections[self.websocket_user_id].user_subscriptions.copy()

        for subscription_fqi in user_connection_fqis:
            StorageUserSubscriptionRemover(self.storage, self.websocket_user_id, subscription_fqi)()

    def remove_user_connections(self) -> None:
        del self.storage.user_connections[self.websocket_user_id]
        logger.info("The last connection for user removed from storage. User ID: '%s'", self.websocket_user_id)

    def remove_websocket_from_user_connections(self) -> None:
        self.storage.user_connections[self.websocket_user_id].websockets.remove(self.websocket)
        logger.info("Websocket removed form user connections. UserId: `%s`, WebsocketId: `%s`", self.websocket_user_id, str(self.websocket.id))

    def remove_websocket_from_registered_websockets(self) -> None:
        del self.storage.registered_websockets[self.websocket]
        logger.info("Websocket removed from registered websockets. Websocket ID: `%s`", str(self.websocket.id))

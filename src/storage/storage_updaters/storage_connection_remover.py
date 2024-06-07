from dataclasses import dataclass
import logging

from websockets.server import WebSocketServerProtocol

from app.services import BaseService
from app.types import UserId
from storage.storage_updaters.storage_user_unsubscriber import StorageUserSubscriptionRemover
from storage.subscription_storage import SubscriptionStorage

logger = logging.getLogger(__name__)


@dataclass
class StorageConnectionRemover(BaseService):
    """ "Remove connection from storage.

    If websocket is not registered then nothing to do.
    If websocket is registered and it's last connection then unsubscribe user from all subscriptions.
    If websocket is registered and other user websocket exists then just remove the websocket from user connections and keep user subscriptions.
    """

    storage: SubscriptionStorage
    websocket: WebSocketServerProtocol

    def act(self) -> None:
        user_id = self.storage.get_websocket_user_id(self.websocket)

        if not user_id:
            logger.info("Removing not registered connection with id = '%s', nothing to do with storage", str(self.websocket.id))
            return

        if self.is_last_user_websocket(user_id):
            self.remove_user_subscriptions(user_id)
            self.remove_user_connections(user_id)
        else:
            self.remove_websocket_from_user_connections(user_id)

        self.remove_websocket_from_registered_websockets()

    def is_last_user_websocket(self, user_id: UserId) -> bool:
        return len(self.storage.user_connections[user_id].websockets) == 1

    def remove_user_subscriptions(self, user_id: UserId) -> None:
        user_connection_fqis = self.storage.user_connections[user_id].user_subscriptions.copy()

        for subscription_fqi in user_connection_fqis:
            StorageUserSubscriptionRemover(self.storage, user_id, subscription_fqi)()

    def remove_user_connections(self, user_id: UserId) -> None:
        del self.storage.user_connections[user_id]
        logger.info("The last connection for user removed from storage. User ID: '%s'", user_id)

    def remove_websocket_from_user_connections(self, user_id: UserId) -> None:
        self.storage.user_connections[user_id].websockets.remove(self.websocket)
        logger.info("Websocket removed form user connections. UserId: `%s`, WebsocketId: `%s`", user_id, str(self.websocket.id))

    def remove_websocket_from_registered_websockets(self) -> None:
        del self.storage.registered_websockets[self.websocket]
        logger.info("Websocket removed from registered websockets. Websocket ID: `%s`", str(self.websocket.id))

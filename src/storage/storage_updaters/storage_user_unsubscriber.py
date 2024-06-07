from dataclasses import dataclass
from functools import cached_property
import logging

from websockets.server import WebSocketServerProtocol

from app.services import BaseService
from app.types import UserId
from app.types import Event
from storage.exceptions import StorageOperationException
from storage.subscription_storage import SubscriptionStorage

logger = logging.getLogger(__name__)


@dataclass
class StorageUserUnsubscriber(BaseService):
    storage: SubscriptionStorage
    websocket: WebSocketServerProtocol
    event: Event

    @cached_property
    def websocket_user_id(self) -> UserId:
        user_id = self.storage.get_websocket_user_id(self.websocket)

        if not user_id:
            raise StorageOperationException("The user is not registered")

        return user_id

    def act(self) -> None:
        if self.is_user_has_subscription():
            StorageUserSubscriptionRemover(
                self.storage,
                self.websocket_user_id,
                self.event,
            )()

    def is_user_has_subscription(self) -> bool:
        return self.event in self.storage.user_connections[self.websocket_user_id].user_subscriptions


@dataclass
class StorageUserSubscriptionRemover(BaseService):
    storage: SubscriptionStorage
    user_id: UserId
    event: Event

    def act(self) -> None:
        self.remove_storage_subscription()
        self.update_user_subscriptions()

    def remove_storage_subscription(self) -> None:
        event_subscriptions = self.storage.subscriptions[self.event]

        event_subscriptions.discard(self.user_id)
        logger.info("User unsubscribed from event. User: '%s', Event '%s'", self.user_id, self.event)

        if not event_subscriptions:
            del self.storage.subscriptions[self.event]
            logger.info("Event record removed from storage cause has no subscribers. Event: '%s'", self.event)

    def update_user_subscriptions(self) -> None:
        self.storage.user_connections[self.user_id].user_subscriptions.discard(self.event)
        logger.info("Subscription removed from user. User: '%s', event: '%s'", self.user_id, self.event)

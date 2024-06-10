import logging
from dataclasses import dataclass
from functools import cached_property

from websockets.server import WebSocketServerProtocol

from app.services import BaseService
from app.types import Event, UserId
from storage.exceptions import StorageOperationException
from storage.subscription_storage import SubscriptionStorage

logger = logging.getLogger(__name__)


@dataclass
class StorageUserSubscriber(BaseService):
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
        self.validate_websocket_registered()

        self.update_storage_subscriptions()
        self.update_user_subscriptions()

    def validate_websocket_registered(self) -> UserId:
        return self.websocket_user_id  # access to property

    def update_storage_subscriptions(self) -> None:
        event_subscriptions: set[UserId] | None = self.storage.subscriptions.get(self.event)

        if event_subscriptions is None:
            event_subscriptions = set()
            self.storage.subscriptions[self.event] = event_subscriptions
            logger.info("Event record for subscriptions created in storage. Event: '%s'", self.event)

        event_subscriptions.add(self.websocket_user_id)
        logger.info("User added to event subscribers. UserId: '%s', Event: '%s'", self.websocket_user_id, self.event)

    def update_user_subscriptions(self) -> None:
        self.storage.user_connections[self.websocket_user_id].user_subscriptions.add(self.event)
        logger.info("Subscription added to user: '%s', Event: '%s'", self.websocket_user_id, self.event)

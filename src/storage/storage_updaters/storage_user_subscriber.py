from dataclasses import dataclass
from functools import cached_property
import logging

from websockets.server import WebSocketServerProtocol

from app.services import BaseService
from app.types import UserId
from storage.exceptions import StorageOperationException
from storage.subscription_storage import SubscriptionStorage
from storage.types import SubscriptionFullQualifiedIdentifier

logger = logging.getLogger(__name__)


@dataclass
class StorageUserSubscriber(BaseService):
    storage: SubscriptionStorage
    websocket: WebSocketServerProtocol
    subscription_fqi: SubscriptionFullQualifiedIdentifier

    @cached_property
    def websocket_user_id(self) -> UserId:
        user_id = self.storage.get_websocket_user_id(self.websocket)

        if not user_id:
            raise StorageOperationException("The user is not registered")

        return user_id

    def act(self) -> None:
        self.update_storage_subscriptions()
        self.update_user_subscriptions()

    def update_storage_subscriptions(self) -> None:
        event, _, event_subscription_identifier = self.subscription_fqi

        # Create event with events_subscriptions_storage if it's the first subscription for the event
        if event not in self.storage.subscriptions:
            self.storage.subscriptions[event] = {}
            logger.info("Event record for subscriptions created in storage. Event: '%s'", event)

        event_subscriptions = self.storage.subscriptions[event]

        # Create subscription identifier in event subscription storage if it doesn't exist
        if event_subscription_identifier not in event_subscriptions:
            event_subscriptions[event_subscription_identifier] = set()
            logger.info("Subscription identifier created for event. Event: '%s', Identifier '%s'", event, event_subscription_identifier)

        event_subscriptions[event_subscription_identifier].add(self.websocket_user_id)
        logger.info("User added to event subscribers. UserId: '%s', subscription_fqi: '%s'", self.websocket_user_id, self.subscription_fqi)

    def update_user_subscriptions(self) -> None:
        self.storage.user_connections[self.websocket_user_id].user_subscriptions.add(self.subscription_fqi)
        logger.info("Subscription added to user: '%s', subscription_fqi: '%s'", self.websocket_user_id, self.subscription_fqi)

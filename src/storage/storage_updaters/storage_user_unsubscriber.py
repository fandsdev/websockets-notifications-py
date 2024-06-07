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
class StorageUserUnsubscriber(BaseService):
    storage: SubscriptionStorage
    websocket: WebSocketServerProtocol
    subscription_fqi: SubscriptionFullQualifiedIdentifier

    @cached_property
    def websocket_user_id(self) -> UserId:
        user_id = self.storage.get_websocket_user_id(self.websocket)

        if not user_id:
            raise StorageOperationException("The user is not authenticated")

        return user_id


    def act(self) -> None:
        if self.is_user_has_subscription():
            StorageUserSubscriptionRemover(
                self.storage,
                self.websocket_user_id,
                self.subscription_fqi,
            )()

    def is_user_has_subscription(self) -> bool:
        return self.subscription_fqi in self.storage.user_connections[self.websocket_user_id].user_subscriptions


@dataclass
class StorageUserSubscriptionRemover(BaseService):
    storage: SubscriptionStorage
    user_id: UserId
    subscription_fqi: SubscriptionFullQualifiedIdentifier

    def act(self) -> None:
        self.remove_storage_subscription()
        self.update_user_subscriptions()

    def remove_storage_subscription(self) -> None:
        event, _, event_subscription_identifier = self.subscription_fqi

        event_subscriptions = self.storage.subscriptions[event]

        event_subscriptions[event_subscription_identifier].discard(self.user_id)
        logger.info("User unsubscribed from event. User: '%s', subscription_fqi '%s'", self.user_id, self.subscription_fqi)

        if not event_subscriptions[event_subscription_identifier]:
            del event_subscriptions[event_subscription_identifier]
            logger.info("Subscription identifier removed from event in storage. Event: '%s', identifier: '%s'", event, event_subscription_identifier)

        if not self.storage.subscriptions[event]:
            del self.storage.subscriptions[event]
            logger.info("Event from storage removed cause empty. Event: '%s'", event)

    def update_user_subscriptions(self) -> None:
        self.storage.user_connections[self.user_id].user_subscriptions.discard(self.subscription_fqi)
        logger.info("Subscription removed from user. User: '%s', subscription_fqi: '%s'", self.user_id, self.subscription_fqi)

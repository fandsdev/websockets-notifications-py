from dataclasses import dataclass
from typing import NamedTuple

from websockets.server import WebSocketServerProtocol

from app.types import Event
from app.types import UserId


@dataclass
class WebSocketMeta:
    """Data to store with websocket connection to identify it and to be able to close it needed.

    Expiration timestamp should be updated on each authentication message with updated token.
    """

    user_id: UserId
    expiration_timestamp: int


EventSubscriptionKey = tuple[str, ...]  # ordered keys used to subscribe to specific event
EventSubscriptionIdentifier = tuple[int | str, ...]  # values matched to subscription key
EventSubscriptionsBucket = dict[EventSubscriptionIdentifier, set[UserId]]  # bucket of subscriptions for specific event


class SubscriptionFullQualifiedIdentifier(NamedTuple):
    """Necessary and sufficient data to create user subscription in storage."""

    event: Event
    subscription_key: EventSubscriptionKey
    subscription_identifier: EventSubscriptionIdentifier


class ConnectedUserMeta(NamedTuple):
    """Data related to exact user."""

    websockets: list[WebSocketServerProtocol]
    user_subscriptions: set[SubscriptionFullQualifiedIdentifier]

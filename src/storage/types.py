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


class ConnectedUserMeta(NamedTuple):
    """Data related to exact user."""

    websockets: list[WebSocketServerProtocol]
    user_subscriptions: set[Event]

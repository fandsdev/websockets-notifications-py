from dataclasses import dataclass
from dataclasses import field
import time

from websockets import WebSocketServerProtocol

from app.types import Event
from app.types import UserId
from storage.types import ConnectedUserMeta
from storage.types import WebSocketMeta
from storage.types import EventSubscriptionIdentifier
from storage.types import EventSubscriptionsBucket


@dataclass
class SubscriptionStorage:
    registered_websockets: dict[WebSocketServerProtocol, WebSocketMeta] = field(default_factory=dict)
    subscriptions: dict[Event, EventSubscriptionsBucket] = field(default_factory=dict)
    user_connections: dict[UserId, ConnectedUserMeta] = field(default_factory=dict)

    def is_websocket_registered(self, websocket: WebSocketServerProtocol) -> bool:
        return websocket in self.registered_websockets

    def get_registered_websockets(self) -> list[WebSocketServerProtocol]:
        return list(self.registered_websockets.keys())

    def get_websocket_user_id(self, websocket: WebSocketServerProtocol) -> UserId | None:
        websocket_meta = self.registered_websockets.get(websocket)
        return websocket_meta.user_id if websocket_meta else None

    def get_event_subscribers_user_ids(self, event: Event, identifier: EventSubscriptionIdentifier) -> set[UserId]:
        return self.subscriptions.get(event, {}).get(identifier, set())

    def is_event_active(self, event: Event) -> bool:
        return event in self.subscriptions

    def get_users_websockets(self, user_ids: set[UserId]) -> list[WebSocketServerProtocol]:
        users_websockets = []

        for user_id in user_ids:
            user_connection_meta = self.user_connections.get(user_id)

            if user_connection_meta:
                users_websockets.extend(user_connection_meta.websockets)

        return users_websockets

    def get_expired_websockets(self) -> list[WebSocketServerProtocol]:
        now_timestamp = time.time()

        return [websocket for websocket, websocket_meta in self.registered_websockets.items() if websocket_meta.expiration_timestamp <= now_timestamp]

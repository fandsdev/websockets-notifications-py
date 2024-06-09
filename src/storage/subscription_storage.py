from dataclasses import dataclass
from dataclasses import field
import time

from websockets import WebSocketServerProtocol

from app.types import Event
from app.types import UserId
from storage.types import ConnectedUserMeta
from storage.types import WebSocketMeta


@dataclass
class SubscriptionStorage:
    registered_websockets: dict[WebSocketServerProtocol, WebSocketMeta] = field(default_factory=dict)
    subscriptions: dict[Event, set[UserId]] = field(default_factory=dict)
    user_connections: dict[UserId, ConnectedUserMeta] = field(default_factory=dict)

    def is_websocket_registered(self, websocket: WebSocketServerProtocol) -> bool:
        return websocket in self.registered_websockets

    def get_registered_websockets(self) -> list[WebSocketServerProtocol]:
        return list(self.registered_websockets.keys())

    def get_websocket_user_id(self, websocket: WebSocketServerProtocol) -> UserId | None:
        websocket_meta = self.registered_websockets.get(websocket)
        return websocket_meta.user_id if websocket_meta else None

    def get_event_subscribers_websockets(self, event: Event) -> list[WebSocketServerProtocol]:
        subscribers_user_ids = self.subscriptions.get(event) or set()

        user_websockets = []

        for user_id in subscribers_user_ids:
            user_websockets.extend(self.user_connections[user_id].websockets)

        return user_websockets

    def get_expired_websockets(self) -> list[WebSocketServerProtocol]:
        now_timestamp = time.time()

        return [websocket for websocket, websocket_meta in self.registered_websockets.items() if websocket_meta.expiration_timestamp <= now_timestamp]

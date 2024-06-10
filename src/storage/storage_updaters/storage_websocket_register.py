import logging
from dataclasses import dataclass
from functools import cached_property

from websockets.server import WebSocketServerProtocol

from app.services import BaseService
from app.types import DecodedValidToken, UserId
from storage.exceptions import StorageOperationException
from storage.subscription_storage import SubscriptionStorage
from storage.types import ConnectedUserMeta, WebSocketMeta

logger = logging.getLogger(__name__)


@dataclass
class StorageWebSocketRegister(BaseService):
    """Add or update websocket in storage.

    If websocket not registered: just register it.
    If websocket is registered already:
        - if token's 'user_id' is the same then update websocket's expiration timestamp
        - if token's 'user_id' is different then do not change existed registered websocket and raise `StorageOperationException`
    """

    storage: SubscriptionStorage
    websocket: WebSocketServerProtocol
    validated_token: DecodedValidToken

    @cached_property
    def existed_websocket_meta(self) -> WebSocketMeta | None:
        return self.storage.registered_websockets.get(self.websocket)

    @cached_property
    def token_user_id(self) -> UserId:
        return self.validated_token.sub

    @cached_property
    def token_expiration_timestamp(self) -> int:
        return self.validated_token.exp

    def act(self) -> None:
        self.validate_token_user_id()

        if self.existed_websocket_meta:
            self.update_registered_websocket_meta(self.existed_websocket_meta)
            return

        self.register_new_websocket()

    def validate_token_user_id(self) -> None:
        if self.existed_websocket_meta and self.existed_websocket_meta.user_id != self.token_user_id:
            logger.warning("The user with id '%s' provided token of user of id '%s'", self.existed_websocket_meta.user_id, self.token_user_id)
            raise StorageOperationException("The user has different public id")

    def update_registered_websocket_meta(self, websocket_meta: WebSocketMeta) -> None:
        websocket_meta.expiration_timestamp = self.token_expiration_timestamp
        logger.info("The expiration time for ws with id '%s' was updated to '%s'", str(self.websocket.id), self.token_expiration_timestamp)

    def register_new_websocket(self) -> None:
        self.add_new_websocket_to_registered_websockets()
        self.add_new_websocket_to_user_connections()

    def add_new_websocket_to_registered_websockets(self) -> None:
        self.storage.registered_websockets[self.websocket] = WebSocketMeta(
            user_id=self.token_user_id,
            expiration_timestamp=self.token_expiration_timestamp,
        )

    def add_new_websocket_to_user_connections(self) -> None:
        user_connections = self.storage.user_connections.get(self.token_user_id)

        if user_connections:
            user_connections.websockets.append(self.websocket)
            logger.info("The user with id '%s' has new websocket connection", self.token_user_id)
        else:
            self.storage.user_connections[self.token_user_id] = ConnectedUserMeta(websockets=[self.websocket], user_subscriptions=set())
            logger.info("The user with id '%s' registered with first websocket connection", self.token_user_id)

from dataclasses import dataclass
from typing import Coroutine, Any, Callable

from websockets import WebSocketServerProtocol

from a12n.jwk_client import AsyncJWKClient
from a12n.jwk_client import AsyncJWKClientException
from app import conf
from handlers.dto import AuthMessage
from handlers.dto import SubscribeMessage
from handlers.dto import UnsubscribeMessage
from handlers.dto import SuccessResponseMessage
from handlers.exceptions import WebsocketMessageException
from storage.exceptions import StorageOperationException
from storage.storage_updaters import StorageWebSocketRegister
from storage import SubscriptionStorage
from storage.storage_updaters import StorageUserSubscriber
from storage.storage_updaters import StorageUserUnsubscriber
from handlers.dto import IncomingMessage

AsyncMessageHandler = Callable[[WebSocketServerProtocol, Any], Coroutine[Any, Any, SuccessResponseMessage]]


@dataclass
class WebSocketMessagesHandler:
    storage: SubscriptionStorage

    def __post_init__(self) -> None:
        settings = conf.get_app_settings()
        self.jwk_client = AsyncJWKClient(jwks_url=settings.AUTH_JWKS_URL, supported_signing_algorithms=settings.AUTH_SUPPORTED_SIGNING_ALGORITHMS)

        self.message_handlers: dict[str, AsyncMessageHandler] = {
            "Authenticate": self.handle_auth_message,
            "Subscribe": self.handle_subscribe_message,
            "Unsubscribe": self.handle_unsubscribe_message,
        }

    async def handle_message(self, websocket: WebSocketServerProtocol, message: IncomingMessage) -> SuccessResponseMessage:
        return await self.message_handlers[message.message_type](websocket, message)

    async def handle_auth_message(self, websocket: WebSocketServerProtocol, message: AuthMessage) -> SuccessResponseMessage:
        try:
            validated_token = await self.jwk_client.decode(message.params.token.get_secret_value())
            StorageWebSocketRegister(storage=self.storage, websocket=websocket, validated_token=validated_token)()
        except (AsyncJWKClientException, StorageOperationException) as exc:
            raise WebsocketMessageException(str(exc), message)

        return SuccessResponseMessage.model_construct(incoming_message=message)

    async def handle_subscribe_message(self, websocket: WebSocketServerProtocol, message: SubscribeMessage) -> SuccessResponseMessage:
        StorageUserSubscriber(storage=self.storage, websocket=websocket, event=message.params.event)()
        return SuccessResponseMessage.model_construct(incoming_message=message)

    async def handle_unsubscribe_message(self, websocket: WebSocketServerProtocol, message: UnsubscribeMessage) -> SuccessResponseMessage:
        StorageUserUnsubscriber(storage=self.storage, websocket=websocket, event=message.params.event)()
        return SuccessResponseMessage.model_construct(incoming_message=message)

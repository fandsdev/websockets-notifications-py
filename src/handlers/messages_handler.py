from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from jwt.exceptions import InvalidTokenError
from websockets import WebSocketServerProtocol

from a12n import jwt_decode
from handlers.dto import AuthMessage, IncomingMessage, SubscribeMessage, SuccessResponseMessage, UnsubscribeMessage
from handlers.exceptions import WebsocketMessageException
from storage import SubscriptionStorage
from storage.exceptions import StorageOperationException
from storage.storage_updaters import StorageUserSubscriber, StorageUserUnsubscriber, StorageWebSocketRegister

MessageHandler = Callable[[WebSocketServerProtocol, Any], SuccessResponseMessage]


@dataclass
class WebSocketMessagesHandler:
    storage: SubscriptionStorage

    def __post_init__(self) -> None:
        self.message_handlers: dict[str, MessageHandler] = {
            "Authenticate": self.handle_auth_message,
            "Subscribe": self.handle_subscribe_message,
            "Unsubscribe": self.handle_unsubscribe_message,
        }

    def handle_message(self, websocket: WebSocketServerProtocol, message: IncomingMessage) -> SuccessResponseMessage:
        return self.message_handlers[message.message_type](websocket, message)

    def handle_auth_message(self, websocket: WebSocketServerProtocol, message: AuthMessage) -> SuccessResponseMessage:
        try:
            validated_token = jwt_decode.decode(jwt_token=message.params.token.get_secret_value())
            StorageWebSocketRegister(storage=self.storage, websocket=websocket, validated_token=validated_token)()
        except (InvalidTokenError, StorageOperationException) as exc:
            raise WebsocketMessageException(str(exc), message) from exc

        return SuccessResponseMessage.model_construct(incoming_message=message)

    def handle_subscribe_message(self, websocket: WebSocketServerProtocol, message: SubscribeMessage) -> SuccessResponseMessage:
        StorageUserSubscriber(storage=self.storage, websocket=websocket, event=message.params.event)()
        return SuccessResponseMessage.model_construct(incoming_message=message)

    def handle_unsubscribe_message(self, websocket: WebSocketServerProtocol, message: UnsubscribeMessage) -> SuccessResponseMessage:
        StorageUserUnsubscriber(storage=self.storage, websocket=websocket, event=message.params.event)()
        return SuccessResponseMessage.model_construct(incoming_message=message)

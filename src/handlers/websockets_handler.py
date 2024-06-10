import logging
from dataclasses import dataclass
from typing import Annotated

import pydantic
from pydantic import Field, TypeAdapter
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedError

from app import conf
from handlers.dto import AuthMessage, ErrorResponseMessage, IncomingMessage, SuccessResponseMessage
from handlers.exceptions import WebsocketMessageException
from handlers.messages_handler import WebSocketMessagesHandler
from storage.storage_updaters import StorageWebSocketRemover
from storage.subscription_storage import SubscriptionStorage

logger = logging.getLogger(__name__)

IncomingMessageAdapter = TypeAdapter(Annotated[IncomingMessage, Field(discriminator="message_type")])
AuthMessageAdapter = TypeAdapter(Annotated[AuthMessage, Field(discriminator="message_type")])


@dataclass
class WebSocketsHandler:
    storage: SubscriptionStorage

    def __post_init__(self) -> None:
        settings = conf.get_app_settings()
        self.websockets_path = settings.WEBSOCKETS_PATH

        self.messages_handler = WebSocketMessagesHandler(storage=self.storage)

    async def websockets_handler(self, websocket: WebSocketServerProtocol) -> None:
        if websocket.path != self.websockets_path:
            return

        try:
            async for message in websocket:
                response_message = await self.process_message(websocket=websocket, raw_message=message)
                await websocket.send(response_message.model_dump_json(exclude_none=True))
        except ConnectionClosedError:
            logger.warning("Trying to send message to closed connection. Connection id: '%s'", websocket.id)
        finally:
            StorageWebSocketRemover(storage=self.storage, websocket=websocket)()

    async def process_message(self, websocket: WebSocketServerProtocol, raw_message: str | bytes) -> SuccessResponseMessage | ErrorResponseMessage:
        try:
            message = self.parse_raw_message(websocket, raw_message)
        except pydantic.ValidationError as exc:
            return ErrorResponseMessage.model_construct(errors=exc.errors(include_url=False, include_context=False), incoming_message=None)

        try:
            success_response = await self.messages_handler.handle_message(websocket, message)
        except WebsocketMessageException as exc:
            return exc.as_error_message()

        return success_response

    def parse_raw_message(self, websocket: WebSocketServerProtocol, raw_message: str | bytes) -> IncomingMessage:
        adapter = self.get_message_adapter(websocket)
        return adapter.validate_json(raw_message)

    def get_message_adapter(self, websocket: WebSocketServerProtocol) -> TypeAdapter:
        """Only registered websockets can send all messages. Unregistered websockets can only send Auth messages."""
        if self.storage.is_websocket_registered(websocket):
            return IncomingMessageAdapter

        return AuthMessageAdapter

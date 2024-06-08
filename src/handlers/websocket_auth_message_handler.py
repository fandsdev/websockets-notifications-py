from dataclasses import dataclass

from websockets import WebSocketServerProtocol

from a12n.jwk_client import AsyncJWKClient
from a12n.jwk_client import AsyncJWKClientException
from app import conf
from handlers.dto import AuthMessage
from handlers.dto import SuccessResponseMessage
from handlers.exceptions import WebsocketMessageException
from storage.exceptions import StorageOperationException
from storage.storage_updaters import StorageWebSocketRegister
from storage.subscription_storage import SubscriptionStorage


@dataclass
class WebsocketAuthMessageHandler:
    storage: SubscriptionStorage

    def __post_init__(self) -> None:
        settings = conf.get_app_settings()
        self.jwk_client = AsyncJWKClient(jwks_url=settings.AUTH_JWKS_URL, supported_signing_algorithms=settings.AUTH_SUPPORTED_SIGNING_ALGORITHMS)

    async def handle_message(self, websocket: WebSocketServerProtocol, message: AuthMessage) -> SuccessResponseMessage:
        try:
            validated_token = await self.jwk_client.decode(message.params.token)
            StorageWebSocketRegister(storage=self.storage, websocket=websocket, validated_token=validated_token)()
        except (AsyncJWKClientException, StorageOperationException) as exc:
            raise WebsocketMessageException(str(exc), message)

        return SuccessResponseMessage.model_construct(incoming_message=message)

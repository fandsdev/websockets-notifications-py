from typing import Literal

from pydantic import BaseModel, SecretStr
from pydantic_core import ErrorDetails

from app.types import Event

MessageId = int | str


class AuthMessageParams(BaseModel):
    token: SecretStr


class AuthMessage(BaseModel):
    message_id: MessageId
    message_type: Literal["Authenticate"]
    params: AuthMessageParams


class SubscribeParams(BaseModel):
    event: Event


class SubscribeMessage(BaseModel):
    message_id: MessageId
    message_type: Literal["Subscribe"]
    params: SubscribeParams


class UnsubscribeMessage(BaseModel):
    message_id: MessageId
    message_type: Literal["Unsubscribe"]
    params: SubscribeParams


IncomingMessage = AuthMessage | SubscribeMessage | UnsubscribeMessage


class SuccessResponseMessage(BaseModel):
    message_type: Literal["SuccessResponse"] = "SuccessResponse"
    incoming_message: IncomingMessage


class ErrorResponseMessage(BaseModel):
    message_type: Literal["ErrorResponse"] = "ErrorResponse"
    errors: list[ErrorDetails | str]
    incoming_message: IncomingMessage | None  # may be null if incoming message was not valid

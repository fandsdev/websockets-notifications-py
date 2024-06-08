from typing import Literal

from pydantic import Field

from pydantic import BaseModel
from app.types import Event


messageId = int | str


class AuthMessageParams(BaseModel):
    token: str


class AuthMessage(BaseModel):
    message_id: messageId
    message_type: Literal["Authenticate"]
    params: AuthMessageParams = Field(exclude=True)


class SubscribeParams(BaseModel):
    event: Event


class SubscribeMessage(BaseModel):
    message_id: messageId
    message_type: Literal["Subscribe"]
    params: SubscribeParams


class UnsubscribeMessage(BaseModel):
    message_id: messageId
    message_type: Literal["Unsubscribe"]
    params: SubscribeParams


IncomingMessage = AuthMessage | SubscribeMessage | UnsubscribeMessage


class SuccessResponseMessage(BaseModel):
    message_type: Literal["SuccessResponse"] = "SuccessResponse"
    incoming_message: IncomingMessage


class ErrorResponseMessage(BaseModel):
    message_type: Literal["ErrorResponse"] = "ErrorResponse"
    error_detail: str
    incoming_message: IncomingMessage | None  # may be null if incoming message was not valid

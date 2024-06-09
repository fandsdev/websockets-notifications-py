from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Literal
from app.types import Event


class ConsumedMessage(BaseModel):
    model_config = ConfigDict(extra="allow")

    event: Event


class OutgoingMessage(BaseModel):
    message_type: Literal["EventNotification"] = "EventNotification"
    payload: ConsumedMessage

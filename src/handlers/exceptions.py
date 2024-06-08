from handlers.dto import IncomingMessage
from handlers.dto import ErrorResponseMessage


class WebsocketMessageException(Exception):
    """Raise if error occurred during message handling."""

    def __init__(self, error_detail: str, incoming_message: IncomingMessage | None = None) -> None:
        self.error_detail = error_detail
        self.incoming_message = incoming_message

    def as_error_message(self) -> ErrorResponseMessage:
        return ErrorResponseMessage.model_construct(error_detail=self.error_detail, incoming_message=self.incoming_message)

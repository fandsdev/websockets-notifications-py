from handlers.dto import ErrorResponseMessage, IncomingMessage


class WebsocketMessageException(Exception):
    """Raise if error occurred during message handling."""

    def __init__(self, error_detail: str, incoming_message: IncomingMessage) -> None:
        self.errors = [error_detail]
        self.incoming_message = incoming_message

    def as_error_message(self) -> ErrorResponseMessage:
        return ErrorResponseMessage.model_construct(errors=self.errors, incoming_message=self.incoming_message)

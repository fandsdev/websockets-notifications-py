import pytest
from handlers.messages_handler import WebSocketMessagesHandler
from storage.storage_updaters import StorageUserSubscriber


@pytest.fixture
def subscribe_handler(message_handler: WebSocketMessagesHandler, ws_registered):
    return lambda subscribe_message: message_handler.handle_subscribe_message(ws_registered, subscribe_message)


async def test_subscribe_handler_return_success_response(subscribe_handler, subscribe_message):
    subscribe_response = await subscribe_handler(subscribe_message)

    assert subscribe_response.message_type == "SuccessResponse"
    assert subscribe_response.incoming_message == subscribe_message


async def test_subscribe_handler_call_storage_subscriber_under_the_hood(subscribe_handler, subscribe_message, mocker, storage, ws_registered):
    spy_storage_subscriber = mocker.spy(StorageUserSubscriber, "__call__")

    await subscribe_handler(subscribe_message)

    spy_storage_subscriber.assert_called_once()
    called_service = spy_storage_subscriber.call_args.args[0]
    assert called_service.storage == storage
    assert called_service.websocket == ws_registered
    assert called_service.event == subscribe_message.params.event

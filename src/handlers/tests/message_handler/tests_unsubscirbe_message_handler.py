import pytest
from handlers.message_handler import WebSocketMessageHandler
from storage.storage_updaters import StorageUserUnsubscriber


@pytest.fixture
def unsubscribe_handler(message_handler: WebSocketMessageHandler, ws_subscribed):
    return lambda unsubscribe_message: message_handler.handle_unsubscribe_message(ws_subscribed, unsubscribe_message)


async def test_unsubscribe_handler_return_success_response(unsubscribe_handler, unsubscribe_message):
    unsubscribe_response = await unsubscribe_handler(unsubscribe_message)

    assert unsubscribe_response.message_type == "SuccessResponse"
    assert unsubscribe_response.incoming_message == unsubscribe_message


async def test_unsubscribe_handler_call_storage_unsubscriber_under_the_hood(unsubscribe_handler, unsubscribe_message, mocker, storage, ws_subscribed):
    spy_storage_unsubscriber = mocker.spy(StorageUserUnsubscriber, "__call__")

    await unsubscribe_handler(unsubscribe_message)

    spy_storage_unsubscriber.assert_called_once()
    called_service = spy_storage_unsubscriber.call_args.args[0]
    assert called_service.storage == storage
    assert called_service.websocket == ws_subscribed
    assert called_service.event == unsubscribe_message.params.event

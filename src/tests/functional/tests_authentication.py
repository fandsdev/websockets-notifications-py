import pytest

pytestmark = [
    pytest.mark.rabbitmq,
    pytest.mark.usefixtures("force_token_validation"),
]


async def test_zero_connected_clients_on_server_start(storage):
    assert len(storage.registered_websockets) == 0


async def test_return_error_if_first_message_not_auth(ws_client, ws_client_recv_decoded):
    await ws_client.send("#!?")

    received = await ws_client_recv_decoded(ws_client)

    assert len(received) == 2
    assert received["message_type"] == "ErrorResponse"
    assert len(received["errors"]) > 0


async def test_return_success_on_authenticate(storage, ws_client, auth_message, ws_client_recv_decoded, auth_message_data):
    await ws_client.send(auth_message)

    received = await ws_client_recv_decoded(ws_client)

    assert len(received) == 2
    assert received["message_type"] == "SuccessResponse"
    assert received["incoming_message"] == {
        "message_id": auth_message_data["message_id"],
        "message_type": auth_message_data["message_type"],
        "params": {"token": "**********"},
    }
    assert len(storage.registered_websockets) == 1


async def test_decrease_count_of_registered_on_closing_connections(storage, ws_client, ws_client_close, auth_message, ws_client_recv_decoded):
    await ws_client.send(auth_message)
    await ws_client_recv_decoded(ws_client)  # it's not necessary but it's represent actual behavior and faster to test

    await ws_client_close(ws_client)

    assert len(storage.registered_websockets) == 0


async def test_could_authorize_on_the_second_try(storage, ws_client, auth_message, ws_client_recv_decoded):
    await ws_client.send("#!?")
    await ws_client_recv_decoded(ws_client)
    await ws_client.send(auth_message)

    received = await ws_client_recv_decoded(ws_client)

    assert len(received) == 2
    assert received["message_type"] == "SuccessResponse"
    assert received["incoming_message"]["message_type"] == "Authenticate"
    assert len(storage.registered_websockets) == 1

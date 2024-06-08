import asyncio
import json
import pytest

from websockets import client

from entrypoint import app_runner
from handlers.websockets_handler import WebSocketsHandler


@pytest.fixture(autouse=True)
def _adjust_settings(settings, unused_tcp_port):
    settings.WEBSOCKETS_HOST = "0.0.0.0"
    settings.WEBSOCKETS_PORT = unused_tcp_port


@pytest.fixture
def websockets_handler(storage):
    return WebSocketsHandler(storage=storage)


@pytest.fixture(autouse=True)
async def serve_app_runner(settings, websockets_handler):
    serve_task = asyncio.get_running_loop().create_task(
        app_runner(
            settings=settings,
            websockets_handler=websockets_handler,
        ),
    )

    await asyncio.sleep(0.1)  # give enough time to start the server
    assert serve_task.done() is False  # be sure server is running
    return serve_task


@pytest.fixture
async def ws_client(settings):
    async with client.connect(f"ws://localhost:{settings.WEBSOCKETS_PORT}{settings.WEBSOCKETS_PATH}") as ws_client:
        yield ws_client


@pytest.fixture
def ws_client_close():
    async def close(ws_client):
        await ws_client.close()
        await asyncio.sleep(0.1)

    return close


@pytest.fixture
def ws_client_recv_decoded():
    async def recv_and_decode(ws_client):
        async with asyncio.timeout(delay=0.2):
            message = await ws_client.recv()

        return json.loads(message)

    return recv_and_decode


@pytest.fixture
def ws_client_send_and_recv():
    async def send_and_recv(ws_client, message: str):
        async with asyncio.timeout(delay=0.2):
            await ws_client.send(message)
            await ws_client.recv()
        return ws_client

    return send_and_recv


@pytest.fixture
def auth_message_data():
    return {
        "message_id": 777,
        "message_type": "Authenticate",
        "params": {
            "token": "valid-token",
        },
    }


@pytest.fixture
def auth_message(auth_message_data):
    return json.dumps(auth_message_data)


@pytest.fixture
async def client_ws_authenticated(auth_message, ws_client_send_and_recv, ws_client, force_token_validation):
    return await ws_client_send_and_recv(ws_client, auth_message)

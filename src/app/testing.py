import asyncio
import json
from uuid import uuid4

import websockets
from websockets.frames import CloseCode
from websockets.protocol import State


class MockedWebSocketServerProtocol(websockets.WebSocketServerProtocol):
    """Websocket Server connection implementation for testing purpose.

    To send and receive messages on the client, use the 'client_send' and 'client_recv' methods.
    These methods store messages in appropriate queues but do not actually send them to the client
    """

    def __init__(self) -> None:
        self.id = uuid4()

        self.send_queue: asyncio.Queue[str] = asyncio.Queue(0)
        self.recv_queue: asyncio.Queue[str] = asyncio.Queue(0)

        # Used by websockets to track connection state
        self.state = State.OPEN

    async def recv(self) -> str | bytes:
        if self.state == State.CLOSED:
            raise websockets.ConnectionClosedOK(rcvd=None, sent=None)

        return await self.recv_queue.get()

    async def send(self, message: str) -> None:  # type: ignore[override]
        await asyncio.sleep(0)
        await self.send_queue.put(message)

    async def close(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = "") -> None:  # noqa: ARG002
        self.state = State.CLOSED

    async def wait_messages_to_be_sent(self) -> None:
        await asyncio.sleep(0.1)  # to get enough time to receive messages in coroutines tasks

    async def count_sent_to_client(self) -> int:
        await self.wait_messages_to_be_sent()
        return self.send_queue.qsize()

    def client_send(self, message: dict) -> None:
        self.recv_queue.put_nowait(json.dumps(message))

    async def client_recv(self, skip_count_first_messages: int = 0) -> dict | None:
            """Skip 'skip_count_first_messages' messages and return the next one. Convenient for testing."""
            await self.wait_messages_to_be_sent()

            if self.send_queue.empty():
                return None

            while skip_count_first_messages:
                self.send_queue.get_nowait()
                skip_count_first_messages -= 1

            return json.loads(self.send_queue.get_nowait())

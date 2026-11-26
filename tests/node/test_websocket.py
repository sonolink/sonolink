"""Apache License 2.0

Copyright (c) 2026-present SonoLink Development Team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from unittest.mock import AsyncMock

import pytest

from sonolink.gateway.node import Node
from sonolink.network.message import Message, MessageType


class FakeWS:
    """Minimal websocket stand-in that replays a fixed list of messages."""

    def __init__(self, messages: list[Message]) -> None:
        self._messages = messages
        self._drained = asyncio.Event()

    async def receive(self) -> Message:
        if self._messages:
            return self._messages.pop(0)
        await self._drained.wait()
        raise asyncio.CancelledError  # pragma: no cover


class TestKeepAliveReader:
    async def test_malformed_payload_does_not_kill_reader(
        self,
        node: Node,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Bad frames get dropped with a warning; the reader keeps consuming."""
        node._ws = FakeWS(
            [
                Message(b"{not valid json", MessageType.TEXT),
                Message(b"[]", MessageType.TEXT),  # valid JSON, not an object
                Message(b'{"op": "stats", "players": []}', MessageType.TEXT),
            ]
        )

        processed = asyncio.Event()
        seen: dict[str, Any] = {}

        async def spy(event_type: str | None, data: dict[str, Any]) -> None:
            seen["event_type"] = event_type
            seen["data"] = data
            processed.set()

        node._ws_client._dispatch_event = spy  # type: ignore[method-assign]

        task = asyncio.create_task(node._ws_client.keep_alive_coro())
        with caplog.at_level(
            logging.WARNING, logger="sonolink.gateway.node._websocket"
        ):
            await asyncio.wait_for(processed.wait(), timeout=5)

        try:
            # both bad frames were dropped, the good one still went through
            assert seen["event_type"] == "stats"
            assert seen["data"] == {"players": []}
            assert not task.done(), "reader task died on a malformed payload"
            dropped = [r for r in caplog.records if "malformed payload" in r.message]
            assert len(dropped) == 2
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task

    async def test_receive_error_triggers_reconnect_flow(self, node: Node) -> None:
        ws = FakeWS([])

        async def raise_connection_error() -> Message:
            raise ConnectionError("boom")

        ws.receive = raise_connection_error  # type: ignore[assignment]
        node._ws = ws
        node._ws_client._handle_disconnect = AsyncMock()  # type: ignore[method-assign]

        await asyncio.wait_for(node._ws_client.keep_alive_coro(), timeout=5)

        node._ws_client._handle_disconnect.assert_awaited_once()  # type: ignore[attr-defined]

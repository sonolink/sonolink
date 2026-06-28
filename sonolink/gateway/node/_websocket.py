"""MIT License

Copyright (c) 2026-present SonoLink Development Team.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, Coroutine, cast

import msgspec

from sonolink.gateway.enums import NodeStatus
from sonolink.network.message import MessageType

from ._base import NodeComponent

if TYPE_CHECKING:
    from sonolink.gateway.node import Node


__all__ = ("WebsocketClient",)

_log = logging.getLogger(__name__)

type EventHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, None] | None]


class WebsocketClient(NodeComponent):
    """Internal component responsible for managing websocket connections."""

    def __init__(self, node: Node) -> None:
        super().__init__(node)
        self._event_handlers: dict[str, EventHandler] = {
            "ready": node._events.handle_ready,
            "playerUpdate": node._events.handle_player_update,
            "stats": node._events.handle_stats,
            "event": node._events.handle_event,
        }

    def build_headers(self) -> dict[str, str]:
        assert self.node._client is not None

        headers = self.node._client._build_ws_headers()
        if self.node._resume_session:
            headers["Session-Id"] = self.node._resume_session

        return headers

    async def connect_ws(self, headers: dict[str, str]) -> None:
        self.node._ws = await self.node._manager.connect_ws(
            "/v4/websocket", headers=headers
        )
        self.node._keep_alive = asyncio.create_task(self.keep_alive_coro())

    async def keep_alive_coro(self) -> None:
        if self.node._ws is None or self.node._client is None:
            return

        while True:
            try:
                msg = await self.node._ws.receive()
            except (ConnectionError, RuntimeError) as exc:
                _log.warning("%r lost connection unexpectedly: %s", self.node, exc)
                await self._handle_disconnect()
                break

            if MessageType.CLOSE in msg.flags:
                await self._handle_disconnect()
                break

            if msg.data is None:
                _log.debug("Received a None message from the websocket. Ignoring.")
                continue

            data = cast(dict[str, Any], msgspec.json.decode(msg.data))
            event_type = data.pop("op", None)
            _log.debug("Received event OP=%s ; D=%r", event_type, data)

            try:
                await self._dispatch_event(event_type, data)
            except Exception as exc:
                _log.error(
                    "Node %r: Unhandled exception while processing OP=%s: %s",
                    self.node._id,
                    event_type,
                    exc,
                    exc_info=True,
                )

    async def _dispatch_event(self, event_type: str, data: dict[str, Any]) -> None:
        handler = self._event_handlers.get(event_type)

        if handler is None:
            _log.debug(
                "Received unhandled event type %r from Node %r", event_type, self.node
            )
            return

        result = handler(data)
        if asyncio.iscoroutine(result):
            await result

    async def _handle_disconnect(self) -> None:
        if self.node._is_reconnecting:
            _log.debug("%r already reconnecting; ignoring disconnect event.", self.node)
            return

        if (
            self.node.auto_reconnect
            and self.node._status is not NodeStatus.DISCONNECTED
        ):
            _log.info("%r WS closed, attempting reconnect...", self.node)
            await self.node.reconnect()
        elif self.node.is_connected or self.node._status is NodeStatus.CONNECTING:
            await self.node.close()

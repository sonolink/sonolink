"""
MIT License

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
import itertools
import logging

from sonolink.gateway.enums import NodeStatus
from sonolink.gateway.errors import InvalidNodePassword, NodeError, NodeURINotFound
from sonolink.network.errors import WebSocketError

from ._base import NodeComponent

__all__ = ("ConnectionManager",)

_log = logging.getLogger(__name__)


class ConnectionManager(NodeComponent):
    """Internal component responsible for managing node connections."""

    async def connect(self) -> None:
        if self.node._client is None:
            raise RuntimeError("Cannot connect a node that is not bound to a client.")

        if self.node._keep_alive is not None:
            _log.warning(
                "Node %r: connect() called while already connected; ignoring.",
                self.node,
            )
            return

        await self.node._manager.setup()
        self.node._status = NodeStatus.CONNECTING

        try:
            await self.attempt_connect()
        except NodeError:
            self.node._status = NodeStatus.DISCONNECTED
            raise

    async def close(self) -> None:
        if self.node._client is None:
            raise RuntimeError("Cannot close a Node that is not bound to a client.")

        if self.node._status is NodeStatus.DISCONNECTED:
            raise RuntimeError("This Node is not connected yet.")

        if (
            self.node._keep_alive
            and self.node._keep_alive is not asyncio.current_task()
            and not self.node._keep_alive.cancelled()
        ):
            self.node._keep_alive.cancel()

        if self.node._ws and self.node._ws.is_connected:
            await self.node._ws.close()

        if not self.node._manager.is_closed:
            await self.node._manager.close()

        self.node._ws = None
        self.node._keep_alive = None
        self.node._resume_session = None
        self.node._status = NodeStatus.DISCONNECTED
        self.node._ready_event.clear()

        await self.node.cleanup()
        self.node._client._dispatch("node_close", self.node)

    async def reconnect(self) -> None:
        if self.node._client is None:
            raise RuntimeError("Cannot reconnect a Node that is not bound to a client.")

        if self.node._is_reconnecting:
            raise RuntimeError("This node is already reconnecting.")

        self.node._resume_session = None
        self.node._ws = None
        self.node._status = NodeStatus.CONNECTING
        self.node._ready_event.clear()
        self.node._is_reconnecting = True

        try:
            await self.attempt_connect()
        except NodeError:
            self.node._status = NodeStatus.DISCONNECTED
            self.node._is_reconnecting = False
            raise

    async def attempt_connect(self) -> None:
        if self.node._client is None:
            return

        base_delay = 0.5
        max_delay = 10.0

        headers = self.node._ws_client.build_headers()
        retries = self.node.retries
        counter = range(retries) if retries is not None else itertools.count()

        for attempt in counter:
            _log.info(
                "Starting connection attempt %d/%s on Node %r",
                attempt + 1,
                "inf" if retries is None else retries,
                self.node,
            )

            try:
                await self.node._ws_client.connect_ws(headers)
            except WebSocketError as exc:
                await self.handle_connection_error(exc)
            else:
                _log.info(
                    "Successfully connected node %r (attempt %d/%s)",
                    self.node,
                    attempt + 1,
                    "inf" if retries is None else retries,
                )
                self.node._is_reconnecting = False
                return

            delay = min(base_delay * (2**attempt), max_delay)
            _log.debug("Retrying %r in %.2f seconds...", self.node, delay)
            await asyncio.sleep(delay)

        _log.warning(
            "%r exhausted %s connection attempts. Node will remain disconnected.",
            self.node,
            retries,
        )
        self.node._status = NodeStatus.DISCONNECTED

        if self.node._is_reconnecting:
            self.node._is_reconnecting = False
            _log.info("%r finished reconnecting attempts. Node closed.", self.node)
            self.node._client._dispatch("node_close", self.node)

        await self.node.cleanup()

    async def handle_connection_error(self, exc: WebSocketError) -> None:
        if exc.status in (3000, 3003, 401):
            await self.node.cleanup()
            raise InvalidNodePassword(self.node) from exc

        if exc.status in (1014, 404):
            await self.node.cleanup()
            raise NodeURINotFound(self.node) from exc

        _log.warning(
            "Unexpected error while connecting %r to Lavalink: %s", self.node, exc
        )

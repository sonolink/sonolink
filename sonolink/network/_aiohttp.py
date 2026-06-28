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

from collections.abc import Mapping
from typing import Any

import aiohttp

from ..rest.errors import HTTPException
from .base import BaseHTTPManager, BaseWebsocketManager
from .errors import WebSocketError
from .message import Message, MessageType


class AioHTTPManager(BaseHTTPManager[aiohttp.ClientSession]):
    """Aiohttp implementation of the HTTP Manager."""

    def __init__(self, *, session: aiohttp.ClientSession | None = None) -> None:
        self._session: aiohttp.ClientSession | None = session

    async def setup(self) -> None:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> bytes | None:
        if self._session is None:
            await self.setup()

        assert self._session is not None

        async with self._session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            data=data,
        ) as response:
            if response.status == 204:
                return None

            body = await response.read()

            if response.status >= 400:
                raise HTTPException(body)

            return body

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    @property
    def is_closed(self) -> bool:
        return self._session is None or self._session.closed


class AioWebsocketManager(
    BaseWebsocketManager[
        aiohttp.ClientSession,
        aiohttp.ClientWebSocketResponse,
    ]
):
    """Aiohttp implementation of the Websocket Manager."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._ws: aiohttp.ClientWebSocketResponse | None = None

    async def connect(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        try:
            self._ws = await self._session.ws_connect(url=url, headers=headers)
        except aiohttp.WSServerHandshakeError as e:
            raise WebSocketError(e) from e

    async def receive(self) -> Message:
        if self._ws is None:
            raise RuntimeError("Websocket is not connected.")

        ws: aiohttp.ClientWebSocketResponse = self._ws

        if ws.closed:
            self._ws = None
            raise RuntimeError("Websocket is closed.")

        msg = await ws.receive()

        if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
            self._ws = None
            raise ConnectionError("Websocket connection was closed.")

        if msg.type == aiohttp.WSMsgType.ERROR:
            raise RuntimeError(f"Websocket received error: {ws.exception()}")

        return Message(msg.data, MessageType(msg.type.value))

    async def close(self) -> None:
        if self._ws and not self._ws.closed:
            await self._ws.close()

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and not self._ws.closed

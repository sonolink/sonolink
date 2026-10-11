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

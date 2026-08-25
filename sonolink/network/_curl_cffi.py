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
from typing import TYPE_CHECKING, Any, cast

from curl_cffi import CurlError
from curl_cffi.requests import (
    AsyncSession,
    AsyncWebSocket,
    Response,
    WebSocketClosed,
    WebSocketError,
)

from ..rest.errors import HTTPException
from .base import BaseHTTPManager, BaseWebsocketManager
from .errors import WebSocketError as InnerWSError
from .message import Message, MessageType

if TYPE_CHECKING:
    from curl_cffi.requests import HeaderTypes
    from curl_cffi.requests.session import HttpMethod


class CurlHTTPManager(BaseHTTPManager[AsyncSession[Response]]):
    """Curl-CCFI implementation of the HTTP Manager."""

    def __init__(self, *, session: AsyncSession[Response] | None = None) -> None:
        self._session: AsyncSession[Response] | None = session

    async def setup(self) -> None:
        if self._session is None:
            self._session = AsyncSession()

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
        
        response = await self._session.request(
            method=cast("HttpMethod", method.upper()),
            url=url,
            headers=cast("HeaderTypes", headers),
            params=dict(params) if params else None,
            json=json,
            data=data,
        )

        if response.status_code == 204:
            return None

        if response.status_code >= 400:
            raise HTTPException(response.content)

        return response.content

    async def close(self) -> None:
        if not self._session:
            return None

        await self._session.close()
        self._session = None

    @property
    def is_closed(self) -> bool:
        return self._session is None


class CurlWebsocketManager(
    BaseWebsocketManager[
        AsyncSession[Response],
        AsyncWebSocket,
    ]
):
    """Curl-cffi implementation of the Websocket Manager."""

    def __init__(self, session: AsyncSession[Response]) -> None:
        self._session = session
        self._ws: AsyncWebSocket | None = None

    async def connect(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        try:
            self._ws = await self._session.ws_connect(
                url=url,
                headers=headers,
            )
        except (CurlError, WebSocketError) as exc:
            raise InnerWSError(exc) from exc

    async def receive(self) -> Message:
        if self._ws is None:
            raise RuntimeError("Websocket is not connected.")

        ws: AsyncWebSocket = self._ws

        try:
            payload, flags = await ws.recv()
        except (CurlError, WebSocketClosed):
            self._ws = None
            raise ConnectionResetError("Websocket connection was closed.")

        if not payload:
            self._ws = None
            raise ConnectionResetError(
                "Websocket received an empty payload/close frame."
            )

        return Message(payload, MessageType(flags))

    async def close(self) -> None:
        if self._ws is None:
            return None

        await self._ws.close()
        self._ws = None

    @property
    def is_connected(self) -> bool:
        return self._ws is not None

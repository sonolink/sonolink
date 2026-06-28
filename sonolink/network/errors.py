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

from typing import TYPE_CHECKING

from sonolink.errors import SonoLinkException

if TYPE_CHECKING:
    import aiohttp
    import curl_cffi

    WSErrorType = (
        aiohttp.WebSocketError
        | aiohttp.WSServerHandshakeError
        | curl_cffi.requests.WebSocketError
        | curl_cffi.CurlError
    )


class NetworkError(SonoLinkException):
    """Base exception for all network-related errors."""


class WebSocketError(NetworkError):
    """Exception raised when a websocket error occurs."""

    def __init__(self, original: WSErrorType) -> None:
        self._original: WSErrorType = original

    @property
    def code(self) -> int:
        """The code of the websocket error."""
        return self._original.code

    @property
    def status(self) -> int:
        """The status code of the websocket."""
        return getattr(self._original, "status", self.code)

    @property
    def message(self) -> str | None:
        """The message of the websocket error."""
        return getattr(self._original, "message", None)

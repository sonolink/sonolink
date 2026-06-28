"""MIT License.

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

import datetime
from typing import Any

import msgspec

from sonolink.errors import SonoLinkException
from sonolink.utils import cached_property

__all__ = (
    "ErrorResponseType",
    "HTTPException",
)


class ErrorResponseType(msgspec.Struct, kw_only=True):
    """Represents the error response on a HTTP request."""

    timestamp: int
    status: int
    error: str
    path: str
    message: str | None = None
    trace: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dict(self.__dict__)

    def __str__(self) -> str:
        return (
            f"{self.status} while requesting {self.path}: {self.message or self.error}"
        )


class HTTPException(SonoLinkException):
    """An error response received by a HTTP request."""

    __slots__ = (
        "_cs_timestamp",
        "_underlying",
    )

    _underlying: ErrorResponseType

    def __init__(self, data: bytes) -> None:
        self._underlying = msgspec.json.decode(data, type=ErrorResponseType)
        super().__init__(str(self._underlying))

    @cached_property("_cs_timestamp")
    def timestamp(self) -> datetime.datetime:
        """Return the timestamp on which this exception was created."""
        return datetime.datetime.fromtimestamp(
            self._underlying.timestamp, tz=datetime.timezone.utc
        )

    @property
    def status(self) -> int:
        """The status code of the request."""
        return self._underlying.status

    @property
    def error(self) -> str:
        """The status' code message."""
        return self._underlying.error

    @property
    def trace(self) -> str | None:
        """The stack trace of the error."""
        return self._underlying.trace

    @property
    def message(self) -> str | None:
        """The error message."""
        return self._underlying.message

    @property
    def path(self) -> str:
        """The path that caused the error."""
        return self._underlying.path

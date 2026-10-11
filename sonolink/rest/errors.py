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
    """Represents the error response on an HTTP request."""

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
    """An error response received by an HTTP request."""

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
            self._underlying.timestamp / 1000,
            tz=datetime.timezone.utc,
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

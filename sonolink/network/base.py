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

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Generic, TypeVar

from .message import Message

SessionT = TypeVar("SessionT")
WebsocketT = TypeVar("WebsocketT")


class BaseHTTPManager(ABC, Generic[SessionT]):
    """Abstract Base Class for SonoLink HTTP backends."""

    _session: SessionT | None

    def __init__(self, *, session: SessionT | None = None) -> None: ...

    @abstractmethod
    async def setup(self) -> None:
        """Initialize the underlying session (ClientSession or AsyncSession)."""
        ...

    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> Any:
        """Perform an async HTTP request and return the response body/JSON."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the session and cleanup connectors."""
        ...

    @property
    @abstractmethod
    def is_closed(self) -> bool:
        """Check if the underlying session is closed."""
        ...


class BaseWebsocketManager(ABC, Generic[SessionT, WebsocketT]):
    """Abstract Base Class for SonoLink Websocket backends."""

    _session: SessionT
    _ws: WebsocketT | None

    def __init__(self, session: SessionT) -> None: ...

    @abstractmethod
    async def connect(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """Establish a connection to the Lavalink Websocket server."""
        ...

    @abstractmethod
    async def receive(self) -> Message:
        """Wait for a message from the websocket and return the parsed JSON data."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close the websocket connection and perform cleanup."""
        ...

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the websocket is currently connected and active."""
        ...

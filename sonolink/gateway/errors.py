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

from typing import TYPE_CHECKING

from sonolink.errors import SonoLinkException

if TYPE_CHECKING:
    from .node import Node
    from .player import FrameworkLiteral

__all__ = (
    "AutoPlaySeedMissing",
    "FrameworkClientMismatch",
    "FrameworkImportError",
    "HistoryEmpty",
    "InvalidNodePassword",
    "NodeError",
    "NodeURINotFound",
    "QueueEmpty",
)


class NodeError(SonoLinkException):
    """Base class for all Node-related errors."""


class AutoPlaySeedMissing(SonoLinkException):
    """Exception raised when AutoPlay cannot find a valid track to use as a discovery seed.

    .. versionadded:: 1.1.0
    """


class FrameworkClientMismatch(SonoLinkException):
    """Exception raised when trying to initialize a Sonolink Client with a
    client that does not match the detected framework. This likely means the
    client is from a different framework or the framework detection is incorrect.

    .. versionadded:: 1.1.0
    """

    expected_type: type
    """The expected framework type."""
    received_type: type
    """The actual framework type."""
    framework: FrameworkLiteral
    """The detected framework."""

    def __init__(
        self, *, expected_type: type, received_type: type, framework: FrameworkLiteral
    ) -> None:
        self.expected_type = expected_type
        self.received_type = received_type
        self.framework = framework
        msg = (
            f"Expected client of type {self.expected_type!r} for detected framework '{framework}', "
            f"but got {self.received_type!r}. Either the client is from a different framework or the framework detection is incorrect."
        )
        super().__init__(msg)


class FrameworkImportError(SonoLinkException):
    """Exception raised when trying to initialize a Sonolink Client with a framework's
    client, but the framework cannot be imported. This likely means the framework
    is not installed, there is an issue with the installation or the framework detection is incorrect.

    .. versionadded:: 1.1.0
    """

    framework: FrameworkLiteral
    """The detected framework."""

    def __init__(self, *, framework: FrameworkLiteral) -> None:
        self.framework = framework

        msg = f"Could not import detected framework '{framework}'. Make sure the framework is installed and up to date."
        super().__init__(msg)


class HistoryEmpty(SonoLinkException):
    """Exception raised when trying to get a track from an empty history."""


class InvalidNodePassword(NodeError):
    """Exception raised when a Node attempts to connect with an invalid password."""

    node: Node
    """The node that failed connecting."""

    def __init__(self, node: Node) -> None:
        self.node = node


class NodeURINotFound(NodeError):
    """Exception raised when a Node's uri is not found when connecting."""

    node: Node
    """The Node which URI is not found."""

    def __init__(self, node: Node) -> None:
        self.node = node


class QueueEmpty(SonoLinkException):
    """Exception raised when trying to get a track from an empty queue."""

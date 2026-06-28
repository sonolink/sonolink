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

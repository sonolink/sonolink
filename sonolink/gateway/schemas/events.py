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

import types
from typing import Any

import msgspec

from sonolink.rest.schemas.track import Track

from ..enums import (
    DisconnectTriggerType,
    TrackEndReason,
    TrackExceptionSeverity,
)

__all__ = (
    "PlayerDisconnectEvent",
    "TrackEndEvent",
    "TrackException",
    "TrackExceptionEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
)


class PlayerDisconnectEvent(types.SimpleNamespace):
    trigger: DisconnectTriggerType
    """The trigger that caused the disconnect."""
    extra_data: Any | None
    """Extra data from the trigger.

    When :attr:`trigger` is :attr:`sonolink.gateway.DisconnectTriggerType.ERROR`, this usually
    is an :exc:`Exception` object.
    """


class TrackEndEvent(msgspec.Struct):
    """Represents a track end event dispatched whenever a track stops playing."""

    track: Track
    """The track that ended playing."""
    reason: TrackEndReason
    """The reason the track ended."""


class TrackException(msgspec.Struct):
    """Represents a TrackExceptionEvent's :attr:`TrackExceptionEvent.exception`."""

    message: str | None
    """The message of the exception."""
    severity: TrackExceptionSeverity
    """The severity of the exception."""
    cause: str
    """The cause of the exception."""
    cause_stack_trace: str = msgspec.field(name="causeStackTrace")
    """The full stack trace of the cause."""


class TrackExceptionEvent(msgspec.Struct):
    """Represents a track exception event dispatched whenever an error is found when playing a track."""

    track: Track
    """The track that threw the exception."""
    exception: TrackException
    """The occurred exception."""


class TrackStartEvent(msgspec.Struct):
    """Represents a track start event dispatched whenever a new track starts playing."""

    track: Track
    """The track that started playing."""


class TrackStuckEvent(msgspec.Struct):
    """Represents a track stuck event dispatched whenever a track gets stuck while playing."""

    track: Track
    """The track that got stuck."""
    threshold: int = msgspec.field(name="thresholdMs")
    """The threshold in milliseconds that was exceeded."""

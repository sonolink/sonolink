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

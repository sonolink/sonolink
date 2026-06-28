"""
MIT License

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

import abc
import types
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import msgspec

from sonolink.models.track import Playable
from sonolink.utils import cached_property

if TYPE_CHECKING:
    from .enums import DisconnectTriggerType, TrackEndReason
    from .node import Node
    from .schemas import events, receive

T = TypeVar("T", bound=msgspec.Struct | types.SimpleNamespace, covariant=True)

__all__ = (
    "EventModel",
    "PlayerDisconnectEvent",
    "PlayerUpdateEvent",
    "ReadyEvent",
    "StatsEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackStartEvent",
    "TrackStuckEvent",
    "WebSocketClosedEvent",
)


class EventModel(abc.ABC, Generic[T]):
    """Base class where all events models derive from.

    This is an :class:`abc.ABC` subclass.
    """

    __repr_attrs__: tuple[str, ...]
    _underlying: T

    def __init__(self, underlying: T, node: Node) -> None:
        self._underlying = underlying
        self._node: Node = node

    @property
    def node(self) -> Node:
        """The node that received the event."""
        return self._node

    def __getattr__(self, name: str) -> Any:
        try:
            return getattr(self._underlying, name)
        except AttributeError as exc:
            raise AttributeError(
                f"{self.__class__.__name__} does not have an attribute named {name}"
            ) from exc

    def __repr__(self) -> str:
        attrs = ", ".join(f"{a}={getattr(self, a)}" for a in self.__repr_attrs__)
        return f"<{self.__class__.__name__} {attrs}>"


class PlayerUpdateEvent(EventModel["receive.PlayerUpdateEvent"]):
    """Represents a player_update event."""

    __repr_attrs__ = ("state", "guild_id")

    state: receive.PlayerState
    """The state of the player."""

    guild_id: int
    """The guild ID of the player."""


class ReadyEvent(EventModel["receive.ReadyEvent"]):
    """Represents a ready event."""

    __repr_attrs__ = ("resumed", "session_id")

    resumed: bool
    """
    Whether the session was resumed,
    if this is ``False`` it implies a new connection was created.
    """

    session_id: str
    """The secret session ID."""


class StatsEvent(EventModel["receive.StatsEvent"]):
    """Represents a stats event."""

    __repr_attrs__ = (
        "players",
        "playing_players",
        "uptime",
        "memory",
        "cpu",
        "frame_stats",
    )

    players: int
    """The players count attached to the node."""

    playing_players: int
    """The players count attached to the node that are playing a track."""

    uptime: int
    """The node uptime in milliseconds."""

    memory: receive.MemoryStats
    """The memory stats of the node."""

    cpu: receive.CPUStats
    """The CPU stats of the node."""

    frame_stats: receive.FrameStats | None
    """The frame stats of the node."""


class TrackStartEvent(EventModel["events.TrackStartEvent"]):
    """Represents a track start event."""

    __repr_attrs__ = (
        "track",
        "original",
    )

    def __init__(
        self,
        underlying: events.TrackStartEvent,
        node: Node,
        original: Playable | None = None,
    ) -> None:
        super().__init__(underlying, node)
        self._original = original

    @cached_property("_cs_track")
    def track(self) -> Playable:
        """The track that started playing."""
        assert self.node.client
        return Playable(
            client=self.node.client, data=self._underlying.track, playlist=None
        )

    @property
    def original(self) -> Playable | None:
        """The original track associated with this event.

        This is the track that was passed to `play()` or added to the queue.
        This is useful in cases where you have modified the track before playing it.

        This is only set when the event is received after a call to `play()`.

        .. versionadded:: 1.2.0
        """
        return self._original


class TrackEndEvent(EventModel["events.TrackEndEvent"]):
    """Represents a track end event."""

    __repr_attrs__ = (
        "reason",
        "track",
        "original",
    )

    def __init__(
        self,
        underlying: events.TrackEndEvent,
        node: Node,
        original: Playable | None = None,
    ) -> None:
        super().__init__(underlying, node)
        self._original = original

    reason: TrackEndReason
    """The reason the track ended."""

    @cached_property("_cs_track")
    def track(self) -> Playable:
        """The track that ended playing."""
        assert self.node.client
        return Playable(
            client=self.node.client, data=self._underlying.track, playlist=None
        )

    @property
    def original(self) -> Playable | None:
        """The original track associated with this event.

        This is the track that was passed to `play()` or added to the queue.
        This is useful in cases where you have modified the track before playing it.

        .. versionadded:: 1.2.0
        """
        return self._original


class TrackExceptionEvent(EventModel["events.TrackExceptionEvent"]):
    """Represents a track exception event."""

    __repr_attrs__ = (
        "track",
        "exception",
    )

    exception: events.TrackException
    """The occurred exception."""

    @cached_property("_cs_track")
    def track(self) -> Playable:
        """The track that thew the exception."""
        assert self.node.client
        return Playable(
            client=self.node.client, data=self._underlying.track, playlist=None
        )


class TrackStuckEvent(EventModel["events.TrackStuckEvent"]):
    """Represents a track stuck event."""

    __repr_attrs__ = (
        "track",
        "threshold",
    )

    threshold: int
    """The threshold in milliseconds that was exceeded."""

    @cached_property("_cs_track")
    def track(self) -> Playable:
        """The track that got stuck."""
        assert self.node.client
        return Playable(
            client=self.node.client, data=self._underlying.track, playlist=None
        )


class PlayerDisconnectEvent(EventModel["events.PlayerDisconnectEvent"]):
    """Represents a player disconnected event."""

    __repr_attrs__ = (
        "trigger",
        "extra_data",
    )

    trigger: DisconnectTriggerType
    """The trigger that caused the disconnect."""

    extra_data: Any | None
    """Extra data from the trigger.

    When :attr:`trigger` is a :attr:`sonolink.gateway.DisconnectTriggerType.ERROR`, this usually
    is an :exc:`Exception` object.
    """


class WebSocketClosedEvent(EventModel["receive.WebSocketClosedEvent"]):
    """Represents a ws_close event."""

    __repr_attrs__ = (
        "code",
        "reason",
        "by_remote",
    )

    code: int
    """The Discord close event code."""

    reason: str
    """The reason why the connection was closed."""

    by_remote: bool
    """Whether the closure was made by Discord."""

"""MIT License

Copyright (c) 2026-present SonoLink Development Team

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
import asyncio
import time
from typing import TYPE_CHECKING, Annotated, Any

from sonolink import _registry
from sonolink.gateway.player.handlers._autoplay import AutoPlayHandler
from sonolink.gateway.player.handlers._events import EventsHandler
from sonolink.gateway.player.handlers._inactivity import InactivityHandler
from sonolink.gateway.player.handlers._lifecycle import LifecycleHandler
from sonolink.gateway.player.handlers._playback import PlaybackHandler
from sonolink.models.filters import Filters

from ..enums import AutoPlayMode, DisconnectTriggerType, QueueMode
from ..queue.queue import Queue

if TYPE_CHECKING:
    from sonolink.gateway.schemas.receive import PlayerState
    from sonolink.models.settings import AutoPlaySettings, HistorySettings
    from sonolink.models.track import Playable

    from ..node import Node


__all__ = ("BasePlayer", "PlayerConnectionState")


class PlayerConnectionState:
    """Represents the voice connection state for a :class:`BasePlayer`.

    This class is intended to be subclassed if you need to store
    extra metadata during the Discord handshake.
    """

    __slots__ = (
        "_connected_flag",
        "channel_id",
        "endpoint",
        "session_id",
        "token",
    )

    def __init__(self) -> None:
        self.token: str | None = None
        self.endpoint: str | None = None
        self.session_id: str | None = None
        self.channel_id: str | None = None
        self._connected_flag: asyncio.Event = asyncio.Event()

    @property
    def is_complete(self) -> bool:
        """Indicates if all gateway data has been received."""
        return all((self.token, self.endpoint, self.session_id, self.channel_id))


class BasePlayer(abc.ABC):
    """Abstract base class that defines the interface for a Lavalink player.

    This class is library-agnostic and is intended to be subclassed to provide
    concrete implementations compatible with ``discord.py``, ``py-cord``, ``disnake``, or ``nextcord``.
    Each library-specific subclass is responsible for implementing the voice protocol
    integration (e.g., inheriting from the appropriate ``VoiceProtocol`` class) and
    fulfilling the abstract methods defined here.

    The public API exposed by this class remains consistent across all three
    Discord library backends, allowing shared business logic, extensions, and
    third-party integrations to target ``BasePlayer`` without coupling to any
    specific library.

    Parameters
    ----------
    node : :class:`~sonolink.Node` | None
        The Lavalink node to associate this player with. If ``None``, the player
        will attempt to resolve an available node at connection time.
    queue_mode : :class:`~sonolink.QueueMode`
        The initial queue looping mode. Defaults to ``QueueMode.NORMAL``.
    autoplay_settings : :class:`~sonolink.models.AutoPlaySettings` | None
        Configuration for the AutoPlay feature. If ``None``, a default
        configuration is used. History must be enabled if AutoPlay is used.
    history_settings : :class:`~sonolink.models.HistorySettings` | None
        Configuration for queue history. If ``None``, a default configuration
        is used.
    volume : :class:`int` | None
        The initial volume of the player (0–1000). Defaults to ``100``.
    paused : :class:`bool` | None
        Whether the player should start in a paused state. Defaults to ``False``.
    filters : :class:`~sonolink.models.Filters` | None
        The initial set of audio filters to apply. If ``None``, an empty
        :class:`~sonolink.models.Filters` instance is used.

    Attributes
    ----------
    guild
        The guild this player is attached to. The concrete type depends on the
        underlying Discord library (e.g. :class:`discord:discord.Guild`
        (discord.py), :class:`pycord:discord.Guild` (py-cord),
        :class:`disnake:disnake.Guild` (disnake), or
        :class:`nextcord:nextcord.Guild` (nextcord)).
    channel
        The voice channel this player is currently connected to. The concrete
        type depends on the underlying Discord library.
    client
        The Discord client instance driving this player. The concrete type
        depends on the underlying Discord library.
    """

    __slots__ = (
        "_autoplay_handler",
        "_connection",
        "_events_handler",
        "_filters",
        "_inactivity_handler",
        "_last_position",
        "_last_update",
        "_lifecycle_handler",
        "_node",
        "_original_track",
        "_paused",
        "_playback_handler",
        "_queue",
        "_ready",
        "_volume",
    )

    _connection: PlayerConnectionState
    _filters: Filters
    _last_position: Annotated[int, "ms"]
    _last_update: Annotated[float, "time.monotonic"]
    _node: Node | None
    _original_track: Playable | None
    _paused: bool
    _queue: Queue
    _ready: bool
    _volume: int

    client: Any
    channel: Any
    _guild: Any

    def __init__(
        self,
        *,
        node: Node | None = None,
        queue_mode: QueueMode = QueueMode.NORMAL,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
        volume: int | None = None,
        paused: bool | None = None,
        filters: Filters | None = None,
    ) -> None:
        self._node = node
        self._connection = self.get_connection_state()

        self._filters = filters or Filters()
        self._queue = Queue(mode=queue_mode, history_settings=history_settings)
        self._paused = paused or False
        self._volume = volume if volume is not None else 100
        self._original_track = None

        self._last_position = 0
        self._last_update = 0.0

        self._autoplay_handler: AutoPlayHandler = AutoPlayHandler(
            self, settings=autoplay_settings
        )
        self._events_handler: EventsHandler = EventsHandler(self)
        self._inactivity_handler: InactivityHandler = InactivityHandler(self)
        self._lifecycle_handler: LifecycleHandler = LifecycleHandler(self)
        self._playback_handler: PlaybackHandler = PlaybackHandler(self)

        self._ready = False

    @abc.abstractmethod
    def __call__(self, client: Any, channel: Any) -> BasePlayer:
        """Bind the player when a pre-configured **instance** is passed to
        a library's ``connect`` method.

        Binds the VoiceProtocol attributes, resolves the guild from the channel,
        and registers the player with its node.

        Parameters
        ----------
        client
            The client instance.
        channel
            The voice channel being connected to.

        Returns
        -------
        :class:`BasePlayer`
            The player instance, fully initialised.
        """

    @property
    def autoplay(self) -> AutoPlayMode:
        """The current :class:`~sonolink.AutoPlayMode` for this player.

        When AutoPlay is enabled, the player will automatically fetch and enqueue
        related tracks when the queue is exhausted.

        Raises
        ------
        RuntimeError
            When setting, if the player's history is disabled (history is required
            for AutoPlay to function).
        """
        return self._autoplay_handler._settings.mode

    @autoplay.setter
    def autoplay(self, value: AutoPlayMode) -> None:
        if not self._queue._history.enabled:
            raise RuntimeError(
                f"Player {self.guild.id} has disabled history, which is required for AutoPlay."
            )
        self._autoplay_handler._settings.mode = value

    @property
    def autoplay_settings(self) -> AutoPlaySettings:
        """The current :class:`~sonolink.models.AutoPlaySettings` for this player.

        Can be mutated directly to update individual fields, or replaced entirely.

        .. versionadded:: 1.1.0

        Returns
        -------
        :class:`~sonolink.models.AutoPlaySettings`
        """
        return self._autoplay_handler._settings

    @autoplay_settings.setter
    def autoplay_settings(self, value: AutoPlaySettings) -> None:
        self._autoplay_handler._settings = value

    @property
    def current(self) -> Playable | None:
        """The track that is currently playing, or ``None`` if the player is idle.

        Returns
        -------
        :class:`~sonolink.models.Playable` | None
        """
        return self._queue.current_track

    @property
    def filters(self) -> Filters:
        """The :class:`~sonolink.models.Filters` currently applied to this player.

        To apply new filters, use :meth:`set_filters` rather than mutating this
        object directly, so that the updated state is dispatched to the Lavalink node.

        Returns
        -------
        :class:`~sonolink.models.Filters`
        """
        return self._filters

    @property
    def guild(self) -> Any:
        """The guild this player is associated with.

        The concrete return type is the guild class of the underlying Discord
        library (e.g. ``discord.Guild``, ``disnake.Guild``).

        Raises
        ------
        RuntimeError
            If the player has not yet been attached to a guild.
        """
        if self._guild is None:
            raise RuntimeError("Player is not yet attached to a guild.")
        return self._guild

    @property
    def history_settings(self) -> HistorySettings:
        """The current :class:`~sonolink.models.HistorySettings` for this player's queue.

        Can be mutated directly to update individual fields, or replaced entirely.

        .. versionadded:: 1.1.0

        Returns
        -------
        :class:`~sonolink.models.HistorySettings`
        """
        return self._queue._history._settings

    @history_settings.setter
    def history_settings(self, value: HistorySettings) -> None:
        self._queue._history._settings = value

    @property
    def node(self) -> Node:
        """The :class:`~sonolink.Node` this player is currently attached to.

        Raises
        ------
        RuntimeError
            If the player is not currently attached to a node.
        """
        if self._node is None:
            raise RuntimeError(f"Player {self.guild.id} is not attached to a node.")
        return self._node

    @property
    def paused(self) -> bool:
        """Whether the player is currently paused.

        Returns
        -------
        :class:`bool`
        """
        return self._paused

    @property
    def position(self) -> int:
        """The estimated current playback position in milliseconds.

        When the player is paused or has not yet started, this returns the last
        known position. Otherwise, it is calculated by interpolating the time
        elapsed since the last state update received from the Lavalink node.

        Returns
        -------
        :class:`int`
            Position in milliseconds.
        """
        if self._paused or self._last_update == 0:
            return self._last_position

        delta = int((time.monotonic() - self._last_update) * 1000)
        return self._last_position + delta

    @property
    def queue(self) -> Queue:
        """The :class:`~sonolink.Queue` associated with this player.

        The queue manages both upcoming tracks and playback history. Tracks can
        be added with ``queue.put()`` / ``queue.put_wait()`` and inspected or
        manipulated via the queue's public API.

        Returns
        -------
        :class:`~sonolink.Queue`
        """
        return self._queue

    @property
    def queue_mode(self) -> QueueMode:
        """The current :class:`~sonolink.QueueMode` for this player's queue.

        .. versionadded:: 1.1.0

        Returns
        -------
        :class:`~sonolink.QueueMode`
        """
        return self._queue.mode

    @queue_mode.setter
    def queue_mode(self, value: QueueMode) -> None:
        self._queue.mode = value

    @property
    def volume(self) -> int:
        """The current volume of the player as an integer in the range ``0``–``1000``.

        ``100`` represents the default (unmodified) volume. Values above ``100``
        amplify the audio and may introduce distortion.

        Returns
        -------
        :class:`int`
        """
        return self._volume

    async def connect(
        self,
        *,
        timeout: float = 10.0,
        reconnect: bool = False,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        """Connect this player to its assigned voice channel.

        Called automatically by libraries after the player is instantiated.
        Manual invocation is not normally required.

        Parameters
        ----------
        timeout : :class:`float`
            Seconds to wait for the Discord gateway handshake before raising.
            Defaults to ``10.0``.
        reconnect : :class:`bool`
            Whether to attempt reconnection on failure. Defaults to ``False``.
        self_deaf : :class:`bool`
            Whether to join the channel self-deafened. Defaults to ``False``.
        self_mute : :class:`bool`
            Whether to join the channel self-muted. Defaults to ``False``.
        """
        await self._lifecycle_handler.connect(
            timeout=timeout,
            reconnect=reconnect,
            self_deaf=self_deaf,
            self_mute=self_mute,
        )

    async def disconnect(self, *, force: bool = False) -> None:
        """Disconnect this player, destroy it on the Lavalink node, and clean up
        all internal state.

        Parameters
        ----------
        force : :class:`bool`
            If ``True``, proceeds even if the player is not currently connected.
            Defaults to ``False``.
        """
        await self._lifecycle_handler.disconnect(
            force=force,
            trigger=DisconnectTriggerType.MANUAL,
        )

    async def move_to(self, node: Node, /) -> None:
        """Migrate this player to a different Lavalink node without interrupting
        playback.

        Parameters
        ----------
        node: :class:`~sonolink.Node`
            The destination node.
        """
        await self._lifecycle_handler.move_to(node)

    async def play(
        self,
        track: Playable,
        /,
        *,
        start: int = 0,
        end: int | None = None,
        volume: int | None = None,
        paused: bool | None = None,
    ) -> Playable:
        """Begin playback of the specified track.

        If a track is already playing, it is stopped and the currently playing
        track is added to history (if history is enabled) before the new track
        starts.

        Parameters
        ----------
        track : :class:`~sonolink.models.Playable`
            The track to play.
        start : :class:`int`
            The position in milliseconds at which to begin playback.
            Defaults to ``0``.
        end : :class:`int` | None
            The position in milliseconds at which to stop playback.
            If ``None``, the track plays to completion. Defaults to ``None``.
        volume : :class:`int` | None
            Override the player volume for this track only. If ``None``,
            the current player volume is used. Defaults to ``None``.
        paused : :class:`bool` | None
            If ``True``, the track begins in a paused state. If ``None``,
            the player's current pause state is preserved. Defaults to ``None``.

        Returns
        -------
        :class:`~sonolink.models.Playable`
            The track that was dispatched to the Lavalink node for playback.
        """
        return await self._playback_handler.play(
            track,
            start=start,
            end=end,
            volume=volume,
            paused=paused,
        )

    async def stop(
        self,
        /,
        *,
        clear_queue: bool = False,
        clear_history: bool = False,
    ) -> None:
        """Stop the currently playing track.

        This sends a stop request to the Lavalink node and resets the player's
        internal position tracking and current track reference.

        Parameters
        ----------
        clear_queue : :class:`bool`
            If ``True``, all pending tracks in the queue are removed and
            the :attr:`Queue.mode` is reset to :attr:`QueueMode.NORMAL`.
            Defaults to ``False``.
        clear_history : :class:`bool`
            If ``True``, the playback history is cleared. Defaults to ``False``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.stop(
            clear_queue=clear_queue,
            clear_history=clear_history,
        )

    async def pause(self) -> None:
        """Set the pause state of the player.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.pause()

    async def resume(self) -> None:
        """Resume playback if the player is currently paused.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.resume()

    async def skip(self) -> Playable | None:
        """Skip the currently playing track and advance to the next one in the queue.

        If the queue is empty and AutoPlay is enabled, a related track may be
        fetched automatically. If neither a queued nor an AutoPlay track is
        available, playback stops and ``None`` is returned.

        Returns
        -------
        :class:`~sonolink.models.Playable` | None
            The track that began playing after the skip, or ``None`` if the
            player stopped due to an empty queue with no AutoPlay fallback.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        QueueEmpty
            If the queue is empty and AutoPlay is disabled or yields no results.
        """
        return await self._playback_handler.skip()

    async def skip_to(self, index: int, /) -> Playable:
        """Skip directly to a track at the given queue index.

        The current track is added to history and the target track begins
        playing immediately. This does **not** fall back to AutoPlay; if the
        index is out of range, an :exc:`IndexError` is raised.

        .. versionadded:: 1.3.0

        Parameters
        ----------
        index: :class:`int`
            The queue index of the track to play.

        Returns
        -------
        :class:`~sonolink.models.Playable`
            The track that is now playing.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        IndexError
            The index is out of range.
        QueueEmpty
            The queue is empty.
        """
        return await self._playback_handler.skip_to(index)

    async def previous(self) -> Playable:
        """Return to the most recently played track in the history.

        The current track is pushed back to the front of the queue so it can
        be reached again via :meth:`skip`. The historical track then begins
        playing immediately.

        Returns
        -------
        :class:`~sonolink.models.Playable`
            The historical track that is now playing.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        HistoryEmpty
            If there is no previous track in the history.
        """
        return await self._playback_handler.previous()

    async def seek(self, position: int, /) -> None:
        """Seek to an arbitrary position within the current track.

        Parameters
        ----------
        position : :class:`int`
            The target position in milliseconds. Must be within the bounds
            of the current track's duration.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.seek(position)

    async def set_volume(self, value: int, /) -> None:
        """Set the player's output volume.

        Parameters
        ----------
        value : :class:`int`
            The desired volume level, in the range ``0``–``1000``.
            ``100`` is the default (unmodified) level.

        Raises
        ------
        ValueError
            If ``value`` is outside the range ``0``–``1000``.
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.set_volume(value)

    async def set_filters(
        self,
        filters: Filters,
        /,
        *,
        seek: bool = False,
    ) -> None:
        """Apply a new set of audio filters to this player.

        Parameters
        ----------
        filters : :class:`~sonolink.models.Filters`
            The :class:`~sonolink.models.Filters` instance to apply.
        seek : :class:`bool`
            If ``True``, the player seeks to the current position immediately
            after applying filters. This forces Lavalink to process the audio
            through the new filter chain without a audible delay.
            Defaults to ``False``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.set_filters(filters.payload, seek=seek)

    async def update(
        self,
        *,
        queue_mode: QueueMode | None = None,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
        volume: int | None = None,
        filters: Filters | None = None,
    ) -> None:
        """Update the player's configuration in-place.

        .. versionadded:: 1.1.0

        Parameters
        ----------
        queue_mode : :class:`~sonolink.QueueMode` | None
            The new queue looping mode. If ``None``, the current mode is preserved.
        autoplay_settings : :class:`~sonolink.models.AutoPlaySettings` | None
            New AutoPlay configuration. If ``None``, the current settings are preserved.
        history_settings : :class:`~sonolink.models.HistorySettings` | None
            New history configuration. If ``None``, the current settings are preserved.
        volume : :class:`int` | None
            New volume in the range ``0``–``1000``. If ``None``, the current volume is preserved.
        filters : :class:`~sonolink.models.Filters` | None
            New audio filters. If ``None``, the current filters are preserved.
        """
        if queue_mode is not None:
            self.queue_mode = queue_mode

        if autoplay_settings is not None:
            self.autoplay_settings = autoplay_settings

        if history_settings is not None:
            self.history_settings = history_settings

        if volume is not None:
            await self.set_volume(volume)

        if filters is not None:
            await self.set_filters(filters)

    @abc.abstractmethod
    async def on_voice_server_update(self, data: Any) -> None:
        """Handle a ``VOICE_SERVER_UPDATE`` payload from the Discord gateway.

        This provides the voice server token and endpoint required by the
        Lavalink node to establish or re-establish the audio stream. This
        method should be called by the library-specific subclass in response
        to the corresponding gateway event.

        The ``data`` dictionary is passed as a raw mapping so that this base
        class remains decoupled from any specific library's type aliases.
        Subclasses may cast it to the appropriate typed dict for their library
        (e.g., ``discord.types.voice.VoiceServerUpdate``,
        ``disnake.types.voice.VoiceServerUpdate``).

        Parameters
        ----------
        data : Any
            The raw ``VOICE_SERVER_UPDATE`` payload received from the Discord
            gateway.
        """
        ...

    @abc.abstractmethod
    async def on_voice_state_update(self, data: Any) -> None:
        """Handle a ``VOICE_STATE_UPDATE`` payload from the Discord gateway.

        This provides the session ID and channel ID required for the voice
        connection handshake with the Lavalink node. This method should be
        called by the library-specific subclass in response to the
        corresponding gateway event.

        The ``data`` dictionary is passed as a raw mapping so that this base
        class remains decoupled from any specific library's type aliases.
        Subclasses may cast it to the appropriate typed dict for their library
        (e.g., ``discord.types.voice.GuildVoiceState``,
        ``disnake.types.voice.GuildVoiceState``).

        Parameters
        ----------
        data : Any
            The raw ``VOICE_STATE_UPDATE`` payload received from the Discord
            gateway.
        """
        ...

    @abc.abstractmethod
    def cleanup(self) -> None:
        """Clean the internal state of the Player. This is automatically called by the library when failures
        or disconnects occur.

        If this is overridden, it **must** call the original ``cleanup``.
        """

    def get_connection_state(self) -> PlayerConnectionState:
        """Return a :class:`~sonolink.PlayerConnectionState` instance
        for this player.

        Override this method to supply a custom connection state subclass with
        additional metadata relevant to your application.

        Returns
        -------
        :class:`~sonolink.PlayerConnectionState`
        """
        return PlayerConnectionState()

    def _ensure_node(self) -> Node:
        node = self._node

        if node is None:
            if not bool(self.client):
                raise RuntimeError("Cannot ensure Node without a Client.")

            sl_client = _registry.clients.get(self.client)
            if sl_client is None:
                raise RuntimeError(
                    f"No sonolink.Client is associated with {self.client!r}"
                )

            rtc_region = self.channel.rtc_region
            if rtc_region is not None and not isinstance(rtc_region, str):
                rtc_region = getattr(rtc_region, "value", str(rtc_region))

            node = sl_client.get_best_node(region=rtc_region)
            self._node = node

        if self.guild.id not in node._players:
            node._add_player(self)

        return node

    async def _dispatch_event(self, data: dict[str, Any]) -> None:
        await self._events_handler._dispatch_event(data)

    def _update_state(self, state: PlayerState, /) -> None:
        self._events_handler._update_state(state)

    async def _dispatch_voice_update(self) -> None:
        await self._events_handler._dispatch_voice_update()

    def _check_inactivity(self) -> None:
        self._inactivity_handler._check_inactivity()

    def _start_inactivity_timer(self) -> None:
        self._inactivity_handler._start_inactivity_timer()

    def _stop_inactivity_timer(self) -> None:
        self._inactivity_handler._stop_inactivity_timer()

    async def _inactivity_timeout(self, timeout: int) -> None:
        await self._inactivity_handler._inactivity_timeout(timeout)

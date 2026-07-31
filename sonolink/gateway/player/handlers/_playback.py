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

import time
import types
from typing import Any, Callable

import msgspec

from sonolink.gateway.enums import AutoPlayMode, QueueMode
from sonolink.gateway.errors import AutoPlaySeedMissing, QueueEmpty
from sonolink.models.filters import Filters
from sonolink.models.track import Playable
from sonolink.rest.schemas.filters import PlayerFilters
from sonolink.rest.schemas.player import UpdatePlayerRequest, UpdatePlayerTrackRequest

from ._base import HandlerBase, _log

__all__ = ()


class PlaybackHandler(HandlerBase):
    """Internal handler responsible for audio playback control logic."""

    __slots__ = ()

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
        node = self._player.node
        assert node._resume_session is not None

        volume = volume if volume is not None else self._player._volume
        paused = paused if paused is not None else self._player._paused

        track_payload = UpdatePlayerTrackRequest(
            encoded=track.encoded,
            user_data=self._build_user_data(track.extras),
        )
        data = UpdatePlayerRequest(
            track=track_payload,
            position=start,
            endtime=end if end is not None else msgspec.UNSET,
            volume=volume,
            paused=paused,
        )

        self._player._original_track = track

        try:
            await node._manager.update_player(
                session_id=node._resume_session,
                guild_id=str(self._player.guild.id),
                data=data,
            )
        except Exception as exc:
            self._player._original_track = None
            raise exc from None

        self._player._volume = volume
        self._player._paused = paused
        self._player._last_position = start
        self._player._last_update = time.monotonic()

        current = self._player._queue._current_track
        if current is not None and current is not track:
            self._player._queue._history._push(current)
            
        self._player._queue.current_track = track
        self._player._stop_inactivity_timer()
        return track

    async def stop(
        self,
        /,
        *,
        clear_queue: bool = False,
        clear_history: bool = False,
    ) -> None:
        node = self._player.node
        assert node._resume_session is not None

        track_payload = UpdatePlayerTrackRequest(encoded=None)
        data = UpdatePlayerRequest(track=track_payload)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._last_position = 0
        self._player._last_update = 0.0
        self._player._queue.current_track = None
        self._player._original_track = None

        if clear_queue:
            self._player._queue.clear()
            self._player._queue._autoplay_items.clear()
            self._player._queue.mode = QueueMode.NORMAL

        if clear_history:
            self._player._queue.clear_history()

        _log.debug(
            "Player %s: Stopped playback and reset state.", self._player.guild.id
        )
        self._player._check_inactivity()

    async def pause(self, value: bool = True, /) -> None:
        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(paused=value)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._paused = value
        _log.debug("Player %s: Set paused state to %s", self._player.guild.id, value)

    async def resume(self) -> None:
        await self.pause(False)

    async def previous(self) -> Playable:
        track = self._player._queue.previous()
        await self.play(track)
        return track

    async def skip(
        self, *, key: Callable[[Playable], Any] | None = None
    ) -> Playable | None:
        try:
            next_track = self._player.queue.get(key=key)
            await self.play(next_track)
            return next_track
        except QueueEmpty:
            pass

        handler = self._player._autoplay_handler
        if handler._settings.mode != AutoPlayMode.DISABLED:
            try:
                track = await handler.auto_play()
            except AutoPlaySeedMissing:
                await self.stop()
                raise

            if track is not None:
                return track

        await self.stop()
        raise QueueEmpty

    async def skip_to(self, index: int, /) -> Playable:
        track = self._player._queue.pop_at(index)
        await self.play(track)
        return track

    async def seek(self, position: int, /) -> None:
        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(position=position)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._last_position = position
        self._player._last_update = time.monotonic()

        _log.debug("Player %s: Sought to %dms", self._player.guild.id, position)

    async def set_volume(self, value: int, /) -> None:
        if not 0 <= value <= 1000:
            raise ValueError("Volume must be between 0 and 1000.")

        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(volume=value)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._volume = value
        _log.debug("Player %s: Set volume to %d.", self._player.guild.id, value)

    async def set_filters(
        self,
        filters: PlayerFilters,
        /,
        *,
        seek: bool = False,
    ) -> None:
        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(filters=filters)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        assert self._player.node.client
        self._player._filters = Filters._from_data(self._player.node.client, filters)

        if seek:
            await self.seek(self._player.position)

        _log.debug(
            "Player %s: Successfully applied filters: %r",
            self._player.guild.id,
            filters,
        )

    def _build_user_data(
        self, extras: types.SimpleNamespace
    ) -> dict[str, Any] | msgspec.UnsetType:
        result: dict[str, Any] = {}
        skipped: list[str] = []

        for key, value in vars(extras).items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                result[key] = value
            else:
                skipped.append(repr(key))

        if skipped:
            count = len(skipped)
            keys_str = (
                f"{', '.join(skipped[:-1])}, and {skipped[-1]}"
                if count > 2
                else " and ".join(skipped)
            )
            _log.warning(
                "Track extras %s (%s) %s not json-serializable and will not be sent as "
                "user_data to Lavalink.\nUse event.original.extras to access %s.",
                "keys" if count > 1 else "key",
                keys_str,
                "are" if count > 1 else "is",
                "them" if count > 1 else "it",
            )

        return result or msgspec.UNSET

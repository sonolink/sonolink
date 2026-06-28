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

import asyncio
from typing import TYPE_CHECKING

from sonolink.gateway.enums import AutoPlayMode
from sonolink.gateway.errors import AutoPlaySeedMissing
from sonolink.models.playlist import Playlist
from sonolink.models.settings import AutoPlaySettings
from sonolink.models.track import Playable

from ._base import HandlerBase, _log

if TYPE_CHECKING:
    from .._base import BasePlayer


class AutoPlayHandler(HandlerBase):
    """Internal handler responsible for audio discovery and autonomous playback."""

    __slots__ = (
        "_seeds",
        "_lock",
        "_settings",
    )

    def __init__(
        self,
        player: BasePlayer,
        settings: AutoPlaySettings | None = None,
    ) -> None:
        super().__init__(player)
        self._seeds: set[str] = set()
        self._lock: asyncio.Lock = asyncio.Lock()
        self._settings = settings or AutoPlaySettings.default()

    async def auto_play(self) -> Playable | None:
        if self._settings.mode == AutoPlayMode.DISABLED:
            return None

        if len(self._player.queue) > 0 or self._lock.locked():
            return None

        async with self._lock:
            return await self._fill_auto_queue()

    async def _fill_auto_queue(self) -> Playable | None:
        reference = self._player.current or (
            self._player.queue.history[-1] if self._player.queue.history else None
        )

        if not reference or not reference.identifier:
            raise AutoPlaySeedMissing(
                "Could not find a valid track identifier to generate recommendations from."
            )

        if len(self._seeds) > self._settings.max_seeds:
            self._seeds.clear()

        self._seeds.add(reference.identifier)
        query = str(self._settings.provider).format(identifier=reference.identifier)

        try:
            search = await self._player.node.search_track(query)

            if (
                (result := search.result) is None
                or search.is_error()
                or search.is_empty()
            ):
                return None

            if isinstance(result, Playlist):
                raw_tracks = result.tracks
            elif isinstance(result, list):
                raw_tracks = result
            else:
                raw_tracks = [result]

            discovery = [t for t in raw_tracks if t.identifier not in self._seeds]
            if not discovery:
                return None

            return await self._apply_discovery(discovery)
        except Exception as exc:
            _log.error(
                "Player %s: AutoPlay failed: %s",
                self._player.guild.id,
                exc,
                exc_info=True,
            )
            return None

    async def _apply_discovery(self, tracks: list[Playable]) -> Playable | None:
        if not tracks:
            return None

        track = tracks.pop(0)
        track._autoplay = True

        if self._settings.mode == AutoPlayMode.ENABLED:
            queue_limit = max(0, self._settings.discovery_count - 1)
            self._player.queue.put_autoplay(tracks[:queue_limit])

        await self._player.play(track)
        return track

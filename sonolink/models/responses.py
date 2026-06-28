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

import msgspec

from sonolink.gateway.schemas import TrackException
from sonolink.rest.enums import TrackLoadResult
from sonolink.rest.schemas import PlaylistData, Track, TrackLoadingResponse
from sonolink.utils import cached_property

from .base import BaseModel
from .playlist import Playlist
from .track import Playable

__all__ = ("SearchResult",)


class SearchResult(BaseModel[TrackLoadingResponse]):
    """The result of a track search."""

    __slots__ = (
        "_cs_data",
        "_cs_exception",
    )

    @property
    def type(self) -> TrackLoadResult:
        """The result type."""
        return self._data.load_type

    def is_error(self) -> bool:
        """Whether this search result is an error."""
        return self.type is TrackLoadResult.ERROR

    def is_empty(self) -> bool:
        """Whether this search result is empty.
        An empty search result has no :attr:`SearchResult.result`.
        """
        return self.type is TrackLoadResult.EMPTY

    @cached_property("_cs_data")
    def result(self) -> Playlist | Playable | list[Playable] | None:
        r"""Return the data of the search result. Depending on :attr:`SearchResult.type`, this property
        will return a different value.

        If type is :attr:`sonolink.TrackLoadResult.TRACK`, this will return a :class:`sonolink.models.Playable`.
        If type is :attr:`sonolink.TrackLoadResult.PLAYLIST`, this will return a :class:`sonolink.models.Playlist`.
        If type is :attr:`sonolink.TrackLoadResult.SEARCH`, this will return a list of :class:`sonolink.models.Playable`\s.
        """
        assert self._client

        match self.type:
            case TrackLoadResult.TRACK:
                payload = msgspec.convert(self._data.data, Track)
                return Playable(
                    client=self._client,
                    data=payload,
                    playlist=None,
                )
            case TrackLoadResult.PLAYLIST:
                payload = msgspec.convert(self._data.data, PlaylistData)
                return Playlist(
                    client=self._client,
                    data=payload,
                )
            case TrackLoadResult.SEARCH:
                tracks = msgspec.convert(self._data.data, list[Track])
                return [
                    Playable(client=self._client, data=d, playlist=None) for d in tracks
                ]
            case _:
                return None

    @cached_property("_cs_exception")
    def exception(self) -> TrackException | None:
        """Return the raw exception data of this search result.

        This will be ``None`` if :meth:`SearchResult.is_error` is ``False``.
        """
        if not self.is_error():
            return None
        return msgspec.convert(self._data.data, TrackException)

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

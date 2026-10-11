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

import msgspec

from ..schemas import track

if TYPE_CHECKING:
    from .base import HTTPClient


class TrackHTTPMixin:
    """Mixin for Track related HTTP operations."""

    async def load_track(
        self: HTTPClient, identifier: str
    ) -> track.TrackLoadingResponse:
        url = "/loadtracks"
        res = await self.request("GET", url, params={"identifier": identifier})
        return msgspec.json.decode(res, type=track.TrackLoadingResponse)

    async def decode_track(self: HTTPClient, encoded: str) -> track.TrackDecodeResponse:
        url = "/decodetrack"
        res = await self.request("GET", url, params={"encodedTrack": encoded})
        return msgspec.json.decode(res, type=track.TrackDecodeResponse)

    async def decode_tracks(
        self: HTTPClient, encoded_tracks: list[str]
    ) -> track.TracksDecodeResponse:
        url = "/decodetracks"
        res = await self.request(
            "POST",
            url,
            data=msgspec.json.encode(encoded_tracks),
            headers={"Content-Type": "application/json"},
        )
        return msgspec.json.decode(res, type=track.TracksDecodeResponse)

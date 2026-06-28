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

import logging
import urllib.parse
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal

import msgspec

from sonolink.models.info import ServerInfo
from sonolink.models.player_info import PlayerInfo
from sonolink.models.responses import SearchResult
from sonolink.models.track import Playable
from sonolink.network import HTTPFactory
from sonolink.rest.enums import TrackSourceType
from sonolink.rest.errors import HTTPException
from sonolink.rest.http import RESTClient

if TYPE_CHECKING:
    from sonolink.network import SessionType

from ._base import NodeComponent

__all__ = ("HTTPClient",)

_log = logging.getLogger(__name__)


class HTTPClient(NodeComponent):
    """Internal component responsible for handling REST requests."""

    def init_manager(self, session: SessionType | None) -> RESTClient:
        headers = {"Authorization": self.node.password}
        if session:
            manager = HTTPFactory.from_http(session)
        else:
            manager_cls = HTTPFactory.http_manager()
            manager = manager_cls()
        return RESTClient(manager, base_url=self.node._uri, headers=headers)

    async def search_track(
        self,
        query: str,
        *,
        source: TrackSourceType | str | None = None,
    ) -> SearchResult:
        client = self.node._ensure_client()

        is_url = query.startswith(("http://", "https://"))
        formatted = (
            query
            if is_url or source is None
            else f"{str(source).removesuffix(':')}:{query}"
        )

        encoded = urllib.parse.quote(formatted)
        cached_result = self.node._cache.get(encoded)

        if isinstance(cached_result, SearchResult):
            return cached_result

        data = await self.node._manager.load_track(formatted)
        result = SearchResult(client=client, data=data)
        self.node._cache.put(encoded, result)
        return result

    async def decode_track(self, encoded: str) -> Playable:
        client = self.node._ensure_client()
        data = await self.node._manager.decode_track(encoded)
        return Playable(client=client, data=data)

    async def decode_tracks(self, *encoded: str) -> list[Playable]:
        client = self.node._ensure_client()
        data = await self.node._manager.decode_tracks(list(encoded))
        return [Playable(client=client, data=d) for d in data]

    async def fetch_info(self) -> ServerInfo:
        client = self.node._ensure_client()
        data = await self.node._manager.lavalink_info()
        return ServerInfo(client=client, data=data)

    async def fetch_players(self) -> list[PlayerInfo]:
        client = self.node._ensure_client()
        data = await self.node._manager.get_players(self.node.session_id)
        return [PlayerInfo(client=client, data=d) for d in data]

    async def fetch_player(self, guild_id: int) -> PlayerInfo:
        client = self.node._ensure_client()
        data = await self.node._manager.get_player(
            session_id=self.node.session_id,
            guild_id=str(guild_id),
        )
        return PlayerInfo(client=client, data=data)

    async def disconnect_player(self, guild_id: int) -> None:
        _ = self.node._ensure_client()
        await self.node._manager.destroy_player(
            session_id=self.node.session_id,
            guild_id=str(guild_id),
        )

    async def send(
        self,
        method: Literal["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: Any | None = None,
    ) -> dict[str, Any] | list[Any] | str | bytes | None:
        try:
            response = await self.node._manager.request(
                method=method,
                url=path,
                data=data,
                params=params,
                json=json,
                headers=headers,
            )
        except HTTPException:
            raise
        except Exception as exc:
            _log.warning(
                "Unexpected error while sending request to %r: %s", self.node, exc
            )
            return None

        if response is None:
            return None

        try:
            data_resp = msgspec.json.decode(response)
        except msgspec.DecodeError:
            pass
        else:
            return data_resp

        try:
            return response.decode("utf-8")
        except UnicodeDecodeError:
            return response

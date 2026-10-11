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

from ..schemas import player

if TYPE_CHECKING:
    from .base import HTTPClient


class PlayerHTTPMixin:
    """Mixin for Player related HTTP operations."""

    async def get_players(
        self: HTTPClient, session_id: str
    ) -> player.GetPlayersResponse:
        url = f"/sessions/{session_id}/players"
        res = await self.request("GET", url)
        return msgspec.json.decode(res, type=player.GetPlayersResponse)

    async def get_player(
        self: HTTPClient, *, session_id: str, guild_id: str
    ) -> player.GetPlayerResponse:
        url = f"/sessions/{session_id}/players/{guild_id}"
        res = await self.request("GET", url)
        return msgspec.json.decode(res, type=player.GetPlayerResponse)

    async def update_player(
        self: HTTPClient,
        *,
        session_id: str,
        guild_id: str,
        data: player.UpdatePlayerRequest,
        no_replace: bool | None = None,
    ) -> player.UpdatePlayerResponse:
        url = f"/sessions/{session_id}/players/{guild_id}"
        params: dict[str, str] = {}

        if no_replace is not None:
            params["noReplace"] = str(no_replace).lower()

        res = await self.request(
            "PATCH",
            url,
            data=msgspec.json.encode(data),
            params=params,
            headers={"Content-Type": "application/json"},
        )
        return msgspec.json.decode(res, type=player.UpdatePlayerResponse)

    async def destroy_player(
        self: HTTPClient, *, session_id: str, guild_id: str
    ) -> None:
        url = f"/sessions/{session_id}/players/{guild_id}"
        await self.request("DELETE", url)

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

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

from typing import TYPE_CHECKING, cast

from sonolink.gateway.enums import QueueMode
from sonolink.models.filters import Filters
from sonolink.models.settings import AutoPlaySettings, HistorySettings

if TYPE_CHECKING:
    from sonolink.gateway.player import BasePlayer, Player

from ._base import NodeComponent

__all__ = ("PlayerRegistry",)


class PlayerRegistry(NodeComponent):
    """Internal component responsible for managing player registry."""

    def create_player(
        self,
        *,
        volume: int | None = None,
        paused: bool | None = None,
        filters: Filters | None = None,
        queue_mode: QueueMode = QueueMode.NORMAL,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
    ) -> Player:
        client = self.node._ensure_client()
        player_cls = self.node._player_factory.get_player(client.framework)

        player = player_cls(
            node=self.node,
            volume=volume,
            paused=paused,
            filters=filters,
            queue_mode=queue_mode,
            autoplay_settings=autoplay_settings,
            history_settings=history_settings,
        )

        return cast("Player", player)

    def get_player(self, guild_id: int, /) -> BasePlayer | None:
        return self.node._players.get(guild_id)

    def add_player(self, player: BasePlayer) -> None:
        self.node._players[player.guild.id] = player

    def remove_player(self, guild_id: int) -> None:
        self.node._players.pop(guild_id, None)

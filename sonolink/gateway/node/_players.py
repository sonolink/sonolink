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

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

import logging
from typing import Any

import msgspec

from sonolink.gateway.enums import NodeStatus
from sonolink.gateway.event_models import PlayerUpdateEvent, ReadyEvent
from sonolink.gateway.schemas.receive import (
    PlayerUpdateEvent as PlayerUpdatePayload,
    ReadyEvent as ReadyPayload,
)
from sonolink.rest.schemas.info import StatsResponse
from sonolink.rest.schemas.session import UpdateSessionRequest

from ._base import NodeComponent

__all__ = ("EventRouter",)

_log = logging.getLogger(__name__)


class EventRouter(NodeComponent):
    """Internal component responsible for routing node events."""

    async def handle_ready(self, data: dict[str, Any]) -> None:
        payload = msgspec.convert(data, ReadyPayload)
        self.node._resume_session = payload.session_id

        try:
            timeout = int(self.node.resume_timeout)
            update_data = UpdateSessionRequest(
                resuming=timeout > 0, timeout=max(0, timeout)
            )
            await self.node._manager.update_session(
                session_id=self.node._resume_session, data=update_data
            )
            _log.info(
                "Node %r: Session resumption configured (resuming: %s, timeout: %ds).",
                self.node._id,
                timeout > 0,
                timeout,
            )
        except Exception as exc:
            _log.error(
                "Node %r: Failed to configure session resumption: %s",
                self.node._id,
                exc,
            )

        self.node._status = NodeStatus.CONNECTED
        self.node._ready_event.set()

        if self.node._client is None:
            return

        event = ReadyEvent(payload, self.node)
        self.node._client._dispatch("node_ready", event)

    async def handle_player_update(self, data: dict[str, Any]) -> None:
        payload = msgspec.convert(data, PlayerUpdatePayload)

        guild_id = int(payload.guild_id)
        player = self.node.get_player(guild_id)

        if player:
            player._update_state(payload.state)

        if self.node._client is None:
            return

        event = PlayerUpdateEvent(payload, self.node)
        self.node._client._dispatch("player_update", event)

    def handle_stats(self, data: dict[str, Any]) -> None:
        self.node._stats = msgspec.convert(data, StatsResponse)

    async def handle_event(self, data: dict[str, Any]) -> None:
        guild_id = int(data.get("guildId", 0))
        player = self.node.get_player(guild_id)

        if player is None:
            _log.debug(
                "Received event %r for unknown player in guild %s",
                data.get("type"),
                guild_id,
            )
            return

        if self.node._client is None:
            return

        await player._dispatch_event(data)

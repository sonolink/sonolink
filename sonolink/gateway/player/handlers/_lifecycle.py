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
from typing import TYPE_CHECKING, Any, cast

import msgspec

from sonolink.gateway.enums import DisconnectTriggerType
from sonolink.gateway.schemas import PlayerDisconnectEvent
from sonolink.rest.schemas.player import UpdatePlayerRequest, UpdatePlayerTrackRequest
from sonolink.utils.snowflake import Snowflake

from ._base import HandlerBase, _log

if TYPE_CHECKING:
    from sonolink.gateway.node import Node

__all__ = ()


class LifecycleHandler(HandlerBase):
    """Internal handler responsible for the player's connection lifecycle."""

    __slots__ = ()

    async def connect(
        self,
        *,
        timeout: float = 10.0,
        reconnect: bool = True,  # noqa: ARG002  # required by VoiceProtocol
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        channel = self._player.channel
        guild = self._player._guild
        node = self._player._node

        if not guild or not channel:
            raise RuntimeError(
                "Cannot connect without a channel or guild set. "
                "Make sure the player was set to the cls= parameter of Connectable.connect"
            )

        if not node:
            node = self._player._ensure_node()

        self._player._connection._connected_flag.clear()

        await guild.change_voice_state(
            channel=cast(Snowflake, channel),
            self_mute=self_mute,
            self_deaf=self_deaf,
        )

        try:
            async with asyncio.timeout(timeout):
                await self._player._connection._connected_flag.wait()
        except (TimeoutError, asyncio.CancelledError) as exc:
            await self.disconnect(
                force=True,
                trigger=DisconnectTriggerType.ERROR,
                extra_event_data=exc,
            )
            raise ConnectionError(
                f"Connecting to {channel} exceeded the {timeout:.2f} seconds timeout"
            )

    async def disconnect(
        self,
        *,
        force: bool = False,
        trigger: DisconnectTriggerType = DisconnectTriggerType.UNKNOWN,
        extra_event_data: Any = None,
    ) -> None:
        node = self._player._node

        if node is None and not force:
            return

        try:
            if node is None:
                return

            node._remove_player(self._player.guild.id)

            if node._resume_session is None:
                return

            await node._manager.destroy_player(
                session_id=node._resume_session,
                guild_id=str(self._player.guild.id),
            )

            _log.info(
                "Player %s: Disconnected and removed from Node %r.",
                self._player.guild.id,
                node.id,
            )

        except Exception as exc:
            _log.warning(
                "Player %s: Error during disconnect cleanup: %s",
                self._player.guild.id,
                exc,
                exc_info=True,
            )

        finally:
            await self._player.guild.change_voice_state(channel=None)

            self._player.cleanup()
            self._player._queue.reset()
            self._player._connection._connected_flag.clear()

            if node is None or node.client is None:
                return

            event_payload = PlayerDisconnectEvent(
                trigger=trigger,
                extra_data=extra_event_data,
            )
            node.client._dispatch("player_disconnect", self._player, event_payload)

    async def move_to(self, node: Node, /) -> None:
        if self._player._node is node:
            return

        old_node = self._player._node
        self._player._node = node

        if old_node:
            old_node._remove_player(self._player.guild.id)

        node._add_player(self._player)

        await self._player._dispatch_voice_update()
        assert node._resume_session is not None

        track_payload = (
            UpdatePlayerTrackRequest(encoded=self._player.current.encoded)
            if self._player.current
            else msgspec.UNSET
        )
        data = UpdatePlayerRequest(
            track=track_payload,
            position=self._player.position,
            volume=self._player._volume,
            paused=self._player._paused,
            filters=self._player._filters.payload,
        )

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        if old_node is not None and old_node._resume_session is not None:
            try:
                await old_node._manager.destroy_player(
                    session_id=old_node._resume_session,
                    guild_id=str(self._player.guild.id),
                )
            except Exception as exc:
                _log.warning(
                    "Player %s: Failed to destroy player on old node during migration. Error: %s",
                    self._player.guild.id,
                    exc,
                    exc_info=True,
                )

        _log.info(
            "Player %s: Successfully migrated to Node %r.",
            self._player.guild.id,
            node.id,
        )

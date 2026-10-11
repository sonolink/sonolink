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

import asyncio

from sonolink.gateway.enums import DisconnectTriggerType, InactivityMode

from ._base import HandlerBase, _log

__all__ = ()


class InactivityHandler(HandlerBase):
    """Internal handler responsible for monitoring player and voice channel activity."""

    __slots__ = ()

    def _check_inactivity(self) -> None:
        node = self._player._node
        guild = self._player.client.get_guild(self._player.guild.id)

        if (
            node is None
            or guild is None
            or guild.me.voice is None
            or guild.me.voice.channel is None
        ):
            return

        settings = node.inactivity_settings
        whitelist = {u if isinstance(u, int) else u.id for u in settings.user_ids}

        is_active = False
        is_idle = self._player.current is None

        for user_id in guild.me.voice.channel.voice_states:
            if user_id == guild.me.id:
                continue

            if settings.mode == InactivityMode.ONLY_SELF:
                is_active = True
                break

            if settings.mode == InactivityMode.IGNORED_USERS and user_id in whitelist:
                is_active = True
                break

            if settings.mode == InactivityMode.ALL_BOTS:
                member = guild.get_member(user_id)
                if member and not member.bot:
                    is_active = True
                    break

        if not is_active or is_idle:
            self._start_inactivity_timer()
        else:
            self._stop_inactivity_timer()

    def _start_inactivity_timer(self) -> None:
        node = self._player._node

        if node is None or self._player.guild.id in node._waiting_to_disconnect:
            return

        timeout = node.inactivity_settings.timeout
        if timeout is None:
            return

        task = asyncio.create_task(self._inactivity_timeout(timeout))
        task.add_done_callback(
            lambda _: node._waiting_to_disconnect.pop(self._player.guild.id, None)
        )
        node._waiting_to_disconnect[self._player.guild.id] = task
        _log.debug(
            "Player %s: Started inactivity timer for %ds, mode: %s.",
            self._player.guild.id,
            timeout,
            node.inactivity_settings.mode,
        )

    def _stop_inactivity_timer(self) -> None:
        if self._player._node is None:
            return

        task = self._player._node._waiting_to_disconnect.pop(
            self._player.guild.id, None
        )

        if task is None:
            return

        task.cancel()
        _log.debug(
            "Player %s: Activity detected, cancelled timer.", self._player.guild.id
        )

    async def _inactivity_timeout(self, timeout: int) -> None:
        await asyncio.sleep(timeout)
        _log.info("Player %s: Disconnecting due to inactivity.", self._player.guild.id)

        await self._player._lifecycle_handler.disconnect(
            force=True,
            trigger=DisconnectTriggerType.INACTIVITY,
        )

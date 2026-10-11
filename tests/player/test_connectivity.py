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

import pytest

from ..helpers import ConcreteTestPlayer, make_playable


class TestPlayerConnect:
    async def test_connect_requests_voice_state_change(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        async def fake_change_voice_state(**_: object) -> None:
            test_player._connection._connected_flag.set()

        test_player.guild.change_voice_state.side_effect = fake_change_voice_state
        await test_player.connect(timeout=1.0)
        test_player.guild.change_voice_state.assert_awaited_once()

    async def test_connect_without_channel_raises(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        test_player.channel = None
        with pytest.raises(RuntimeError, match="Cannot connect without a channel"):
            await test_player.connect(timeout=1.0)

    async def test_connect_times_out_and_disconnects(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        with pytest.raises(ConnectionError, match="exceeded the"):
            await test_player.connect(timeout=0.01)

        assert test_player.guild.change_voice_state.await_count >= 1


class TestPlayerDisconnect:
    async def test_disconnect_without_node_is_a_no_op(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        test_player._node = None
        await test_player.disconnect()
        test_player.guild.change_voice_state.assert_not_awaited()

    async def test_force_disconnect_resets_voice_state(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        test_player._node = None
        await test_player.disconnect(force=True)
        test_player.guild.change_voice_state.assert_awaited_once_with(channel=None)

    async def test_disconnect_clears_connected_flag(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        test_player._connection._connected_flag.set()
        await test_player.disconnect(force=True)
        assert not test_player._connection._connected_flag.is_set()

    async def test_disconnect_resets_queue(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        test_player.queue.put(make_playable())
        await test_player.disconnect(force=True)
        assert len(test_player.queue) == 0


class TestPlayerConnectionState:
    def test_starts_disconnected(self, test_player: ConcreteTestPlayer) -> None:
        assert not test_player._connection._connected_flag.is_set()

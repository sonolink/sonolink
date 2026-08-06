from __future__ import annotations

from unittest.mock import MagicMock

from ..helpers import ConcreteTestPlayer, make_playable


class TestPlayerSeeking:
    async def test_seek_updates_position(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        await ready_player.play(make_playable())
        await ready_player.seek(30000)
        assert ready_player.position == 30000

    async def test_seek_to_beginning(self, ready_player: ConcreteTestPlayer) -> None:
        await ready_player.play(make_playable())
        await ready_player.seek(0)
        assert ready_player.position == 0

    async def test_seek_notifies_node(
        self, ready_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
    ) -> None:
        await ready_player.play(make_playable())
        await ready_player.seek(90000)
        data = mock_rest_manager.update_player.await_args.kwargs["data"]
        assert data.position == 90000

    async def test_seek_multiple_positions_tracks_latest(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        await ready_player.play(make_playable())
        await ready_player.seek(30000)
        await ready_player.seek(60000)
        await ready_player.seek(90000)
        assert ready_player.position == 90000


class TestPlayerPosition:
    def test_position_starts_at_zero(self, ready_player: ConcreteTestPlayer) -> None:
        assert ready_player.position == 0

    async def test_position_frozen_while_paused(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        await ready_player.play(make_playable(), start=10000, paused=True)
        assert ready_player.position == 10000

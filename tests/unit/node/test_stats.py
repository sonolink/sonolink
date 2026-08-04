from __future__ import annotations

import pytest

from sonolink import Node
from sonolink.rest.schemas.info import FrameStatsObject

from ..helpers import make_stats


class TestNodeStats:
    def test_stats_start_as_none(self, node: Node) -> None:
        assert node.stats is None

    def test_stats_property_has_no_setter(self, node: Node) -> None:
        with pytest.raises(AttributeError):
            node.stats = make_stats()  # pyright: ignore[reportAttributeAccessIssue]

    def test_stats_expose_received_payload(self, node: Node) -> None:
        node._stats = make_stats(players=5, playing_players=3)

        assert node.stats is not None
        assert node.stats.players == 5
        assert node.stats.playing_players == 3

    def test_penalty_is_computed(self, node: Node) -> None:
        node._stats = make_stats(playing_players=10, system_load=0.0)

        assert node.stats is not None
        assert node.stats.penalty == pytest.approx(10.0)

    def test_penalty_grows_with_players(self) -> None:
        light = make_stats(playing_players=1)
        heavy = make_stats(playing_players=50)

        assert light.penalty < heavy.penalty

    def test_penalty_grows_with_cpu_load(self) -> None:
        idle = make_stats(system_load=0.0)
        busy = make_stats(system_load=0.9)

        assert idle.penalty < busy.penalty

    def test_frame_stats_increase_penalty(self) -> None:
        clean = make_stats(playing_players=1)
        lossy = make_stats(
            playing_players=1,
            frame_stats=FrameStatsObject(sent=3000, nulled=300, deficit=100),
        )

        assert lossy.penalty > clean.penalty

    def test_frame_stats_optional(self) -> None:
        assert make_stats().frame_stats is None


class TestNodePenaltyComparison:
    def test_lower_penalty_node_is_preferred(self) -> None:
        assert (
            make_stats(playing_players=1).penalty
            < make_stats(playing_players=100).penalty
        )


class TestNodePlayers:
    def test_node_starts_with_no_players(self, node: Node) -> None:
        assert node._players == {}

    def test_get_player_returns_none_when_absent(self, node: Node) -> None:
        assert node.get_player(123456789) is None

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from sonolink.gateway.enums import AutoPlayMode
from sonolink.gateway.node import Node
from sonolink.models.settings import HistorySettings

from ...helpers import ConcreteTestPlayer


class TestPlayerInitialization:
    def test_player_bound_to_guild(
        self, test_player: ConcreteTestPlayer, mock_guild: MagicMock
    ) -> None:
        assert test_player.guild is mock_guild

    def test_player_bound_to_node(
        self, test_player: ConcreteTestPlayer, node: Node
    ) -> None:
        assert test_player.node is node

    def test_player_starts_with_empty_queue(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        assert len(test_player.queue) == 0

    def test_player_starts_idle(self, test_player: ConcreteTestPlayer) -> None:
        assert test_player.current is None
        assert test_player.is_playing is False
        assert test_player.paused is False

    def test_player_default_volume(self, test_player: ConcreteTestPlayer) -> None:
        assert test_player.volume == 100

    def test_player_custom_volume(self, node: Node) -> None:
        player = ConcreteTestPlayer(node=node, volume=50)
        assert player.volume == 50

    def test_player_can_start_paused(self, node: Node) -> None:
        player = ConcreteTestPlayer(node=node, paused=True)
        assert player.paused is True


class TestPlayerAutoplay:
    def test_autoplay_disabled_by_default(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        assert test_player.autoplay is AutoPlayMode.DISABLED

    def test_autoplay_requires_history(self, node: Node, mock_guild: MagicMock) -> None:
        player = ConcreteTestPlayer(
            node=node, history_settings=HistorySettings(enabled=False)
        )
        player._guild = mock_guild

        with pytest.raises(RuntimeError, match="disabled history"):
            player.autoplay = AutoPlayMode.ENABLED

    def test_autoplay_settable_when_history_enabled(
        self, test_player: ConcreteTestPlayer
    ) -> None:
        test_player.autoplay = AutoPlayMode.ENABLED
        assert test_player.autoplay is AutoPlayMode.ENABLED


class TestPlayerGuildRequired:
    # NOTE: BasePlayer.__init__ never sets self._guild (only __call__ does,
    # once bound to a real voice channel), even though `_guild: Any` is
    # declared as an instance attribute and `guild` promises to raise
    # RuntimeError. Accessing `.guild` before binding therefore raises
    # AttributeError instead. This looks like a genuine library bug in
    # sonolink/gateway/player/_base.py, flagged rather than silently
    # matched here.

    def test_guild_raises_before_binding(self, node: Node) -> None:
        player = ConcreteTestPlayer(node=node)

        with pytest.raises(AttributeError):
            player.guild

    def test_node_raises_when_unbound_and_guild_is_set(
        self, mock_guild: MagicMock
    ) -> None:
        player = ConcreteTestPlayer(node=None)
        player._guild = mock_guild

        with pytest.raises(RuntimeError, match="not attached to a node"):
            player.node

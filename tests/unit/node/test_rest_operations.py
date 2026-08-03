from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sonolink import Node, QueueMode
from sonolink.gateway.player import Player
from sonolink.models import Filters, PlayerInfo, ServerInfo, Timescale
from sonolink.models.settings import AutoPlaySettings, HistorySettings
from sonolink.rest.http import RESTClient
from sonolink.rest.schemas.filters import PlayerFilters
from sonolink.rest.schemas.info import (
    GitObject,
    InfoResponse,
    PluginObject,
    VersionObject,
)
from sonolink.rest.schemas.player import (
    Player as PlayerPayload,
    PlayerState,
    PlayerVoiceState,
)

from ...helpers import ConcreteTestPlayer


def make_player_payload(guild_id: str = "123") -> PlayerPayload:
    return PlayerPayload(
        guild_id=guild_id,
        track=None,
        volume=75,
        paused=False,
        state=PlayerState(time=1000, position=250, connected=True, ping=20),
        voice=PlayerVoiceState(
            token="token",
            endpoint="voice.example.com",
            session_id="voice-session",
            channel_id="456",
        ),
        filters=PlayerFilters(volume=1.0),
    )


@pytest.fixture
def manager(node: Node) -> MagicMock:
    manager = MagicMock(spec=RESTClient)
    manager.lavalink_info = AsyncMock(
        return_value=InfoResponse(
            version=VersionObject(semver="4.2.2", major=4, minor=2, patch=2),
            build_time=1000,
            git=GitObject(branch="main", commit="abc123", commit_time=2000),
            jvm="Java 21",
            lavaplayer="2.2.3",
            source_managers=["youtube"],
            filters=["timescale"],
            plugins=[PluginObject(name="plugin", version="1.0")],
        )
    )
    manager.get_players = AsyncMock(
        return_value=[make_player_payload("123"), make_player_payload("456")]
    )
    manager.get_player = AsyncMock(return_value=make_player_payload())
    manager.destroy_player = AsyncMock()
    manager.request = AsyncMock(return_value=b'{"ok":true}')
    node._manager = manager
    node._resume_session = "session-abc"
    return manager


class TestCreatePlayer:

    def test_create_player_respects_configuration(
        self, node: Node, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def get_test_player(_framework: str) -> type[ConcreteTestPlayer]:
            return ConcreteTestPlayer

        filters = Filters(timescale=Timescale(speed=1.2))
        autoplay = AutoPlaySettings(discovery_count=3)
        history = HistorySettings(enabled=True, max_items=5)
        monkeypatch.setattr(
            node._player_factory, "get_player", get_test_player
        )

        player = node.create_player(
            volume=250,
            paused=True,
            filters=filters,
            queue_mode=QueueMode.LOOP_ALL,
            autoplay_settings=autoplay,
            history_settings=history,
        )

        assert isinstance(player, Player)
        assert player.node is node
        assert player.volume == 250
        assert player.paused is True
        assert player.filters is filters
        assert player.queue_mode is QueueMode.LOOP_ALL
        assert player.autoplay_settings is autoplay
        assert player.history_settings is history
        # Preconfigured players register only after a Discord channel binds them.
        assert node.get_player(123) is None


class TestFetch:

    async def test_fetch_info_returns_server_info(
        self, node: Node, manager: MagicMock
    ) -> None:
        result = await node.fetch_info()

        assert isinstance(result, ServerInfo)
        assert result.version.semver == "4.2.2"
        assert result.jvm == "Java 21"
        assert result.source_managers == ["youtube"]
        manager.lavalink_info.assert_awaited_once_with()

    async def test_fetch_players_returns_player_info_list(
        self, node: Node, manager: MagicMock
    ) -> None:
        result = await node.fetch_players()

        assert all(isinstance(player, PlayerInfo) for player in result)
        assert [player.guild_id for player in result] == [123, 456]
        manager.get_players.assert_awaited_once_with("session-abc")

    async def test_fetch_player_returns_player_info(
        self, node: Node, manager: MagicMock
    ) -> None:
        result = await node.fetch_player(123)

        assert isinstance(result, PlayerInfo)
        assert result.guild_id == 123
        assert result.volume == 75
        manager.get_player.assert_awaited_once_with(
            session_id="session-abc", guild_id="123"
        )

    async def test_disconnect_player_calls_destroy(
        self, node: Node, manager: MagicMock
    ) -> None:
        assert await node.disconnect_player(123) is None
        manager.destroy_player.assert_awaited_once_with(
            session_id="session-abc", guild_id="123"
        )


class TestSend:

    async def test_send_forwards_arguments_and_decodes_json(
        self, node: Node, manager: MagicMock
    ) -> None:
        result = await node.send(
            "POST",
            "plugins/example",
            headers={"X-Test": "yes"},
            params={"page": "1"},
            json={"enabled": True},
            data=b"body",
        )

        assert result == {"ok": True}
        manager.request.assert_awaited_once_with(
            method="POST",
            url="plugins/example",
            data=b"body",
            params={"page": "1"},
            json={"enabled": True},
            headers={"X-Test": "yes"},
        )

    @pytest.mark.parametrize(
        ("response", "expected"),
        [(b"plain text", "plain text"), (b"\xff", b"\xff"), (None, None)],
    )
    async def test_send_passes_through_response_shapes(
        self,
        node: Node,
        manager: MagicMock,
        response: bytes | None,
        expected: str | bytes | None,
    ) -> None:
        manager.request = AsyncMock(return_value=response)

        assert await node.send("GET", "stats") == expected


class TestCleanup:

    async def test_cleanup_is_noop(self, node: Node) -> None:
        assert await node.cleanup() is None

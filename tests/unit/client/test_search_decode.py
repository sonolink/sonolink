from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sonolink import Client, Node
from sonolink.models import SearchResult
from sonolink.models.track import Playable

from ...helpers import make_playable


@pytest.fixture
def client(mock_discord_client: MagicMock) -> Client[MagicMock]:
    with patch(
        "sonolink.gateway.client._factory.ClientFactory.create",
        return_value=MagicMock(),
    ):
        with patch(
            "sonolink.gateway.player.PlayerFactory.detect_framework",
            return_value="discord.py",
        ):
            return Client(mock_discord_client)


class TestClientSearch:
    async def test_search_track_default_source(self, client: Client[MagicMock]) -> None:
        mock_node = MagicMock(spec=Node)
        mock_result = MagicMock(spec=SearchResult)
        mock_node.search_track = AsyncMock(return_value=mock_result)

        with patch.object(client, "get_best_node", return_value=mock_node):
            result = await client.search_track("Never Gonna Give You Up")

            mock_node.search_track.assert_called_once()
            assert result is mock_result

    async def test_search_track_custom_source(self, client: Client[MagicMock]) -> None:
        mock_node = MagicMock(spec=Node)
        mock_node.search_track = AsyncMock()

        with patch.object(client, "get_best_node", return_value=mock_node):
            await client.search_track("query", source="soundcloud")

            mock_node.search_track.assert_called_once_with("query", source="soundcloud")

    async def test_search_track_with_region(self, client: Client[MagicMock]) -> None:
        mock_node = MagicMock(spec=Node)
        mock_node.search_track = AsyncMock()

        with patch.object(client, "get_best_node", return_value=mock_node) as mock_best:
            await client.search_track("query", region="us-east")

            mock_best.assert_called_once_with(region="us-east")


class TestClientDecode:
    async def test_decode_track(self, client: Client[MagicMock]) -> None:
        mock_node = MagicMock(spec=Node)
        playable = make_playable()
        mock_node.decode_track = AsyncMock(return_value=playable)

        with patch.object(client, "get_best_node", return_value=mock_node):
            result = await client.decode_track("encoded_data_123")

            mock_node.decode_track.assert_called_once_with("encoded_data_123")
            assert result is playable

    async def test_decode_tracks_multiple(self, client: Client[MagicMock]) -> None:
        mock_node = MagicMock(spec=Node)
        playables: list[Playable] = [
            make_playable(identifier="a"),
            make_playable(identifier="b"),
        ]
        mock_node.decode_tracks = AsyncMock(return_value=playables)

        with patch.object(client, "get_best_node", return_value=mock_node):
            result = await client.decode_tracks("track1", "track2")

            mock_node.decode_tracks.assert_called_once_with("track1", "track2")
            assert result == playables

    async def test_decode_track_with_region(self, client: Client[MagicMock]) -> None:
        mock_node = MagicMock(spec=Node)
        mock_node.decode_track = AsyncMock()

        with patch.object(client, "get_best_node", return_value=mock_node) as mock_best:
            await client.decode_track("encoded", region="eu-west")

            mock_best.assert_called_once_with(region="eu-west")


class TestClientNodeSelection:
    @pytest.fixture
    def client_with_nodes(self, client: Client[MagicMock]) -> Client[MagicMock]:
        node1 = MagicMock(spec=Node)
        node1.id = "node1"
        node1.is_connected = True
        node1.stats = MagicMock(penalty=10)
        node1.regions = []
        client._nodes[node1.id] = node1

        node2 = MagicMock(spec=Node)
        node2.id = "node2"
        node2.is_connected = True
        node2.stats = MagicMock(penalty=5)
        node2.regions = []
        client._nodes[node2.id] = node2

        return client

    def test_get_best_node_selects_lowest_penalty(
        self, client_with_nodes: Client[MagicMock]
    ) -> None:
        assert client_with_nodes.get_best_node().id == "node2"

    def test_get_best_node_with_region(
        self, client_with_nodes: Client[MagicMock]
    ) -> None:
        node_us = MagicMock(spec=Node)
        node_us.id = "node_us"
        node_us.is_connected = True
        node_us.stats = MagicMock(penalty=100)
        node_us.regions = ["us-east"]
        client_with_nodes._nodes[node_us.id] = node_us

        best = client_with_nodes.get_best_node(region="us-east")
        assert best.id == "node_us"

    def test_get_best_node_region_fallback(
        self, client_with_nodes: Client[MagicMock]
    ) -> None:
        best = client_with_nodes.get_best_node(region="non-existent")
        assert best.id == "node2"  # Falls back to lowest penalty

    def test_get_best_node_no_connected_nodes_raises(
        self, client: Client[MagicMock]
    ) -> None:
        node = MagicMock(spec=Node)
        node.id = "node1"
        node.is_connected = False
        client._nodes[node.id] = node

        with pytest.raises(RuntimeError, match="No nodes are currently connected"):
            client.get_best_node()

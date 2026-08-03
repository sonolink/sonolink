from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import msgspec
import pytest

from sonolink import Client
from sonolink.gateway.client._base import DiscordClient
from sonolink.gateway.node import Node
from sonolink.models.responses import SearchResult
from sonolink.rest.enums import TrackLoadResult
from sonolink.rest.schemas.track import Track, TrackInfo, TrackLoadingResponse


@pytest.fixture
def mock_discord_client() -> DiscordClient[Any]:
    client = Mock(spec=DiscordClient)
    client.user = Mock(id=123456789, name="TestBot")
    client.latency = 0.05
    return client


@pytest.fixture
def sonolink_client(mock_discord_client: DiscordClient[Any]) -> Client[Any]:
    with patch(
        "sonolink.gateway.client._factory.ClientFactory.create", return_value=Mock()
    ):
        with patch(
            "sonolink.gateway.player.PlayerFactory.detect_framework",
            return_value="discord.py",
        ):
            return Client(mock_discord_client)


@pytest.fixture
def multi_node_setup(sonolink_client: Client[Any]) -> tuple[Client[Any], list[Node]]:
    node1 = sonolink_client.create_node(
        uri="ws://localhost:2333", password="pass", id="node-1"
    )
    node2 = sonolink_client.create_node(
        uri="ws://localhost:2334", password="pass", id="node-2"
    )
    return sonolink_client, [node1, node2]


@pytest.fixture
def mock_search_result() -> SearchResult:
    # SearchResult.result depends on .type: TRACK/PLAYLIST/SEARCH resolve to a
    # Playable, a Playlist, or a list[Playable] respectively.
    tracks = [
        Track(
            encoded=f"encoded::{i}",
            info=TrackInfo(
                identifier=str(i),
                uri=f"https://www.youtube.com/watch?v=test{i}",
                title=f"Track {i}",
                author=f"Artist {i}",
                length=180000,
                position=0,
                is_seekable=True,
                is_stream=False,
                source_name="youtube",
            ),
            plugin_info=None,
            user_data=None,
        )
        for i in range(5)
    ]
    response = TrackLoadingResponse(
        load_type=TrackLoadResult.SEARCH,
        data=msgspec.to_builtins(tracks),
    )
    return SearchResult(client=Mock(), data=response)

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import msgspec
import pytest

from sonolink import Client, Queue
from sonolink.gateway.enums import NodeStatus
from sonolink.gateway.node import Node
from sonolink.models import SearchResult
from sonolink.models.settings import InactivitySettings
from sonolink.models.track import Playable
from sonolink.rest.enums import TrackLoadResult
from sonolink.rest.http import RESTClient
from sonolink.rest.schemas.track import TrackLoadingResponse

from .helpers import ConcreteTestPlayer, make_playable


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        path_parts = item.path.parts
        for component in ("client", "node", "player", "queue"):
            if component in path_parts:
                item.add_marker(getattr(pytest.mark, component))
        if "search" in item.path.name:
            item.add_marker(pytest.mark.search)


@pytest.fixture(name="make_playable")
def make_playable_fixture() -> Callable[..., Playable]:
    return make_playable


@pytest.fixture
def mock_guild() -> MagicMock:
    guild = MagicMock()
    guild.id = 987654321
    guild.name = "Test Guild"
    guild.change_voice_state = AsyncMock()
    return guild


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock(spec=Client)
    client.framework = "py-cord"
    return client


@pytest.fixture
def mock_discord_client() -> MagicMock:
    client = MagicMock()
    client.user = MagicMock(id=123456789, name="TestBot")
    return client


@pytest.fixture
def node(mock_client: MagicMock) -> Node:
    return Node(
        client=mock_client,
        uri="http://localhost:2333",
        password="youshallnotpass",
        id="test-node",
        inactivity_settings=InactivitySettings.default(),
    )


@pytest.fixture
def mock_rest_manager() -> MagicMock:
    manager = MagicMock(spec=RESTClient)
    manager.update_player = AsyncMock()
    manager.destroy_player = AsyncMock()
    manager.update_headers = MagicMock()
    return manager


@pytest.fixture
def test_player(node: Node, mock_guild: MagicMock) -> ConcreteTestPlayer:
    player = ConcreteTestPlayer(node=node)
    player._guild = mock_guild
    player.client = MagicMock()
    player.channel = MagicMock(guild=mock_guild)
    return player


@pytest.fixture
def ready_player(
    test_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
) -> ConcreteTestPlayer:
    node = test_player.node
    node._resume_session = "session-abc"
    node._status = NodeStatus.CONNECTED
    node._manager = mock_rest_manager
    return test_player


@pytest.fixture
def track() -> Playable:
    return make_playable()


@pytest.fixture
def tracks() -> list[Playable]:
    return [
        make_playable(
            identifier=f"track-{i}",
            title=f"Track {i + 1}",
            author=f"Artist {i + 1}",
            length=120000 + (i * 30000),
        )
        for i in range(5)
    ]


@pytest.fixture
def empty_queue() -> Queue:
    return Queue()


@pytest.fixture
def queue_with_tracks(tracks: list[Playable]) -> Queue:
    queue = Queue()
    queue.put(tracks)
    return queue


@pytest.fixture
def client(mock_discord_client: MagicMock) -> Client[MagicMock]:
    with patch(
        "sonolink.gateway.client._factory.ClientFactory.create",
        return_value=MagicMock(),
    ):
        with patch(
            "sonolink.gateway.player.PlayerFactory.detect_framework",
            return_value="py-cord",
        ):
            return Client(mock_discord_client)


@pytest.fixture
def track_payload() -> Callable[..., dict[str, Any]]:
    def _track_payload(**kwargs: Any) -> dict[str, Any]:
        return msgspec.to_builtins(make_playable(**kwargs).data)

    return _track_payload


@pytest.fixture
def make_search_result() -> Callable[..., SearchResult]:
    def _make_search_result(
        load_type: TrackLoadResult,
        data: Any,
        *,
        client: MagicMock | None = None,
    ) -> SearchResult:
        response = TrackLoadingResponse(load_type=load_type, data=data)
        return SearchResult(client=client or MagicMock(), data=response)

    return _make_search_result

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import AsyncMock, MagicMock

import pytest

from sonolink import Client
from sonolink.gateway.enums import NodeStatus
from sonolink.gateway.node import Node
from sonolink.models.settings import InactivitySettings
from sonolink.models.track import Playable
from sonolink.rest.http import RESTClient

from .helpers import ConcreteTestPlayer, make_playable


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        path_parts = item.path.parts
        filename = item.path.name

        if "unit" in path_parts:
            item.add_marker(pytest.mark.unit)
        if "integration" in path_parts:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)

        for component in ("client", "node", "player", "queue"):
            if component in path_parts:
                item.add_marker(getattr(pytest.mark, component))

        if "search" in filename:
            item.add_marker(pytest.mark.search)
        if "errors" in path_parts:
            item.add_marker(pytest.mark.error)
        if "framework" in filename:
            item.add_marker(pytest.mark.framework)


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
    client.framework = "discord.py"
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
def test_player(node: Node, mock_guild: MagicMock) -> ConcreteTestPlayer:
    player = ConcreteTestPlayer(node=node)
    player._guild = mock_guild
    player.client = MagicMock()
    player.channel = MagicMock(guild=mock_guild)
    return player


@pytest.fixture
def mock_rest_manager() -> MagicMock:
    manager = MagicMock(spec=RESTClient)
    manager.update_player = AsyncMock()
    manager.destroy_player = AsyncMock()
    manager.update_headers = MagicMock()
    return manager


@pytest.fixture
def ready_player(
    test_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
) -> ConcreteTestPlayer:
    node = test_player.node
    node._resume_session = "session-abc"
    node._status = NodeStatus.CONNECTED
    node._manager = mock_rest_manager
    return test_player

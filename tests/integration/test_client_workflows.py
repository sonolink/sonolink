from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from sonolink import Client, Node
from sonolink.gateway.enums import NodeStatus


class TestClientFullLifecycle:

    @pytest.fixture
    def client(self) -> Client[Any]:
        mock_discord_client = MagicMock()
        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock()
        ):
            with patch(
                "sonolink.gateway.player.PlayerFactory.detect_framework",
                return_value="discord.py"
            ):
                return Client(mock_discord_client)

    async def test_full_player_lifecycle(self, client: Client[Any]) -> None:
        # 1. Create node
        node = client.create_node(
            uri="ws://localhost:2333",
            password="test"
        )
        assert node in client.nodes

        # 2. Connect to node (bypassing the real websocket handshake, since
        # this test only cares about client/node bookkeeping)
        node._status = NodeStatus.CONNECTED

        # 3. Start client (should skip the already-connected node)
        await client.start()

        # 4. Get best node
        best_node = client.get_best_node()
        assert best_node is node

    def test_multi_node_setup(self, client: Client[Any]) -> None:
        node1 = client.create_node(uri="ws://localhost:2333", password="pass")
        node2 = client.create_node(uri="ws://localhost:2334", password="pass")

        assert len(client.nodes) == 2
        assert client.get_node(node1.id) is node1
        assert client.get_node(node2.id) is node2

    def test_node_failover(self, client: Client[Any]) -> None:
        node1 = MagicMock(spec=Node)
        node1.id = "node1"
        node1.is_connected = True
        node1.stats = MagicMock(penalty=100)  # High penalty
        node1.regions = []

        node2 = MagicMock(spec=Node)
        node2.id = "node2"
        node2.is_connected = True
        node2.stats = MagicMock(penalty=10)  # Low penalty
        node2.regions = []

        client._nodes[node1.id] = node1
        client._nodes[node2.id] = node2

        # Should select node2 (lower penalty)
        best = client.get_best_node()
        assert best.id == "node2"

    def test_node_region_affinity(self, client: Client[Any]) -> None:
        node_us = MagicMock(spec=Node)
        node_us.id = "node_us"
        node_us.is_connected = True
        node_us.stats = MagicMock(penalty=50)
        node_us.regions = ["us-east"]

        node_eu = MagicMock(spec=Node)
        node_eu.id = "node_eu"
        node_eu.is_connected = True
        node_eu.stats = MagicMock(penalty=10)
        node_eu.regions = ["eu-west"]

        client._nodes[node_us.id] = node_us
        client._nodes[node_eu.id] = node_eu

        # Should select US node when requesting US region
        best = client.get_best_node(region="us-east")
        assert best.id == "node_us"

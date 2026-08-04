from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from sonolink import Client
from sonolink.gateway.enums import NodeRegion
from sonolink.models.settings import CacheSettings, InactivitySettings


class TestCreateNode:
    def test_create_node_with_uri(self, client: Client[MagicMock]) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")

        assert node.id
        assert node in client.nodes

    def test_create_node_with_host_and_port(self, client: Client[MagicMock]) -> None:
        node = client.create_node(
            host="localhost", port=2333, password="youshallnotpass"
        )

        assert node in client.nodes

    def test_create_node_with_custom_id(self, client: Client[MagicMock]) -> None:
        node = client.create_node(
            uri="ws://localhost:2333", password="youshallnotpass", id="primary-us-node"
        )

        assert node.id == "primary-us-node"

    def test_create_node_with_cache_settings(self, client: Client[MagicMock]) -> None:
        cache_settings = CacheSettings(enabled=True, max_items=1000)
        node = client.create_node(
            uri="ws://localhost:2333",
            password="youshallnotpass",
            cache_settings=cache_settings,
        )

        assert node._cache is not None

    def test_create_node_with_inactivity_settings(
        self, client: Client[MagicMock]
    ) -> None:
        inactivity_settings = InactivitySettings(timeout=300)
        node = client.create_node(
            uri="ws://localhost:2333",
            password="youshallnotpass",
            inactivity_settings=inactivity_settings,
        )

        assert node.inactivity_settings is inactivity_settings

    def test_create_node_with_regions(self, client: Client[MagicMock]) -> None:
        node = client.create_node(
            uri="ws://localhost:2333",
            password="youshallnotpass",
            regions=["us-east", NodeRegion.US_CENTRAL],
        )

        assert node.regions == ["us-east", NodeRegion.US_CENTRAL]

    def test_create_node_uri_and_host_port_conflict(
        self, client: Client[MagicMock]
    ) -> None:
        with pytest.raises(ValueError, match="Cannot specify both uri and host/port"):
            client.create_node(  # pyright: ignore[reportCallIssue]
                uri="ws://localhost:2333",
                host="localhost",
                port=2333,
                password="youshallnotpass",
            )

    def test_create_node_missing_host_or_port(self, client: Client[MagicMock]) -> None:
        with pytest.raises(
            ValueError, match="Must specify either uri or host and port"
        ):
            client.create_node(  # pyright: ignore[reportCallIssue]
                host="localhost", password="youshallnotpass"
            )


class TestGetRemoveNode:
    def test_get_node_existing(self, client: Client[MagicMock]) -> None:
        node = client.create_node(
            uri="ws://localhost:2333", password="youshallnotpass", id="test-node"
        )

        assert client.get_node("test-node") is node

    def test_get_node_nonexistent(self, client: Client[MagicMock]) -> None:
        assert client.get_node("nonexistent") is None

    async def test_remove_node(self, client: Client[MagicMock]) -> None:
        client.create_node(
            uri="ws://localhost:2333", password="youshallnotpass", id="remove-me"
        )

        client.remove_node("remove-me")
        assert client.get_node("remove-me") is None

    def test_remove_nonexistent_node(self, client: Client[MagicMock]) -> None:
        client.remove_node("nonexistent")

    async def test_clear_nodes(self, client: Client[MagicMock]) -> None:
        client.create_node(uri="ws://localhost:2333", password="pass")
        client.create_node(uri="ws://localhost:2334", password="pass")

        assert len(client.nodes) == 2
        client.clear_nodes()
        assert len(client.nodes) == 0

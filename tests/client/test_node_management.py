from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from sonolink import Client
from sonolink.gateway.node import Node
from sonolink.models.settings import CacheSettings


def make_node(client: Client[MagicMock], **kwargs: Any) -> Node:
    return client.create_node(
        uri="ws://localhost:2333",
        password="youshallnotpass",
        **kwargs,
    )


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

    def test_create_node_with_cache_settings(self, client: Client[MagicMock]) -> None:
        cache_settings = CacheSettings(enabled=True, max_items=1000)
        node = make_node(client, cache_settings=cache_settings)

        assert node._cache is not None

    def test_create_node_uri_and_host_port_conflict(
        self, client: Client[MagicMock]
    ) -> None:
        with pytest.raises(ValueError, match="Cannot specify both uri and host/port"):
            cast(Any, client.create_node)(
                uri="ws://localhost:2333",
                host="localhost",
                port=2333,
                password="youshallnotpass",
            )

    def test_create_node_missing_host_or_port(self, client: Client[MagicMock]) -> None:
        with pytest.raises(
            ValueError, match="Must specify either uri or host and port"
        ):
            cast(Any, client.create_node)(host="localhost", password="youshallnotpass")


class TestGetRemoveNode:
    def test_get_node_existing(self, client: Client[MagicMock]) -> None:
        node = make_node(client, id="test-node")

        assert client.get_node("test-node") is node

    def test_get_node_nonexistent(self, client: Client[MagicMock]) -> None:
        assert client.get_node("nonexistent") is None

    async def test_remove_node(self, client: Client[MagicMock]) -> None:
        make_node(client, id="remove-me")

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

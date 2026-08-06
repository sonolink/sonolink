from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sonolink import Client
from sonolink.gateway.enums import NodeStatus


class TestClientStart:
    async def test_start_with_no_nodes(self, client: Client[MagicMock]) -> None:
        await client.start()

    @pytest.mark.parametrize(
        ("status", "expected_calls"),
        [(NodeStatus.DISCONNECTED, 1), (NodeStatus.CONNECTED, 0)],
    )
    async def test_start_connects_only_disconnected_nodes(
        self,
        client: Client[MagicMock],
        status: NodeStatus,
        expected_calls: int,
    ) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.connect = AsyncMock()
        node._status = status

        await client.start()
        assert node.connect.await_count == expected_calls


class TestClientClose:
    @pytest.mark.parametrize(
        ("status", "expected_calls"),
        [(NodeStatus.CONNECTED, 1), (NodeStatus.DISCONNECTED, 0)],
    )
    async def test_close_disconnects_only_connected_nodes(
        self,
        client: Client[MagicMock],
        status: NodeStatus,
        expected_calls: int,
    ) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.close = AsyncMock()
        node._status = status

        await client.close()
        assert node.close.await_count == expected_calls

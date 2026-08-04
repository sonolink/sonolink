from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from sonolink import Client
from sonolink.gateway.enums import NodeStatus


class TestClientStart:
    async def test_start_with_no_nodes(self, client: Client[MagicMock]) -> None:
        await client.start()

    async def test_start_connects_nodes(self, client: Client[MagicMock]) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.connect = AsyncMock()
        node._status = NodeStatus.DISCONNECTED

        await client.start()
        node.connect.assert_called_once()

    async def test_start_skips_already_connected(
        self, client: Client[MagicMock]
    ) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.connect = AsyncMock()
        node._status = NodeStatus.CONNECTED

        await client.start()
        node.connect.assert_not_called()


class TestClientClose:
    async def test_close_disconnects_nodes(self, client: Client[MagicMock]) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.close = AsyncMock()
        node._status = NodeStatus.CONNECTED

        await client.close()
        node.close.assert_called_once()

    async def test_close_skips_disconnected_nodes(
        self, client: Client[MagicMock]
    ) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.close = AsyncMock()
        node._status = NodeStatus.DISCONNECTED

        await client.close()
        node.close.assert_not_called()

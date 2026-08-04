from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sonolink import Client
from sonolink.gateway.enums import NodeStatus


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


class TestClientStart:
    async def test_start_with_no_nodes(self, client: Client[MagicMock]) -> None:
        await client.start()  # Should not raise

    async def test_start_connects_nodes(self, client: Client[MagicMock]) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.connect = AsyncMock()  # pyright: ignore[reportAttributeAccessIssue]
        node._status = NodeStatus.DISCONNECTED

        await client.start()
        node.connect.assert_called_once()  # pyright: ignore[reportAttributeAccessIssue]

    async def test_start_skips_already_connected(
        self, client: Client[MagicMock]
    ) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.connect = AsyncMock()  # pyright: ignore[reportAttributeAccessIssue]
        node._status = NodeStatus.CONNECTED

        await client.start()
        node.connect.assert_not_called()  # pyright: ignore[reportAttributeAccessIssue]


class TestClientClose:
    async def test_close_disconnects_nodes(self, client: Client[MagicMock]) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.close = AsyncMock()  # pyright: ignore[reportAttributeAccessIssue]
        node._status = NodeStatus.CONNECTED

        await client.close()
        node.close.assert_called_once()  # pyright: ignore[reportAttributeAccessIssue]

    async def test_close_skips_disconnected_nodes(
        self, client: Client[MagicMock]
    ) -> None:
        node = client.create_node(uri="ws://localhost:2333", password="youshallnotpass")
        node.close = AsyncMock()  # pyright: ignore[reportAttributeAccessIssue]
        node._status = NodeStatus.DISCONNECTED

        await client.close()
        node.close.assert_not_called()  # pyright: ignore[reportAttributeAccessIssue]

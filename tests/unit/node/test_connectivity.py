from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sonolink import Node
from sonolink.gateway.enums import NodeStatus
from sonolink.rest.http import RESTClient


@pytest.fixture
def manager() -> MagicMock:
    manager = MagicMock(spec=RESTClient)
    manager.setup = AsyncMock()
    manager.close = AsyncMock()
    manager.is_closed = False
    return manager


@pytest.fixture
def connectable(node: Node, manager: MagicMock) -> Node:
    node._manager = manager
    node._connection.attempt_connect = AsyncMock()  # pyright: ignore[reportAttributeAccessIssue]
    return node


class TestNodeConnectionState:

    def test_starts_disconnected(self, node: Node) -> None:
        assert node._status is NodeStatus.DISCONNECTED
        assert node.is_connected is False
        assert node.is_connecting is False

    def test_is_connected_tracks_status(self, node: Node) -> None:
        node._status = NodeStatus.CONNECTED

        assert node.is_connected is True
        assert node.is_connecting is False

    def test_is_connecting_tracks_status(self, node: Node) -> None:
        node._status = NodeStatus.CONNECTING

        assert node.is_connecting is True
        assert node.is_connected is False

    def test_session_id_raises_when_disconnected(self, node: Node) -> None:
        with pytest.raises(RuntimeError, match="no session ID"):
            node.session_id

    def test_session_id_returns_resume_session(self, node: Node) -> None:
        node._resume_session = "session-abc"

        assert node.session_id == "session-abc"


class TestNodeConnect:

    async def test_connect_sets_up_manager(
        self, connectable: Node, manager: MagicMock
    ) -> None:
        await connectable.connect()

        manager.setup.assert_awaited_once()

    async def test_connect_without_client_raises(self, connectable: Node) -> None:
        connectable._client = None

        with pytest.raises(RuntimeError, match="not bound to a client"):
            await connectable.connect()

    async def test_connect_is_ignored_when_already_alive(
        self, connectable: Node, manager: MagicMock
    ) -> None:
        connectable._keep_alive = MagicMock()

        await connectable.connect()

        manager.setup.assert_not_awaited()


class TestNodeClose:

    async def test_close_without_client_raises(self, connectable: Node) -> None:
        connectable._client = None

        with pytest.raises(RuntimeError, match="not bound to a client"):
            await connectable.close()

    async def test_close_when_never_connected_raises(self, connectable: Node) -> None:
        with pytest.raises(RuntimeError, match="not connected yet"):
            await connectable.close()

    async def test_close_resets_state(self, connectable: Node) -> None:
        connectable._status = NodeStatus.CONNECTED
        connectable._resume_session = "session-abc"

        await connectable.close()

        assert connectable._status is NodeStatus.DISCONNECTED
        assert connectable._resume_session is None
        assert connectable._ws is None
        assert connectable._keep_alive is None

    async def test_close_dispatches_event(
        self, connectable: Node, mock_client: MagicMock
    ) -> None:
        connectable._status = NodeStatus.CONNECTED

        await connectable.close()

        mock_client._dispatch.assert_called_once_with("node_close", connectable)


class TestNodeReconnect:

    async def test_reconnect_without_client_raises(self, connectable: Node) -> None:
        connectable._client = None

        with pytest.raises(RuntimeError, match="not bound to a client"):
            await connectable.reconnect()

    async def test_reconnect_twice_raises(self, connectable: Node) -> None:
        connectable._is_reconnecting = True

        with pytest.raises(RuntimeError, match="already reconnecting"):
            await connectable.reconnect()

    async def test_reconnect_marks_connecting(self, connectable: Node) -> None:
        await connectable.reconnect()

        assert connectable._is_reconnecting is True

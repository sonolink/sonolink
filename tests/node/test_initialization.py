from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from sonolink import Node
from sonolink.gateway.enums import NodeRegion, NodeStatus
from sonolink.models.settings import CacheSettings, InactivitySettings


def build_node(client: MagicMock, **kwargs: Any) -> Node:
    params: dict[str, Any] = {
        "client": client,
        "uri": "ws://localhost:2333",
        "password": "youshallnotpass",
        "inactivity_settings": InactivitySettings.default(),
    }
    params.update(kwargs)
    return Node(**params)


class TestNodeInitialization:
    def test_node_generates_id_when_omitted(self, mock_client: MagicMock) -> None:
        first = build_node(mock_client)
        second = build_node(mock_client)

        assert first.id != second.id

    def test_node_strips_trailing_slash_from_uri(self, mock_client: MagicMock) -> None:
        node = build_node(mock_client, uri="ws://localhost:2333/")
        assert node.uri == "ws://localhost:2333"

    def test_node_starts_disconnected(self, mock_client: MagicMock) -> None:
        node = build_node(mock_client)

        assert node.is_connected is False
        assert node.is_connecting is False
        assert node._status is NodeStatus.DISCONNECTED

    def test_node_starts_with_no_stats(self, mock_client: MagicMock) -> None:
        assert build_node(mock_client).stats is None


class TestNodeSettings:
    def test_inactivity_settings_is_required(self, mock_client: MagicMock) -> None:
        with pytest.raises(TypeError):
            cast(Callable[..., Node], Node)(
                client=mock_client,
                uri="ws://localhost:2333",
                password="youshallnotpass",
            )

    def test_cache_settings_are_applied(self, mock_client: MagicMock) -> None:
        node = build_node(
            mock_client,
            cache_settings=CacheSettings(enabled=True, max_items=500),
        )

        assert node._cache is not None


class TestNodeRegions:
    def test_regions_strip_vip_prefix(self, mock_client: MagicMock) -> None:
        node = build_node(mock_client, regions=["vip-us-east"])
        assert node.regions == ["us-east"]

    def test_regions_accept_enum_members(self, mock_client: MagicMock) -> None:
        node = build_node(mock_client, regions=[NodeRegion.US_CENTRAL])
        assert NodeRegion.US_CENTRAL in node.regions


class TestNodeIdMutation:
    def test_id_cannot_change_while_bound_to_client(
        self, mock_client: MagicMock
    ) -> None:
        node = build_node(mock_client, id="bound")

        with pytest.raises(RuntimeError, match="bound to a client"):
            node.id = "renamed"

    def test_uri_cannot_change_while_connected(self, mock_client: MagicMock) -> None:
        node = build_node(mock_client)
        node._status = NodeStatus.CONNECTED

        with pytest.raises(RuntimeError, match="while it is connected"):
            node.uri = "ws://elsewhere:2333"

    def test_uri_can_change_while_disconnected(self, mock_client: MagicMock) -> None:
        node = build_node(mock_client)
        node.uri = "ws://elsewhere:2333"

        assert node.uri == "ws://elsewhere:2333"

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sonolink import Node
from sonolink.models import SearchResult
from sonolink.models.track import Playable
from sonolink.rest.enums import TrackLoadResult
from sonolink.rest.http import RESTClient
from sonolink.rest.schemas.track import TrackLoadingResponse

from ...helpers import make_playable


@pytest.fixture
def manager(node: Node) -> MagicMock:
    manager = MagicMock(spec=RESTClient)
    manager.load_track = AsyncMock(
        return_value=TrackLoadingResponse(
            load_type=TrackLoadResult.EMPTY,
            data=None,
        )
    )
    manager.decode_track = AsyncMock(return_value=make_playable().data)
    manager.decode_tracks = AsyncMock(
        return_value=[
            make_playable(identifier="a").data,
            make_playable(identifier="b").data,
        ]
    )
    node._manager = manager
    return manager


class TestNodeSearch:
    async def test_search_track_returns_search_result(
        self, node: Node, manager: MagicMock
    ) -> None:
        result = await node.search_track("query")

        assert isinstance(result, SearchResult)
        manager.load_track.assert_awaited_once_with("query")

    async def test_search_prefixes_source(self, node: Node, manager: MagicMock) -> None:
        await node.search_track("query", source="spotify")

        manager.load_track.assert_awaited_once_with("spotify:query")

    async def test_search_does_not_prefix_urls(
        self, node: Node, manager: MagicMock
    ) -> None:
        await node.search_track("https://example.com/track", source="spotify")

        manager.load_track.assert_awaited_once_with("https://example.com/track")

    async def test_search_strips_trailing_colon_from_source(
        self, node: Node, manager: MagicMock
    ) -> None:
        await node.search_track("query", source="ytsearch:")

        manager.load_track.assert_awaited_once_with("ytsearch:query")

    async def test_repeated_search_is_cached(
        self, node: Node, manager: MagicMock
    ) -> None:
        first = await node.search_track("query")
        second = await node.search_track("query")

        assert first is second
        manager.load_track.assert_awaited_once()

    async def test_different_queries_are_not_cached_together(
        self, node: Node, manager: MagicMock
    ) -> None:
        await node.search_track("one")
        await node.search_track("two")

        assert manager.load_track.await_count == 2


class TestNodeDecode:
    async def test_decode_track_returns_playable(
        self, node: Node, manager: MagicMock
    ) -> None:
        result = await node.decode_track("encoded_123")

        assert isinstance(result, Playable)
        assert result.title == "Test Track"
        manager.decode_track.assert_awaited_once_with("encoded_123")

    async def test_decode_tracks_returns_playables(
        self, node: Node, manager: MagicMock
    ) -> None:
        result = await node.decode_tracks("e1", "e2")

        assert [track.identifier for track in result] == ["a", "b"]
        manager.decode_tracks.assert_awaited_once_with(["e1", "e2"])

    async def test_decode_tracks_empty(self, node: Node, manager: MagicMock) -> None:
        manager.decode_tracks = AsyncMock(return_value=[])

        assert await node.decode_tracks() == []


class TestNodeRequiresClient:
    async def test_search_without_client_raises(self, node: Node) -> None:
        node._client = None

        with pytest.raises(RuntimeError, match="without an attached client"):
            await node.search_track("query")

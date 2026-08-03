from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import msgspec
import pytest

from sonolink import Client
from sonolink.models import SearchResult
from sonolink.models.track import Playable
from sonolink.rest.enums import TrackLoadResult
from sonolink.rest.schemas.track import Track, TrackInfo, TrackLoadingResponse


def make_playable(
    *,
    identifier: str = "test-id",
    title: str = "Test Track",
    length: int = 180000,
    client: Any = None,
) -> Playable:
    info = TrackInfo(
        identifier=identifier,
        uri="https://example.com/watch?v=test",
        title=title,
        author="Test Artist",
        length=length,
        position=0,
        is_seekable=True,
        is_stream=False,
        source_name="youtube",
    )
    data = Track(
        encoded=f"encoded::{identifier}", info=info, plugin_info=None, user_data=None
    )
    return Playable(client=client, data=data)


def track_payload(**kwargs: Any) -> dict[str, Any]:
    return msgspec.to_builtins(make_playable(**kwargs).data)


def make_search_result(
    load_type: TrackLoadResult, data: Any, *, client: MagicMock
) -> SearchResult:
    response = TrackLoadingResponse(load_type=load_type, data=data)
    return SearchResult(client=client, data=response)


class TestSearchPlaySequence:
    @pytest.fixture
    def client(self) -> Client[Any]:
        mock_discord_client = MagicMock()
        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock(),
        ):
            with patch(
                "sonolink.gateway.player.PlayerFactory.detect_framework",
                return_value="discord.py",
            ):
                return Client(mock_discord_client)

    async def test_search_play_sequence(self, client: Client[Any]) -> None:
        # A track-type search result's .result is a single Playable, since
        # SearchResult.result branches on .type: TRACK -> Playable,
        # PLAYLIST -> Playlist, SEARCH -> list[Playable], EMPTY/ERROR -> None.
        mock_node = MagicMock()
        search_result = make_search_result(
            TrackLoadResult.TRACK,
            track_payload(title="Test Song"),
            client=MagicMock(),
        )
        decoded_track = make_playable(title="Test Song")

        mock_node.search_track = AsyncMock(return_value=search_result)
        mock_node.decode_track = AsyncMock(return_value=decoded_track)

        with patch.object(client, "get_best_node", return_value=mock_node):
            # 1. Search
            result = await client.search_track("Test Song")
            assert result.type is TrackLoadResult.TRACK
            resolved = result.result
            assert isinstance(resolved, Playable)
            assert resolved.title == "Test Song"

            # 2. Decode
            playable = await client.decode_track("encoded_data")
            assert playable.title == "Test Song"

    async def test_search_result_type_is_search_returns_list(
        self, client: Client[Any]
    ) -> None:
        mock_node = MagicMock()
        payload = [
            track_payload(identifier="a", title="First"),
            track_payload(identifier="b", title="Second"),
        ]
        search_result = make_search_result(
            TrackLoadResult.SEARCH, payload, client=MagicMock()
        )
        mock_node.search_track = AsyncMock(return_value=search_result)

        with patch.object(client, "get_best_node", return_value=mock_node):
            result = await client.search_track("query")

            resolved = result.result
            assert isinstance(resolved, list)
            assert [track.title for track in resolved] == ["First", "Second"]

    async def test_search_result_type_empty_returns_none(
        self, client: Client[Any]
    ) -> None:
        mock_node = MagicMock()
        search_result = make_search_result(
            TrackLoadResult.EMPTY, None, client=MagicMock()
        )
        mock_node.search_track = AsyncMock(return_value=search_result)

        with patch.object(client, "get_best_node", return_value=mock_node):
            result = await client.search_track("no matches")

            assert result.is_empty() is True
            assert result.result is None

    async def test_search_multiple_sources(self, client: Client[Any]) -> None:
        mock_node = MagicMock()
        mock_node.search_track = AsyncMock(
            return_value=make_search_result(
                TrackLoadResult.TRACK,
                track_payload(title="Test Song"),
                client=MagicMock(),
            )
        )

        with patch.object(client, "get_best_node", return_value=mock_node):
            # Search YouTube
            await client.search_track("query", source="youtube")

            # Search Spotify
            await client.search_track("query", source="spotify")

            # Search SoundCloud
            await client.search_track("query", source="soundcloud")

            assert mock_node.search_track.call_count == 3

    async def test_bulk_decode_workflow(self, client: Client[Any]) -> None:
        mock_node = MagicMock()
        playables = [
            make_playable(identifier=str(i), title=f"Track {i}", length=180000)
            for i in range(5)
        ]
        mock_node.decode_tracks = AsyncMock(return_value=playables)

        with patch.object(client, "get_best_node", return_value=mock_node):
            result = await client.decode_tracks(
                "encoded1", "encoded2", "encoded3", "encoded4", "encoded5"
            )

            assert len(result) == 5
            assert all(isinstance(track, Playable) for track in result)

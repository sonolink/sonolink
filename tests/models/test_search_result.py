from __future__ import annotations

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest

from sonolink.models import SearchResult
from sonolink.models.playlist import Playlist
from sonolink.models.track import Playable
from sonolink.rest.enums import TrackLoadResult
from sonolink.rest.schemas.track import TrackLoadingResponse


def make_result(
    load_type: TrackLoadResult,
    data: Any,
    *,
    client: MagicMock | None = None,
) -> SearchResult:
    response = TrackLoadingResponse(load_type=load_type, data=data)
    return SearchResult(client=client or MagicMock(), data=response)


ERROR_PAYLOAD: dict[str, Any] = {
    "message": "boom",
    "severity": "common",
    "cause": "test",
    "causeStackTrace": "...",
}


class TestSearchResultIsExported:
    def test_importable_from_models(self) -> None:
        from sonolink import models

        assert models.SearchResult is SearchResult


class TestSearchResultType:
    @pytest.mark.parametrize(
        "load_type",
        [
            TrackLoadResult.TRACK,
            TrackLoadResult.PLAYLIST,
            TrackLoadResult.SEARCH,
            TrackLoadResult.EMPTY,
            TrackLoadResult.ERROR,
        ],
    )
    def test_type_reflects_load_type(self, load_type: TrackLoadResult) -> None:
        assert make_result(load_type, None).type is load_type

    def test_is_empty_true_for_empty(self) -> None:
        assert make_result(TrackLoadResult.EMPTY, None).is_empty() is True

    def test_is_empty_false_for_track(
        self, track_payload: Callable[..., dict[str, Any]]
    ) -> None:
        result = make_result(TrackLoadResult.TRACK, track_payload())
        assert result.is_empty() is False

    def test_is_error_true_for_error(self) -> None:
        data = ERROR_PAYLOAD
        assert make_result(TrackLoadResult.ERROR, data).is_error() is True

    def test_is_error_false_for_track(
        self, track_payload: Callable[..., dict[str, Any]]
    ) -> None:
        result = make_result(TrackLoadResult.TRACK, track_payload())
        assert result.is_error() is False


class TestSearchResultResult:
    def test_track_result_is_playable(
        self, track_payload: Callable[..., dict[str, Any]]
    ) -> None:
        result = make_result(TrackLoadResult.TRACK, track_payload(title="Only Track"))
        resolved = result.result

        assert isinstance(resolved, Playable)
        assert resolved.title == "Only Track"

    def test_search_result_is_list_of_playables(
        self, track_payload: Callable[..., dict[str, Any]]
    ) -> None:
        payload = [
            track_payload(identifier="a", title="First"),
            track_payload(identifier="b", title="Second"),
        ]
        resolved = make_result(TrackLoadResult.SEARCH, payload).result

        assert isinstance(resolved, list)
        assert [track.title for track in resolved] == ["First", "Second"]

    def test_playlist_result_is_playlist(
        self, track_payload: Callable[..., dict[str, Any]]
    ) -> None:
        payload = {
            "info": {"name": "Test Playlist", "selectedTrack": -1},
            "pluginInfo": {},
            "tracks": [track_payload(identifier="a")],
        }
        resolved = make_result(TrackLoadResult.PLAYLIST, payload).result

        assert isinstance(resolved, Playlist)

    def test_empty_result_is_none(self) -> None:
        assert make_result(TrackLoadResult.EMPTY, None).result is None

    def test_error_result_is_none(self) -> None:
        data = ERROR_PAYLOAD
        assert make_result(TrackLoadResult.ERROR, data).result is None


class TestSearchResultException:
    def test_exception_none_when_not_error(
        self, track_payload: Callable[..., dict[str, Any]]
    ) -> None:
        result = make_result(TrackLoadResult.TRACK, track_payload())
        assert result.exception is None

    def test_exception_populated_on_error(self) -> None:
        data = ERROR_PAYLOAD
        exception = make_result(TrackLoadResult.ERROR, data).exception

        assert exception is not None
        assert exception.message == "boom"

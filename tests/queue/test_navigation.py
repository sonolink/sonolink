from __future__ import annotations

import pytest

from sonolink import HistoryEmpty, Queue, QueueEmpty
from sonolink.models.track import Playable


class TestPop:
    def test_pop_removes_head_and_updates_history(
        self, queue_with_tracks: Queue, tracks: list[Playable]
    ) -> None:
        queue_with_tracks.current_track = tracks[4]

        result = queue_with_tracks.pop()

        assert result is tracks[0]
        assert queue_with_tracks.current_track is tracks[0]
        assert queue_with_tracks.tracks == tracks[1:]
        assert queue_with_tracks.history is not None
        assert list(queue_with_tracks.history) == [tracks[4]]

    def test_pop_empty_raises(self, empty_queue: Queue) -> None:
        with pytest.raises(QueueEmpty, match="Queue is empty"):
            empty_queue.pop()


class TestPopAt:
    @pytest.mark.parametrize(("index", "expected"), [(2, 2), (-1, 4)])
    def test_pop_at_supports_indices(
        self,
        queue_with_tracks: Queue,
        tracks: list[Playable],
        index: int,
        expected: int,
    ) -> None:
        result = queue_with_tracks.pop_at(index)

        assert result is tracks[expected]
        assert queue_with_tracks.current_track is tracks[expected]
        assert result not in queue_with_tracks.tracks

    def test_pop_at_out_of_range_raises(self, queue_with_tracks: Queue) -> None:
        with pytest.raises(IndexError):
            queue_with_tracks.pop_at(10)

    def test_pop_at_empty_raises(self, empty_queue: Queue) -> None:
        with pytest.raises(QueueEmpty, match="Queue is empty"):
            empty_queue.pop_at(0)


class TestPrevious:
    def test_previous_restores_history_and_requeues_current(
        self, queue_with_tracks: Queue, tracks: list[Playable]
    ) -> None:
        queue_with_tracks.pop()
        queue_with_tracks.pop()

        result = queue_with_tracks.previous()

        assert result is tracks[0]
        assert queue_with_tracks.current_track is tracks[0]
        assert queue_with_tracks.tracks == [tracks[1], *tracks[2:]]
        assert queue_with_tracks.history is not None
        assert len(queue_with_tracks.history) == 0

    def test_previous_empty_history_raises(self, empty_queue: Queue) -> None:
        with pytest.raises(HistoryEmpty, match="History is empty"):
            empty_queue.previous()

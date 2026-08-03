from __future__ import annotations

import pytest

from sonolink import Queue
from sonolink.models.track import Playable


class TestQueueIteration:

    def test_queue_iterate(self, queue_with_tracks: Queue) -> None:
        assert sum(1 for _ in queue_with_tracks) == 5

    def test_queue_iterate_yields_tracks(self, queue_with_tracks: Queue) -> None:
        titles = [track.title for track in queue_with_tracks]
        assert titles == [f"Track {i + 1}" for i in range(5)]

    def test_queue_iterate_empty(self) -> None:
        assert sum(1 for _ in Queue()) == 0

    def test_queue_reversed(self, queue_with_tracks: Queue, tracks: list[Playable]) -> None:
        assert list(reversed(queue_with_tracks)) == list(reversed(tracks))

    def test_queue_contains(self, queue_with_tracks: Queue, tracks: list[Playable]) -> None:
        assert tracks[0] in queue_with_tracks


class TestQueueIndexing:

    def test_queue_indexing(self, queue_with_tracks: Queue, tracks: list[Playable]) -> None:
        assert queue_with_tracks[0] is tracks[0]
        assert queue_with_tracks[1] is tracks[1]

    def test_queue_index_zero(self, queue_with_tracks: Queue) -> None:
        assert queue_with_tracks[0].title == "Track 1"

    def test_queue_negative_indexing(self, queue_with_tracks: Queue, tracks: list[Playable]) -> None:
        assert queue_with_tracks[-1] is tracks[-1]

    def test_queue_index_out_of_range(self, queue_with_tracks: Queue) -> None:
        with pytest.raises(IndexError):
            queue_with_tracks[999]


class TestQueueSlicing:

    def test_queue_slicing(self, queue_with_tracks: Queue, tracks: list[Playable]) -> None:
        assert queue_with_tracks[0:2] == tracks[0:2]

    def test_queue_slice_all(self, queue_with_tracks: Queue, tracks: list[Playable]) -> None:
        assert queue_with_tracks[:] == tracks

    def test_queue_slice_with_step(self, queue_with_tracks: Queue, tracks: list[Playable]) -> None:
        assert queue_with_tracks[::2] == tracks[::2]

    def test_queue_slice_returns_list(self, queue_with_tracks: Queue) -> None:
        assert isinstance(queue_with_tracks[:2], list)

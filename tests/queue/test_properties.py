from __future__ import annotations

from collections.abc import Callable

import pytest

from sonolink import Queue
from sonolink.gateway.enums import QueueMode
from sonolink.models.track import Playable


class TestQueueLength:
    def test_queue_empty_length(self) -> None:
        queue = Queue()
        assert len(queue) == 0

    def test_count_matches_len(self, make_playable: Callable[..., Playable]) -> None:
        queue = Queue()
        queue.put([make_playable(identifier="a"), make_playable(identifier="b")])
        assert queue.count == len(queue) == 2


class TestQueueDuration:
    def test_queue_total_duration(self, make_playable: Callable[..., Playable]) -> None:
        queue = Queue()
        queue.put(
            [
                make_playable(identifier="a", length=120000),
                make_playable(identifier="b", length=180000),
            ]
        )

        assert queue.total_duration() == 300000

    def test_queue_empty_duration(self) -> None:
        assert Queue().total_duration() == 0

    def test_streams_contribute_zero(
        self, make_playable: Callable[..., Playable]
    ) -> None:
        queue = Queue()
        queue.put(
            [
                make_playable(identifier="a", length=120000),
                make_playable(identifier="live", length=999999, is_stream=True),
            ]
        )

        assert queue.total_duration() == 120000

    def test_loop_mode_is_infinite(
        self, make_playable: Callable[..., Playable]
    ) -> None:
        queue = Queue(mode=QueueMode.LOOP)
        queue.put(make_playable(length=120000))

        assert queue.total_duration() == float("inf")

    def test_duration_until(self, make_playable: Callable[..., Playable]) -> None:
        queue = Queue()
        queue.put(
            [
                make_playable(identifier="a", length=120000),
                make_playable(identifier="b", length=180000),
                make_playable(identifier="c", length=60000),
            ]
        )

        assert queue.duration_until(0) == 0
        assert queue.duration_until(1) == 120000
        assert queue.duration_until(2) == 300000
        assert queue.duration_until(len(queue)) == 360000

    def test_duration_until_out_of_range(
        self, make_playable: Callable[..., Playable]
    ) -> None:
        queue = Queue()
        queue.put(make_playable())

        with pytest.raises(IndexError):
            queue.duration_until(5)


class TestQueueEmpty:
    def test_queue_is_falsy_when_empty(self) -> None:
        queue = Queue()
        assert not queue
        assert len(queue) == 0

    def test_queue_is_truthy_when_not_empty(
        self, make_playable: Callable[..., Playable]
    ) -> None:
        queue = Queue()
        queue.put(make_playable())

        assert queue
        assert len(queue) > 0


class TestQueueDuplication:
    def test_queue_allows_duplicate_tracks(
        self, make_playable: Callable[..., Playable]
    ) -> None:
        queue = Queue()
        track = make_playable()
        queue.put(track)
        queue.put(track)

        assert len(queue) == 2

    def test_queue_duplicates_remain_separate(
        self, make_playable: Callable[..., Playable]
    ) -> None:
        queue = Queue()
        track = make_playable()
        queue.put([track, track])

        assert queue[0] is track
        assert queue[1] is track
        assert len(queue) == 2

    def test_dedupe_removes_duplicates(
        self, make_playable: Callable[..., Playable]
    ) -> None:
        queue = Queue()
        track = make_playable(identifier="dupe")
        queue.put([track, track, make_playable(identifier="unique")])

        removed = queue.dedupe()

        assert removed == 1
        assert len(queue) == 2

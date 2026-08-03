from __future__ import annotations

from typing import Callable

import pytest

from sonolink import Queue
from sonolink.gateway.errors import QueueEmpty
from sonolink.models.track import Playable


class TestQueueInitialization:

    def test_queue_init(self) -> None:
        queue = Queue()
        assert len(queue) == 0

    def test_queue_init_populate_via_put(self, make_playable: Callable[..., Playable]) -> None:
        queue = Queue()
        queue.put(make_playable())
        assert len(queue) == 1

    def test_queue_repr(self) -> None:
        assert "Queue" in repr(Queue())


class TestQueuePutGet:

    def test_queue_put(self, empty_queue: Queue, make_playable: Callable[..., Playable]) -> None:
        empty_queue.put(make_playable())
        assert len(empty_queue) == 1

    def test_queue_put_multiple(self, empty_queue: Queue, make_playable: Callable[..., Playable]) -> None:
        empty_queue.put(make_playable(identifier="a"))
        empty_queue.put(make_playable(identifier="b"))
        assert len(empty_queue) == 2

    def test_queue_put_rejects_non_playable_when_atomic(self, empty_queue: Queue) -> None:
        with pytest.raises(TypeError):
            empty_queue.put("not a track")  # type: ignore[arg-type]

    def test_queue_get(self, empty_queue: Queue, make_playable: Callable[..., Playable]) -> None:
        track = make_playable()
        empty_queue.put(track)
        retrieved = empty_queue.get()
        assert retrieved == track
        assert len(empty_queue) == 0

    def test_queue_get_empty_raises(self, empty_queue: Queue) -> None:
        with pytest.raises(QueueEmpty):
            empty_queue.get()

    def test_queue_get_sets_current_track(self, empty_queue: Queue, make_playable: Callable[..., Playable]) -> None:
        track = make_playable()
        empty_queue.put(track)
        empty_queue.get()
        assert empty_queue.current_track == track


class TestQueueIndexAccess:

    def test_queue_index_zero_without_removing(
        self, empty_queue: Queue, make_playable: Callable[..., Playable]
    ) -> None:
        track = make_playable()
        empty_queue.put(track)
        assert empty_queue[0] == track
        assert len(empty_queue) == 1

    def test_queue_index_empty_raises(self, empty_queue: Queue) -> None:
        with pytest.raises(IndexError):
            _ = empty_queue[0]


class TestQueueClear:

    def test_queue_clear(self, empty_queue: Queue, make_playable: Callable[..., Playable]) -> None:
        empty_queue.put(make_playable(identifier="a"))
        empty_queue.put(make_playable(identifier="b"))
        empty_queue.clear()
        assert len(empty_queue) == 0

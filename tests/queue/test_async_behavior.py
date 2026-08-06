from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, cast

import pytest

from sonolink import Queue, QueueMode
from sonolink.models.settings import HistorySettings
from sonolink.models.track import Playable


async def _wait_for_waiters(queue: Queue, count: int) -> None:
    while len(queue._waiters) < count:
        await asyncio.sleep(0)


class TestGetWait:
    async def test_get_wait_returns_existing_track_immediately(
        self, queue_with_tracks: Queue, tracks: list[Playable]
    ) -> None:
        result = await queue_with_tracks.get_wait()

        assert result is tracks[0]
        assert queue_with_tracks.tracks == tracks[1:]

    async def test_get_wait_blocks_until_put(
        self, empty_queue: Queue, track: Playable
    ) -> None:
        task = asyncio.create_task(empty_queue.get_wait())
        await _wait_for_waiters(empty_queue, 1)

        assert not task.done()
        empty_queue.put(track)
        assert await task is track

    async def test_get_wait_wakes_on_put_autoplay(
        self, empty_queue: Queue, track: Playable
    ) -> None:
        task = asyncio.create_task(empty_queue.get_wait())
        await _wait_for_waiters(empty_queue, 1)
        empty_queue.put_autoplay(track)

        assert await task is track
        assert track.autoplay is True
        assert not empty_queue.autoplay_tracks

    async def test_many_waiters_wake_fifo(
        self, empty_queue: Queue, tracks: list[Playable]
    ) -> None:
        tasks = [asyncio.create_task(empty_queue.get_wait()) for _ in tracks]
        await _wait_for_waiters(empty_queue, len(tracks))

        for track in tracks:
            empty_queue.put(track)

        results = await asyncio.gather(*tasks)
        assert [track.identifier for track in results] == [
            track.identifier for track in tracks
        ]

    async def test_single_put_wakes_single_waiter(
        self, empty_queue: Queue, tracks: list[Playable]
    ) -> None:
        first = asyncio.create_task(empty_queue.get_wait())
        second = asyncio.create_task(empty_queue.get_wait())
        await _wait_for_waiters(empty_queue, 2)

        empty_queue.put(tracks[0])
        await asyncio.sleep(0)

        assert first.done()
        assert not second.done()

        empty_queue.put(tracks[1])
        results = await asyncio.gather(first, second)

        assert [track.identifier for track in results] == [
            tracks[0].identifier,
            tracks[1].identifier,
        ]

    async def test_get_wait_autoplay_fallback(
        self, empty_queue: Queue, tracks: list[Playable]
    ) -> None:
        empty_queue.put_autoplay(tracks[:2])

        result = await empty_queue.get_wait()

        assert result is tracks[0]
        assert result.autoplay is True
        assert empty_queue.autoplay_tracks == tracks[1:2]

    async def test_get_wait_loop_all_restores_history(
        self, tracks: list[Playable]
    ) -> None:
        queue = Queue(
            mode=QueueMode.LOOP_ALL,
            history_settings=HistorySettings(enabled=True),
        )
        queue.put(tracks[:2])
        queue.get()
        queue.get()
        assert queue.history is not None
        assert len(queue.history) == 1

        result = await queue.get_wait()

        assert result is tracks[0]
        assert queue.tracks == [tracks[1]]
        assert queue.history is not None
        assert len(queue.history) == 0

    async def test_cancelled_get_wait_cleans_up_waiter(
        self, empty_queue: Queue, track: Playable
    ) -> None:
        task = asyncio.create_task(empty_queue.get_wait())
        await _wait_for_waiters(empty_queue, 1)

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert len(empty_queue._waiters) == 0

        empty_queue.put(track)

        assert await empty_queue.get_wait() is track

    async def test_reset_cancels_pending_waiters(self, empty_queue: Queue) -> None:
        task = asyncio.create_task(empty_queue.get_wait())
        await _wait_for_waiters(empty_queue, 1)

        empty_queue.reset()

        with pytest.raises(asyncio.CancelledError):
            await task
        assert task.cancelled()
        assert len(empty_queue._waiters) == 0


class TestPutWaitConcurrency:
    async def test_concurrent_put_wait_keeps_batches_contiguous(
        self,
        empty_queue: Queue,
        tracks: list[Playable],
        make_playable: Callable[..., Playable],
    ) -> None:
        extra = make_playable(identifier="extra")
        batches = [tracks[:2], tracks[2:4], [tracks[4], extra]]

        await asyncio.gather(*(empty_queue.put_wait(batch) for batch in batches))

        final = empty_queue.tracks
        total = [track.identifier for track in final]

        assert sorted(total) == sorted(
            [track.identifier for track in tracks] + [extra.identifier]
        )

        for batch in batches:
            start = final.index(batch[0])
            assert final[start : start + len(batch)] == batch

    async def test_mixed_put_wait_and_get_wait_consumes_everything(
        self, empty_queue: Queue, tracks: list[Playable]
    ) -> None:
        getters = [asyncio.create_task(empty_queue.get_wait()) for _ in tracks]
        await _wait_for_waiters(empty_queue, len(tracks))

        await asyncio.gather(*(empty_queue.put_wait([track]) for track in tracks))
        results = await asyncio.gather(*getters)

        assert [track.identifier for track in results] == [
            track.identifier for track in tracks
        ]
        assert len(empty_queue) == 0

    async def test_put_wait_releases_lock_when_atomic_raises(
        self, empty_queue: Queue, track: Playable
    ) -> None:
        with pytest.raises(TypeError, match="Expected Playable"):
            await empty_queue.put_wait(cast(Any, [track, "invalid"]))

        assert not empty_queue.tracks

        added = await asyncio.wait_for(empty_queue.put_wait([track]), timeout=2.0)
        assert added == 1

        removed = await asyncio.wait_for(empty_queue.remove_wait(track), timeout=2.0)
        assert removed == 1

    async def test_failed_put_wait_does_not_stall_other_put_waiters(
        self, empty_queue: Queue, track: Playable
    ) -> None:
        async def failing_put() -> str:
            try:
                await empty_queue.put_wait(cast(Any, [track, "invalid"]))
            except TypeError:
                return "raised"
            return "unexpected"

        results = await asyncio.gather(
            failing_put(),
            empty_queue.put_wait([track]),
            empty_queue.put_wait([track]),
        )

        assert results[0] == "raised"
        assert results[1:] == [1, 1]
        assert empty_queue.tracks == [track, track]


class TestRemoveWaitConcurrency:
    async def test_concurrent_remove_wait_removes_all_targets(
        self, empty_queue: Queue, tracks: list[Playable]
    ) -> None:
        empty_queue.put(tracks)
        removed = await asyncio.gather(
            *(empty_queue.remove_wait(track) for track in tracks[:3])
        )

        assert removed == [1, 1, 1]
        assert empty_queue.tracks == tracks[3:]

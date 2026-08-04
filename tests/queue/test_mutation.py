from __future__ import annotations

from collections.abc import Callable

import pytest

from sonolink import Queue, QueueEmpty, QueueMode, ShuffleMode
from sonolink.models.settings import HistorySettings
from sonolink.models.track import Playable


class TestPutAndRemove:
    async def test_put_wait_adds_tracks(
        self, empty_queue: Queue, tracks: list[Playable]
    ) -> None:
        assert await empty_queue.put_wait(tracks[:2]) == 2
        assert empty_queue.tracks == tracks[:2]

    async def test_put_wait_atomic_rejects_invalid_item(
        self, empty_queue: Queue, track: Playable
    ) -> None:
        with pytest.raises(TypeError, match="Expected Playable"):
            await empty_queue.put_wait([track, "invalid"])  # pyright: ignore[reportArgumentType]
        assert empty_queue.tracks == []

    def test_put_autoplay_tags_and_stages_tracks(
        self, empty_queue: Queue, tracks: list[Playable]
    ) -> None:
        assert empty_queue.put_autoplay(tracks[:2]) == 2
        assert empty_queue.autoplay_tracks == tracks[:2]
        assert all(track.autoplay for track in tracks[:2])

    @pytest.mark.parametrize(("remove_all", "remaining"), [(True, 0), (False, 1)])
    def test_remove_occurrences(
        self,
        empty_queue: Queue,
        track: Playable,
        remove_all: bool,
        remaining: int,
    ) -> None:
        empty_queue.put([track, track])

        assert empty_queue.remove(track, remove_all=remove_all) == 2 - remaining
        assert empty_queue.tracks == [track] * remaining

    def test_remove_iterable_and_key(
        self,
        empty_queue: Queue,
        make_playable: Callable[..., Playable],
    ) -> None:
        tracks = [
            make_playable(identifier="a"),
            make_playable(identifier="b"),
            make_playable(identifier="a"),
        ]
        empty_queue.put(tracks)

        assert (
            empty_queue.remove(
                ["a"],  # pyright: ignore[reportArgumentType]
                key=lambda item: item.identifier,
            )
            == 2
        )
        assert empty_queue.tracks == [tracks[1]]

    async def test_remove_wait_removes_first_match(
        self, empty_queue: Queue, track: Playable
    ) -> None:
        empty_queue.put([track, track])

        assert await empty_queue.remove_wait(track, remove_all=False) == 1
        assert empty_queue.tracks == [track]


class TestOrdering:
    def test_copy_is_independent(
        self, queue_with_tracks: Queue, tracks: list[Playable]
    ) -> None:
        queue_with_tracks.mode = QueueMode.LOOP_ALL
        queue_with_tracks.shuffle_mode = ShuffleMode.PERSISTENT
        queue_with_tracks.pop()
        queue_with_tracks.pop()
        copied = queue_with_tracks.copy()

        copied.remove_at(0)
        copied.clear_history()

        assert copied.mode is QueueMode.LOOP_ALL
        assert copied.shuffle_mode is ShuffleMode.PERSISTENT
        assert copied.current_track is queue_with_tracks.current_track
        assert copied.tracks != queue_with_tracks.tracks
        assert copied.history is not None
        assert queue_with_tracks.history is not None
        assert len(copied.history) == 0
        assert len(queue_with_tracks.history) == 1
        queue_with_tracks.put(tracks[0])
        assert queue_with_tracks.tracks != copied.tracks

    def test_reverse_returns_none(
        self, queue_with_tracks: Queue, tracks: list[Playable]
    ) -> None:
        assert queue_with_tracks.reverse() is None
        assert queue_with_tracks.tracks == list(reversed(tracks))

    @pytest.mark.parametrize("reverse", [False, True])
    def test_sort(self, queue_with_tracks: Queue, reverse: bool) -> None:
        queue_with_tracks.sort(key=lambda track: track.title, reverse=reverse)

        assert [track.title for track in queue_with_tracks] == sorted(
            [track.title for track in queue_with_tracks], reverse=reverse
        )

    @pytest.mark.parametrize("count", [0, 1, 2, 5])
    def test_shuffle_preserves_tracks(
        self, empty_queue: Queue, tracks: list[Playable], count: int
    ) -> None:
        selected = tracks[:count]
        empty_queue.put(selected)

        assert empty_queue.shuffle() is None
        assert len(empty_queue) == count
        assert set(empty_queue.tracks) == set(selected)

    @pytest.mark.parametrize(
        ("old", "new", "expected"),
        [
            (0, 3, [1, 2, 3, 0, 4]),
            (3, 0, [3, 0, 1, 2, 4]),
            (2, 2, [0, 1, 2, 3, 4]),
        ],
    )
    def test_move(
        self,
        queue_with_tracks: Queue,
        tracks: list[Playable],
        old: int,
        new: int,
        expected: list[int],
    ) -> None:
        result = queue_with_tracks.move(old, new)

        assert result is tracks[old]
        assert queue_with_tracks.tracks == [tracks[index] for index in expected]

    @pytest.mark.parametrize(("old", "new"), [(5, 0), (0, 5), (-6, 0)])
    def test_move_out_of_range_raises(
        self, queue_with_tracks: Queue, old: int, new: int
    ) -> None:
        with pytest.raises(IndexError, match="out of range"):
            queue_with_tracks.move(old, new)

    def test_move_empty_raises(self, empty_queue: Queue) -> None:
        with pytest.raises(QueueEmpty, match="Queue is empty"):
            empty_queue.move(0, 0)

    def test_remove_at_has_no_playback_side_effects(
        self, queue_with_tracks: Queue, tracks: list[Playable]
    ) -> None:
        queue_with_tracks.current_track = tracks[4]

        result = queue_with_tracks.remove_at(1)

        assert result is tracks[1]
        assert queue_with_tracks.current_track is tracks[4]
        assert queue_with_tracks.history is not None
        assert len(queue_with_tracks.history) == 0

    def test_swap(self, queue_with_tracks: Queue, tracks: list[Playable]) -> None:
        assert queue_with_tracks.swap(0, 3) is None
        assert queue_with_tracks.tracks == [
            tracks[3],
            tracks[1],
            tracks[2],
            tracks[0],
            tracks[4],
        ]

    @pytest.mark.parametrize(("old", "new"), [(10, 0), (0, 10)])
    def test_swap_out_of_range_raises(
        self, queue_with_tracks: Queue, old: int, new: int
    ) -> None:
        with pytest.raises(IndexError):
            queue_with_tracks.swap(old, new)


class TestState:
    def test_track_properties_return_copies(
        self, queue_with_tracks: Queue, tracks: list[Playable]
    ) -> None:
        queue_with_tracks.put_autoplay(tracks[:2])
        user_tracks = queue_with_tracks.tracks
        autoplay_tracks = queue_with_tracks.autoplay_tracks

        user_tracks.clear()
        autoplay_tracks.clear()

        assert len(queue_with_tracks) == 5
        assert queue_with_tracks.autoplay_tracks == tracks[:2]

    def test_mode_setter_and_loop_behavior(
        self, queue_with_tracks: Queue, tracks: list[Playable]
    ) -> None:
        queue_with_tracks.mode = QueueMode.LOOP
        queue_with_tracks.current_track = tracks[4]

        assert queue_with_tracks.get() is tracks[4]
        assert queue_with_tracks.get() is tracks[4]
        queue_with_tracks.mode = QueueMode.LOOP_ALL
        assert queue_with_tracks.mode is QueueMode.LOOP_ALL
        queue_with_tracks.mode = QueueMode.NORMAL
        assert queue_with_tracks.mode is QueueMode.NORMAL

    def test_persistent_shuffle_uses_random_choice(
        self,
        queue_with_tracks: Queue,
        tracks: list[Playable],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def choose_third(indices: list[int]) -> int:
            return indices[2]

        monkeypatch.setattr("sonolink.gateway.queue.queue.random.choice", choose_third)
        queue_with_tracks.shuffle_mode = ShuffleMode.PERSISTENT

        assert queue_with_tracks.get() is tracks[2]

    def test_clear_history(self, queue_with_tracks: Queue) -> None:
        queue_with_tracks.pop()
        queue_with_tracks.pop()
        assert queue_with_tracks.history is not None
        assert len(queue_with_tracks.history) == 1

        queue_with_tracks.clear_history()

        assert len(queue_with_tracks.history) == 0

    def test_reset_restores_every_default(self, tracks: list[Playable]) -> None:
        queue = Queue(history_settings=HistorySettings(enabled=True))
        queue.put(tracks[:3])
        queue.pop()
        queue.pop()
        queue.put_autoplay(tracks[3:])
        queue.mode = QueueMode.LOOP_ALL
        queue.shuffle_mode = ShuffleMode.PERSISTENT

        queue.reset()

        assert queue.tracks == []
        assert queue.autoplay_tracks == []
        assert queue.history is not None
        assert len(queue.history) == 0
        assert queue.mode is QueueMode.NORMAL
        assert queue.shuffle_mode is ShuffleMode.DEFAULT
        assert queue.current_track is None

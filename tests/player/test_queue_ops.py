from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from sonolink import HistoryEmpty, QueueEmpty
from sonolink.models.track import Playable

from ..helpers import ConcreteTestPlayer, make_playable


class TestPlayerQueueAccess:
    def test_queue_starts_empty(self, ready_player: ConcreteTestPlayer) -> None:
        assert len(ready_player.queue) == 0

    def test_queue_put_and_len(
        self, ready_player: ConcreteTestPlayer, tracks: list[Playable]
    ) -> None:
        ready_player.queue.put(tracks)
        assert len(ready_player.queue) == len(tracks)


class TestPlayerSkip:
    async def test_skip_plays_next_queued_track(
        self, ready_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
    ) -> None:
        first = make_playable(identifier="first")
        second = make_playable(identifier="second")
        ready_player.queue.put(second)

        await ready_player.play(first)
        result = await ready_player.skip()

        assert result is second
        assert ready_player.current is second

    async def test_skip_moves_previous_to_history(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        first = make_playable(identifier="first")
        ready_player.queue.put(make_playable(identifier="second"))

        await ready_player.play(first)
        await ready_player.skip()

        history = ready_player.history
        assert history is not None
        assert first in history

    async def test_skip_on_empty_queue_raises(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        await ready_player.play(make_playable())

        with pytest.raises(QueueEmpty):
            await ready_player.skip()


class TestPlayerSkipTo:
    async def test_skip_to_index(self, ready_player: ConcreteTestPlayer) -> None:
        ready_player.queue.put(
            [
                make_playable(identifier="a"),
                make_playable(identifier="b"),
                make_playable(identifier="c"),
            ]
        )
        await ready_player.play(make_playable(identifier="current"))
        result = await ready_player.skip_to(1)
        assert result.identifier == "b"

    async def test_skip_to_out_of_range_raises(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        ready_player.queue.put(make_playable())
        with pytest.raises(IndexError):
            await ready_player.skip_to(5)

    async def test_skip_to_on_empty_queue_raises_queue_empty(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        with pytest.raises(QueueEmpty):
            await ready_player.skip_to(0)


class TestPlayerPrevious:
    async def test_previous_replays_history(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        first = make_playable(identifier="first")
        second = make_playable(identifier="second")

        await ready_player.play(first)
        await ready_player.play(second)
        result = await ready_player.previous()

        assert result is first
        assert ready_player.current is first

    async def test_previous_on_empty_history_raises(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        with pytest.raises(HistoryEmpty):
            await ready_player.previous()

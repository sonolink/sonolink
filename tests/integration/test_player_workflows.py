from unittest.mock import MagicMock

from ..helpers import ConcreteTestPlayer, make_playable


class TestPlayerPlayworkflow:

    async def test_play_track_workflow(self, ready_player: ConcreteTestPlayer) -> None:
        track = make_playable(title="Test Track")

        await ready_player.play(track)
        assert ready_player.current is track
        assert ready_player.is_playing is True

        await ready_player.pause()
        assert ready_player.paused is True
        assert ready_player.is_playing is False

        await ready_player.resume()
        assert ready_player.paused is False
        assert ready_player.is_playing is True

    async def test_queue_and_play_workflow(self, ready_player: ConcreteTestPlayer) -> None:
        first = make_playable(identifier="first")
        second = make_playable(identifier="second")

        ready_player.queue.put(second)
        await ready_player.play(first)
        assert len(ready_player.queue) == 1

        skipped_to = await ready_player.skip()
        assert skipped_to is second
        assert ready_player.current is second
        assert len(ready_player.queue) == 0

    async def test_volume_control_workflow(
        self, ready_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
    ) -> None:
        assert ready_player.volume == 100

        await ready_player.set_volume(50)
        assert ready_player.volume == 50

        await ready_player.set_volume(100)
        assert ready_player.volume == 100
        assert mock_rest_manager.update_player.await_count == 2

    async def test_seeking_workflow(self, ready_player: ConcreteTestPlayer) -> None:
        await ready_player.play(make_playable(length=180000))

        await ready_player.seek(30000)
        assert ready_player.position == 30000

        await ready_player.seek(60000)
        assert ready_player.position == 60000

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from sonolink.models.track import Playable

from ...helpers import ConcreteTestPlayer, make_playable


class TestPlayerPlay:
    async def test_play_returns_track(
        self, ready_player: ConcreteTestPlayer, track: Playable
    ) -> None:
        assert await ready_player.play(track) is track

    async def test_play_sets_current_track(
        self, ready_player: ConcreteTestPlayer, track: Playable
    ) -> None:
        await ready_player.play(track)

        assert ready_player.current is track
        assert ready_player.is_playing is True

    async def test_play_sends_update_to_node(
        self,
        ready_player: ConcreteTestPlayer,
        mock_rest_manager: MagicMock,
        track: Playable,
    ) -> None:
        await ready_player.play(track)

        mock_rest_manager.update_player.assert_awaited_once()
        kwargs = mock_rest_manager.update_player.await_args.kwargs
        assert kwargs["session_id"] == "session-abc"
        assert kwargs["guild_id"] == str(ready_player.guild.id)

    async def test_play_sends_encoded_track(
        self,
        ready_player: ConcreteTestPlayer,
        mock_rest_manager: MagicMock,
        track: Playable,
    ) -> None:
        await ready_player.play(track)

        data = mock_rest_manager.update_player.await_args.kwargs["data"]
        assert data.track.encoded == track.encoded

    async def test_play_honours_start_position(
        self, ready_player: ConcreteTestPlayer, track: Playable
    ) -> None:
        await ready_player.play(track, start=5000)

        assert ready_player._last_position == 5000

    async def test_play_volume_override(
        self, ready_player: ConcreteTestPlayer, track: Playable
    ) -> None:
        await ready_player.play(track, volume=50)

        assert ready_player.volume == 50

    async def test_play_paused_override(
        self, ready_player: ConcreteTestPlayer, track: Playable
    ) -> None:
        await ready_player.play(track, paused=True)

        assert ready_player.paused is True
        assert ready_player.is_playing is False

    async def test_play_forwards_no_replace(
        self,
        ready_player: ConcreteTestPlayer,
        mock_rest_manager: MagicMock,
        track: Playable,
    ) -> None:
        await ready_player.play(track, no_replace=True)

        assert mock_rest_manager.update_player.await_args.kwargs["no_replace"] is True

    async def test_previous_track_goes_to_history(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        first = make_playable(identifier="first")
        second = make_playable(identifier="second")

        await ready_player.play(first)
        await ready_player.play(second)

        history = ready_player.history
        assert history is not None
        assert first in history

    async def test_failed_play_clears_original_track(
        self,
        ready_player: ConcreteTestPlayer,
        mock_rest_manager: MagicMock,
        track: Playable,
    ) -> None:
        mock_rest_manager.update_player = AsyncMock(side_effect=RuntimeError("boom"))

        with pytest.raises(RuntimeError, match="boom"):
            await ready_player.play(track)

        assert ready_player._original_track is None


class TestPlayerPauseResume:
    async def test_pause_sets_state(
        self, ready_player: ConcreteTestPlayer, track: Playable
    ) -> None:
        await ready_player.play(track)
        await ready_player.pause()

        assert ready_player.paused is True

    async def test_resume_clears_state(
        self, ready_player: ConcreteTestPlayer, track: Playable
    ) -> None:
        await ready_player.play(track, paused=True)
        await ready_player.resume()

        assert ready_player.paused is False

    async def test_pause_notifies_node(
        self, ready_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
    ) -> None:
        await ready_player.pause()

        data = mock_rest_manager.update_player.await_args.kwargs["data"]
        assert data.paused is True

    async def test_resume_notifies_node(
        self, ready_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
    ) -> None:
        await ready_player.resume()

        data = mock_rest_manager.update_player.await_args.kwargs["data"]
        assert data.paused is False


class TestPlayerStop:
    async def test_stop_resets_position(
        self, ready_player: ConcreteTestPlayer, track: Playable
    ) -> None:
        await ready_player.play(track, start=5000)
        await ready_player.stop()

        assert ready_player._last_position == 0

    async def test_stop_can_clear_queue(
        self, ready_player: ConcreteTestPlayer, tracks: list[Playable]
    ) -> None:
        ready_player.queue.put(tracks)
        await ready_player.stop(clear_queue=True)

        assert len(ready_player.queue) == 0

    async def test_stop_keeps_queue_by_default(
        self, ready_player: ConcreteTestPlayer, tracks: list[Playable]
    ) -> None:
        ready_player.queue.put(tracks)
        await ready_player.stop()

        assert len(ready_player.queue) == len(tracks)


class TestPlayerRequiresNode:
    async def test_play_without_node_raises(self, track: Playable) -> None:
        player = ConcreteTestPlayer(node=None)
        player._guild = MagicMock(id=1)

        with pytest.raises(RuntimeError, match="not attached to a node"):
            await player.play(track)

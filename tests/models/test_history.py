from __future__ import annotations

import pytest

from sonolink import History
from sonolink.models.settings import HistorySettings
from sonolink.models.track import Playable

from ..helpers import make_playable


class TestHistoryBasics:
    def test_history_init_is_empty(self) -> None:
        history = History()
        assert len(history) == 0
        assert not history

    def test_history_enabled_by_default(self) -> None:
        assert History().enabled is True


class TestHistoryRecording:
    def test_push_records_track(self, track: Playable) -> None:
        history = History()
        history._push(track)

        assert len(history) == 1
        assert history[0] is track
        assert track in history

    def test_push_ignored_when_disabled(self, track: Playable) -> None:
        history = History(settings=HistorySettings(enabled=False))
        history._push(track)

        assert len(history) == 0

    def test_max_items_evicts_oldest(self) -> None:
        history = History(settings=HistorySettings(max_items=2))
        first = make_playable(identifier="first")

        history._push(first)
        history._push(make_playable(identifier="second"))
        history._push(make_playable(identifier="third"))

        assert len(history) == 2
        assert first not in history

    def test_clear_empties_history(self, track: Playable) -> None:
        history = History()
        history._push(track)
        assert len(history) == 1

        history._clear()

        assert len(history) == 0

    def test_copy_is_independent(self, track: Playable) -> None:
        history = History()
        history._push(track)

        copied = history._copy()
        copied._push(make_playable(identifier="other"))

        assert len(history) == 1
        assert len(copied) == 2


class TestHistoryIsReadOnly:
    @pytest.mark.parametrize("name", ["add", "put", "append", "clear", "remove"])
    def test_no_public_mutators(self, name: str) -> None:
        assert not hasattr(History(), name)

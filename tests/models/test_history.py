"""Apache License 2.0

Copyright (c) 2026-present SonoLink Development Team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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

        history.clear()

        assert len(history) == 0

    def test_copy_is_independent(self, track: Playable) -> None:
        history = History()
        history._push(track)

        copied = history._copy()
        copied._push(make_playable(identifier="other"))

        assert len(history) == 1
        assert len(copied) == 2


class TestHistoryIsReadOnly:
    @pytest.mark.parametrize("name", ["add", "put", "append", "remove"])
    def test_no_public_mutators(self, name: str) -> None:
        assert not hasattr(History(), name)

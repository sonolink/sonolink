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

import types

from sonolink.models.track import Album, Artist

from ..helpers import make_playable


class TestPlayableMetadata:
    def test_len_returns_length(self) -> None:
        track = make_playable(length=180000)
        assert len(track) == track.length == 180000

    def test_str_returns_title(self) -> None:
        assert str(make_playable(title="Test Track")) == "Test Track"


class TestPlayableEquality:
    def test_same_encoded_is_equal(self) -> None:
        assert make_playable(identifier="same") == make_playable(identifier="same")

    def test_different_encoded_not_equal(self) -> None:
        assert make_playable(identifier="a") != make_playable(identifier="b")

    def test_not_equal_to_other_types(self) -> None:
        assert make_playable() != "not a track"

    def test_hashes_match_equality(self) -> None:
        assert hash(make_playable(identifier="x")) == hash(
            make_playable(identifier="x")
        )

    def test_usable_in_a_set(self) -> None:
        track = make_playable(identifier="dupe")
        assert len({track, make_playable(identifier="dupe")}) == 1


class TestPlayableExtras:
    def test_extras_defaults_to_namespace(self) -> None:
        assert isinstance(make_playable().extras, types.SimpleNamespace)

    def test_extras_accepts_mapping(self) -> None:
        track = make_playable()
        track.extras = {"requester": 12345}

        assert track.extras.requester == 12345

    def test_extras_accepts_namespace(self) -> None:
        track = make_playable()
        track.extras = types.SimpleNamespace(requester=99)

        assert track.extras.requester == 99


class TestPluginMetadata:
    def test_album_without_plugin_info(self) -> None:
        album = make_playable().album

        assert isinstance(album, Album)
        assert album.name is None

    def test_artist_without_plugin_info(self) -> None:
        artist = make_playable().artist

        assert isinstance(artist, Artist)
        assert artist.name is None

    def test_playlist_defaults_to_none(self) -> None:
        assert make_playable().playlist is None

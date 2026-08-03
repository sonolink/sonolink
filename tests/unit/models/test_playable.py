from __future__ import annotations

import types

import pytest

from sonolink.models.track import Album, Artist, Playable

from ...helpers import make_playable


class TestPlayableMetadata:

    def test_title(self) -> None:
        assert make_playable(title="Test Track").title == "Test Track"

    def test_author(self) -> None:
        assert make_playable(author="Test Artist").author == "Test Artist"

    def test_uri(self) -> None:
        track = make_playable(uri="https://example.com/track")
        assert track.uri == "https://example.com/track"

    def test_uri_may_be_none(self) -> None:
        assert make_playable(uri=None).uri is None

    def test_identifier(self) -> None:
        assert make_playable(identifier="abc123").identifier == "abc123"

    def test_source_name(self) -> None:
        assert make_playable(source_name="youtube").source_name == "youtube"

    def test_encoded(self) -> None:
        assert make_playable(encoded="abc==").encoded == "abc=="

    def test_length_is_milliseconds(self) -> None:
        assert make_playable(length=3 * 60 * 1000).length == 180000

    def test_len_returns_length(self) -> None:
        track = make_playable(length=180000)
        assert len(track) == track.length == 180000

    def test_str_returns_title(self) -> None:
        assert str(make_playable(title="Test Track")) == "Test Track"


class TestPlayableFlags:

    def test_is_stream_false(self) -> None:
        assert make_playable(is_stream=False).is_stream is False

    def test_is_stream_true(self) -> None:
        assert make_playable(is_stream=True).is_stream is True

    def test_is_seekable(self) -> None:
        assert make_playable(is_stream=False).is_seekable is True

    def test_autoplay_defaults_false(self) -> None:
        assert make_playable().autoplay is False


class TestPlayableEquality:

    def test_same_encoded_is_equal(self) -> None:
        assert make_playable(identifier="same") == make_playable(identifier="same")

    def test_different_encoded_not_equal(self) -> None:
        assert make_playable(identifier="a") != make_playable(identifier="b")

    def test_not_equal_to_other_types(self) -> None:
        assert make_playable() != "not a track"

    def test_hashes_match_equality(self) -> None:
        assert hash(make_playable(identifier="x")) == hash(make_playable(identifier="x"))

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


class TestPlayableIsExported:

    def test_importable_from_models(self) -> None:
        from sonolink import models

        assert models.Playable is Playable

    @pytest.mark.parametrize("name", ["title", "author", "length", "encoded"])
    def test_core_properties_present(self, name: str) -> None:
        assert isinstance(getattr(Playable, name), property)

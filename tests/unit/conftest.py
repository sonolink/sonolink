from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from sonolink import Queue
from sonolink.models.track import Playable

from ..helpers import make_playable


@pytest.fixture
def track() -> Playable:
    return make_playable()


@pytest.fixture
def tracks() -> list[Playable]:
    return [
        make_playable(
            identifier=f"track-{i}",
            title=f"Track {i + 1}",
            author=f"Artist {i + 1}",
            length=120000 + (i * 30000),
        )
        for i in range(5)
    ]


@pytest.fixture
def empty_queue() -> Queue:
    return Queue()


@pytest.fixture
def queue_with_tracks(tracks: list[Playable]) -> Queue:
    queue = Queue()
    queue.put(tracks)
    return queue


@pytest.fixture
def mock_voice_channel(mock_guild: MagicMock) -> MagicMock:
    channel = MagicMock()
    channel.id = 111111111
    channel.name = "test-voice"
    channel.guild = mock_guild
    return channel


@pytest.fixture
def mock_discord_client() -> MagicMock:
    client = MagicMock()
    client.user = MagicMock(id=123456789, name="TestBot")
    return client

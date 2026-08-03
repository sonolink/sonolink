from __future__ import annotations

from typing import Any

from sonolink.gateway.player._base import BasePlayer
from sonolink.models.track import Playable
from sonolink.rest.schemas.track import Track, TrackInfo


def make_playable(
    *,
    identifier: str = "test-id",
    title: str = "Test Track",
    author: str = "Test Artist",
    length: int = 180000,
    is_stream: bool = False,
    encoded: str | None = None,
    uri: str | None = "https://example.com/watch?v=test",
    source_name: str = "youtube",
) -> Playable:
    info = TrackInfo(
        identifier=identifier,
        uri=uri,
        title=title,
        author=author,
        length=length,
        position=0,
        is_seekable=not is_stream,
        is_stream=is_stream,
        source_name=source_name,
    )
    data = Track(
        encoded=encoded if encoded is not None else f"encoded::{identifier}",
        info=info,
        plugin_info=None,
        user_data=None,
    )
    return Playable(client=None, data=data)  # pyright: ignore[reportArgumentType]


class ConcreteTestPlayer(BasePlayer):

    def __call__(self, client: Any, channel: Any) -> ConcreteTestPlayer:
        self._guild = getattr(channel, "guild", None)
        self.client = client
        self.channel = channel
        return self

    async def on_voice_server_update(self, data: Any) -> None:
        pass

    async def on_voice_state_update(self, data: Any) -> None:
        pass

    def cleanup(self) -> None:
        pass

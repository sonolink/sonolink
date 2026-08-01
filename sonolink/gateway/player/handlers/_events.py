"""MIT License

Copyright (c) 2026-present SonoLink Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
from typing import Any

import msgspec

from sonolink.gateway.enums import DisconnectTriggerType, TrackEndReason
from sonolink.gateway.errors import AutoPlaySeedMissing, QueueEmpty
from sonolink.gateway.event_models import (
    StatsEvent,
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStartEvent,
    TrackStuckEvent,
    WebSocketClosedEvent,
)
from sonolink.gateway.schemas.events import (
    TrackEndEvent as TrackEndEventPayload,
    TrackExceptionEvent as TrackExceptionEventPayload,
    TrackStartEvent as TrackStartEventPayload,
    TrackStuckEvent as TrackStuckEventPayload,
)
from sonolink.gateway.schemas.receive import (
    PlayerState,
    StatsEvent as StatsEventPayload,
    WebSocketClosedEvent as WebSocketClosedEventPayload,
)
from sonolink.rest.errors import HTTPException
from sonolink.rest.schemas.player import (
    PlayerVoiceState,
    UpdatePlayerRequest,
)

from ._base import HandlerBase, _log

__all__ = ()


class EventsHandler(HandlerBase):
    """Internal handler responsible for processing Gateway and Lavalink events."""

    __slots__ = ()

    async def on_voice_server_update(self, data: dict[str, Any]) -> None:
        _log.debug("Received VOICE_SERVER_UPDATE event")
        self._player._connection.token = data.get("token")
        self._player._connection.endpoint = data.get("endpoint")

        # The endpoint might be None; Lavalink needs a string or it will fail.
        # Thus we wait for a non-None endpoint before dispatching.
        if self._player._connection.endpoint:
            await self._dispatch_voice_update()

    async def _dispatch_event(self, data: dict[str, Any]) -> None:
        event_type = data.get("type")
        _log.debug(
            "Player %s receiving event type: %s", self._player.guild.id, event_type
        )

        assert self._player._node is not None
        assert self._player._node._client is not None

        match event_type:
            case "TrackStartEvent":
                payload = msgspec.convert(data, TrackStartEventPayload)

                self._player._paused = False
                self._player._node._client._dispatch(
                    "track_start",
                    self._player,
                    TrackStartEvent(
                        payload,
                        self._player._node,
                        original=self._player._original_track,
                    ),
                )

            case "TrackEndEvent":
                payload = msgspec.convert(data, TrackEndEventPayload)

                if payload.reason != TrackEndReason.REPLACED:
                    self._player._last_position = 0
                    self._player._last_update = 0.0

                original = self._player._original_track

                if payload.reason.can_start_next:
                    try:
                        await self._player.skip()
                    except (QueueEmpty, AutoPlaySeedMissing):
                        pass

                self._player._node._client._dispatch(
                    "track_end",
                    self._player,
                    TrackEndEvent(
                        payload,
                        self._player._node,
                        original=original,
                    ),
                )
                self._player._original_track = None
                self._player._check_inactivity()

            case "TrackExceptionEvent":
                payload = msgspec.convert(data, TrackExceptionEventPayload)
                _log.error(
                    "Track exception in guild %s: %s",
                    self._player.guild.id,
                    payload.exception.message,
                )

                self._player._node._client._dispatch(
                    "track_exception",
                    self._player,
                    TrackExceptionEvent(payload, self._player._node),
                )

            case "TrackStuckEvent":
                payload = msgspec.convert(data, TrackStuckEventPayload)
                _log.warning(
                    "Track stuck in guild %s at %dms",
                    self._player.guild.id,
                    payload.threshold,
                )

                self._player._node._client._dispatch(
                    "track_stuck",
                    self._player,
                    TrackStuckEvent(payload, self._player._node),
                )

            case "Stats":
                payload = msgspec.convert(data, StatsEventPayload)

                self._player._node._client._dispatch(
                    "stats_receive",
                    self._player._node,
                    StatsEvent(payload, self._player._node),
                )

            case "WebSocketClosedEvent":
                payload = msgspec.convert(data, WebSocketClosedEventPayload)

                _log.warning(
                    "Player %s: Lavalink voice WS closed. Code %s, Reason: %s",
                    self._player.guild.id,
                    payload.code,
                    payload.reason,
                )

                # 4014 = Discord terminated the session remotely
                # 4022 = Discord terminated the entire voice session/server remotely
                if payload.code in (4014, 4022):
                    _log.info(
                        "Player %s: Received %d (call terminated remotely), forcing disconnect.",
                        self._player.guild.id,
                        payload.code,
                    )
                    await self._player._lifecycle_handler.disconnect(
                        force=True,
                        trigger=DisconnectTriggerType.ERROR,
                        extra_event_data=payload,
                    )

                elif not payload.by_remote:
                    await self._dispatch_voice_update()

                self._player._node._client._dispatch(
                    "websocket_closed",
                    self._player,
                    WebSocketClosedEvent(payload, self._player._node),
                )

            case _:
                _log.debug(
                    "Player %s received unhandled event type: %s",
                    self._player.guild.id,
                    event_type,
                )
                self._player._node._client._dispatch(
                    "unknown_event",
                    self._player,
                    data,
                )

    def _update_state(self, state: PlayerState, /) -> None:
        self._player._last_position = state.position
        self._player._last_update = time.monotonic()

        _log.debug(
            "Player %s: Synced position to %dms (connected %s)",
            self._player.guild.id,
            state.position,
            state.connected,
        )

    async def on_voice_state_update(self, data: dict[str, Any]) -> None:
        _log.debug("Received VOICE_STATE_UPDATE event")

        channel_id = data.get("channel_id")
        self._player._connection.session_id = data.get("session_id")
        self._player._connection.channel_id = str(channel_id) if channel_id else None

        await self._dispatch_voice_update()
        self._player._check_inactivity()

    async def _dispatch_voice_update(self, retried: bool = False) -> None:
        if not self._player._connection.is_complete or not self._player._node:
            return

        assert self._player._connection.token is not None
        assert self._player._connection.endpoint is not None
        assert self._player._connection.session_id is not None
        assert self._player._connection.channel_id is not None

        if self._player._node._resume_session is None:
            _log.debug("No session ID found, waiting...")
            try:
                await self._player._node._wait_session()
            except RuntimeError:
                _log.warning(
                    "Player %s: Session wait timed out; reconnecting node...",
                    self._player.guild.id,
                )
                await self._player._node.reconnect()
                await self._player._node._wait_session()

        assert self._player._node._resume_session is not None

        voice_state = PlayerVoiceState(
            token=self._player._connection.token,
            endpoint=self._player._connection.endpoint,
            session_id=self._player._connection.session_id,
            channel_id=self._player._connection.channel_id,
        )

        request_data = UpdatePlayerRequest(
            voice=voice_state,
            filters=self._player.filters.payload,
            volume=self._player.volume,
            paused=self._player.paused,
        )

        try:
            await self._player._node._manager.update_player(
                session_id=self._player._node._resume_session,
                guild_id=str(self._player.guild.id),
                data=request_data,
            )
            _log.debug(
                "Player %s: Successfully dispatched voice update to Node %r.",
                self._player.guild.id,
                self._player._node.id,
            )
        except HTTPException as exc:
            if exc.status == 404 and not retried:
                _log.warning(
                    "Player %s: Session not found (404) during voice update — "
                    "node session is stale. Reconnecting and retrying.",
                    self._player.guild.id,
                )
                try:
                    await self._player._node.reconnect()
                    await self._player._node._wait_session()
                except RuntimeError:
                    await self._player._lifecycle_handler.disconnect(
                        force=True,
                        trigger=DisconnectTriggerType.ERROR,
                        extra_event_data=exc,
                    )
                    return
                return await self._dispatch_voice_update(retried=True)

            _log.error(
                "Player %s: Failed to dispatch voice update to Node %r. Error: %s",
                self._player.guild.id,
                self._player._node.id,
                exc,
                exc_info=True,
            )
            return
        except Exception as exc:
            _log.error(
                "Player %s: Unexpected error during voice update to Node %r. Error: %s",
                self._player.guild.id,
                self._player._node.id,
                exc,
                exc_info=True,
            )
            return

        self._player._connection._connected_flag.set()
        _log.debug("Successfully completed connection on player %r", self._player)

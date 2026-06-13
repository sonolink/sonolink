"""
MIT License

Copyright (c) 2026-present SonoLink Development Team.

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

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal

from sonolink.gateway.cache import LFUCache
from sonolink.gateway.enums import NodeRegion, NodeStatus, QueueMode
from sonolink.gateway.player._factory import PlayerFactory
from sonolink.models.filters import Filters
from sonolink.models.info import ServerInfo
from sonolink.models.player_info import PlayerInfo
from sonolink.models.responses import SearchResult
from sonolink.models.settings import (
    AutoPlaySettings,
    CacheSettings,
    HistorySettings,
    InactivitySettings,
)
from sonolink.models.track import Playable
from sonolink.rest.enums import TrackSourceType
from sonolink.rest.schemas.info import StatsResponse

from ._connection import ConnectionManager
from ._events import EventRouter
from ._players import PlayerRegistry
from ._rest import HTTPClient
from ._websocket import WebsocketClient

if TYPE_CHECKING:
    from sonolink.gateway.client import Client
    from sonolink.gateway.player import BasePlayer, Player
    from sonolink.network import BaseWebsocketManager, SessionType

_log = logging.getLogger(__name__)

__all__ = ("Node",)


class Node:
    """
    Represents a connectable Node.

    Parameters
    ----------
    client: :class:`sonolink.Client`
        The SonoLink client this node is attached to.
    uri: :class:`str`
        The base URI for the Lavalink node. Do not include REST or websocket routes.
    password: :class:`str`
        The Lavalink server password used for both HTTP and websocket authentication.
    id: :class:`str` | :data:`None`
        The identifier used to track this node inside the client. If ``None`` is passed,
        a random identifier is generated.
    retries: :class:`int` | :data:`None`
        How many reconnect attempts should be made before the node gives up. If ``None``
        is passed, reconnect attempts are unlimited.
    resume_timeout: :class:`float`
        The number of seconds Lavalink should keep a resumable session alive.
    cache_settings: :class:`sonolink.models.CacheSettings` | :data:`None`
        Settings used for the node's search-result cache. If ``None`` is passed, default
        cache settings are used.
    inactivity_settings: :class:`sonolink.models.InactivitySettings`
        Default inactivity behavior applied to players managed by this node.
    session: ``aiohttp.ClientSession`` | ``curl_cffi.AsyncSession`` | :data:`None`
        Optional pre-existing HTTP session to reuse for this node's REST and websocket
        transport. If ``None`` is passed, the library creates one.
    auto_reconnect: :class:`bool`
        Whether the node should attempt to reconnect automatically after an unexpected
        disconnect.
    regions: :class:`list[str | NodeRegion]` | :data:`None`
        The regions of this node. This is used to determine the best node to use based on
        the channel region. If ``None`` is passed, the node is considered to have no specific region.

        .. versionadded:: 1.2.0
    """

    retries: int | None
    """The amount of retries to attempt when connecting or reconnecting this node."""
    resume_timeout: float
    """The maximum amount of seconds a resume can take before closing the node."""

    _id: str
    _ws: BaseWebsocketManager[Any, Any] | None
    _uri: str
    _password: str
    _client: Client[Any] | None
    _keep_alive: asyncio.Task[None] | None
    _resume_session: str | None
    _stats: StatsResponse | None

    def __init__(
        self,
        *,
        client: Client[Any],
        uri: str,
        password: str,
        id: str | None = None,
        retries: int | None = None,
        resume_timeout: float = 60,
        cache_settings: CacheSettings | None = None,
        inactivity_settings: InactivitySettings,
        session: SessionType | None = None,
        auto_reconnect: bool = True,
        regions: list[str | NodeRegion] | None = None,
    ) -> None:
        self._client = client
        self._id = id or os.urandom(16).hex()
        self._uri = uri.removesuffix("/")
        self._password = password

        self.retries = retries
        self.resume_timeout = resume_timeout
        self.auto_reconnect = auto_reconnect

        self._status: NodeStatus = NodeStatus.DISCONNECTED
        self._is_reconnecting = False
        self._resume_session = None
        self._ready_event = asyncio.Event()
        self._ws = None
        self._keep_alive = None
        self._stats = None

        self._players: dict[int, BasePlayer] = {}
        self._player_factory = PlayerFactory()
        self._inactivity_settings = inactivity_settings
        self._waiting_to_disconnect: dict[int, asyncio.Task[None]] = {}

        self.regions = regions or []

        self._cache: LFUCache[str, Any] = LFUCache(settings=cache_settings)
        self._connection = ConnectionManager(self)
        self._events = EventRouter(self)
        self._ws_client = WebsocketClient(self)
        self._rest = HTTPClient(self)
        self._player_registry = PlayerRegistry(self)
        self._manager = self._rest.init_manager(session)

    def __repr__(self) -> str:
        return f"<Node id={self._id} status={self._status.name} players={len(self._players)} uri={self._uri}>"

    def _ensure_client(self) -> Client[Any]:
        if not self._client:
            raise RuntimeError(
                "Cannot perform HTTP requests without an attached client."
            )
        return self._client

    async def _wait_session(self) -> bool:
        try:
            return await asyncio.wait_for(self._ready_event.wait(), timeout=10.0)
        except TimeoutError:
            raise RuntimeError("Timed out waiting for node READY payload.")

    @property
    def client(self) -> Client[Any] | None:
        """The client this node is attached to."""
        return self._client

    @property
    def id(self) -> str:
        """The ID of this node."""
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        if self._client is not None:
            raise RuntimeError("Node IDs can not be changed when bound to a client.")
        self._id = value

    @property
    def is_connected(self) -> bool:
        """Whether the Node is connected and Players can be attached to it."""
        return self._status is NodeStatus.CONNECTED

    @property
    def inactivity_settings(self) -> InactivitySettings:
        """The inactivity configuration for all players on this node."""
        return self._inactivity_settings

    @property
    def regions(self) -> list[str | NodeRegion]:
        """The regions for this node.

        .. versionadded:: 1.2.0
        """
        return self._regions

    @regions.setter
    def regions(self, value: list[str | NodeRegion]) -> None:
        self._regions = [r.removeprefix("vip-") if isinstance(r, str) else r for r in value]

    @property
    def password(self) -> str:
        """The password of the node."""
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self._password = value
        self._manager.update_headers({"Authorization": value})

    @property
    def stats(self) -> StatsResponse | None:
        """The latest stats received from the Lavalink node."""
        return self._stats

    @property
    def session_id(self) -> str:
        """
        The current session ID for this node.

        Raises
        ------
        RuntimeError
            The node is not connected or has no active session.
        """
        if not self._resume_session:
            raise RuntimeError(f"Node {self._id!r} is not connected (no session ID).")
        return self._resume_session

    @property
    def uri(self) -> str:
        """The URI this node connects to. This can only be changed while the node is disconnected."""
        return self._uri

    @uri.setter
    def uri(self, value: str) -> None:
        if self._status is not NodeStatus.DISCONNECTED:
            raise RuntimeError("Cannot update the node uri while it is connected.")
        self._uri = value

    async def connect(self) -> None:
        """
        Connects this node.

        This can only be done when the node has been attached to a pool.
        """
        await self._connection.connect()

    async def reconnect(self) -> None:
        """
        Reconnects this node.

        This can only be done when the node has been attached to a pool.

        .. versionadded:: 1.2.0
        """
        await self._connection.reconnect()

    async def close(self) -> None:
        """
        Closes the connection to this node.

        All Players connected to it will stop playing.

        This also closes all HTTP and WS sessions and connections.

        This dispatches a ``on_node_close`` event.
        """
        await self._connection.close()

    def create_player(
        self,
        *,
        volume: int | None = None,
        paused: bool | None = None,
        filters: Filters | None = None,
        queue_mode: QueueMode = QueueMode.NORMAL,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
    ) -> Player:
        """
        Creates a player with extra configuration bound to this node.

        Parameters
        ----------
        volume: :class:`int` | :data:`None`
            The volume of the player, in percentage from 0 to 1000. Defaults to ``None``.
        paused: :class:`bool` | :data:`None`
            Whether the player should start paused. Defaults to ``None``.
        filters: :class:`Filters` | :data:`None`
            The filters to apply to the player. Defaults to ``None``.
        queue_mode: :class:`QueueMode`
            The playback strategy for the queue. Defaults to :attr:`QueueMode.NORMAL`.
        autoplay_settings: :class:`AutoPlaySettings` | :data:`None`
            The autoplay settings to set to this player. Defaults to ``None``.
        history_settings: :class:`HistorySettings` | :data:`None`
            The history settings to set to this player. Defaults to ``None``.

        Returns
        -------
        :class:`Player`
            The player. This can be passed to the ``cls=`` kwarg on

            - :meth:`discord:discord.abc.Connectable.connect` (discord.py)
            - :meth:`pycord:discord.VoiceChannel.connect` (py-cord)
            - :meth:`disnake:disnake.VoiceChannel.connect` (disnake)
            - :meth:`nextcord:nextcord.VoiceChannel.connect` (nextcord)
        """
        return self._player_registry.create_player(
            volume=volume,
            paused=paused,
            filters=filters,
            queue_mode=queue_mode,
            autoplay_settings=autoplay_settings,
            history_settings=history_settings,
        )

    async def search_track(
        self,
        query: str,
        *,
        source: TrackSourceType | str | None = None,
    ) -> SearchResult:
        """
        Searches for ``query`` in this Node.

        Parameters
        ----------
        query: :class:`str`
            The query to search. This can be a full URL, or headed by hosts specified by any plugin.
        source: :class:`TrackSourceType` | :class:`str` | :data:`None`
            The source to search from. This is, essentially, providing a host to ``query``. The library
            provides default source types under :class:`TrackSourceType`, but custom ones can be passed
            with a raw string.

        Returns
        -------
        :class:`SearchResult`
            The search result.
        """
        return await self._rest.search_track(query, source=source)

    async def decode_track(self, encoded: str) -> Playable:
        """
        Decodes a track from its encoded data.

        When a track is fetched, the encoded data can be found under
        :attr:`sonolink.rest.schemas.Track.encoded`.

        Parameters
        ----------
        encoded: :class:`str`
            The encoded data to resolve the track from.

        Returns
        -------
        :class:`sonolink.models.Playable`
            The decoded resolved track.
        """
        return await self._rest.decode_track(encoded)

    async def decode_tracks(self, *encoded: str) -> list[Playable]:
        """
        Bulk decodes encoded tracks.

        Parameters
        ----------
        *encoded: :class:`str`
            The encoded data for each track to be decoded.

        Returns
        -------
        ``list[Playable]``
            The decoded resolved tracks.
        """
        return await self._rest.decode_tracks(*encoded)

    async def fetch_info(self) -> ServerInfo:
        """
        Fetches the Lavalink server info this node is connected to.

        Returns
        -------
        :class:`sonolink.models.ServerInfo`
            The server info.
        """
        return await self._rest.fetch_info()

    async def fetch_players(self) -> list[PlayerInfo]:
        """
        Fetches all the players that are connected to this node.

        This performs a fresh REST request for the current player states on the node.

        Returns
        -------
        ``list[PlayerInfo]``
            The players connected to this node.
        """
        return await self._rest.fetch_players()

    async def fetch_player(self, guild_id: int) -> PlayerInfo:
        """
        Fetches a player from this node connected to the provided guild ID.

        Usually, you should use :attr:`Node.get_player` instead of this method.

        Parameters
        ----------
        guild_id: :class:`int`
            The guild ID the player is connected to.

        Returns
        -------
        :class:`PlayerInfo`
            The player connected to the guild ID.
        """
        return await self._rest.fetch_player(guild_id)

    async def disconnect_player(self, guild_id: int) -> None:
        """
        Force disconnects a player from this node connected to the provided guild ID.

        Parameters
        ----------
        guild_id: :class:`int`
            The guild ID to disconnect the player from.
        """
        await self._rest.disconnect_player(guild_id)

    def get_player(self, guild_id: int, /) -> BasePlayer | None:
        """Gets a player connected to this node."""
        return self._player_registry.get_player(guild_id)

    async def send(
        self,
        method: Literal["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: Any | None = None,
    ) -> dict[str, Any] | list[Any] | str | bytes | None:
        """Method for doing manual requests to the Lavalink node.

        .. warning::

            Usually you wouldn't use this method. Please use the built in methods of :class:`~sonolink.Client`,
            :class:`~sonolink.Node` and :class:`~sonolink.Player`, unless you need to send specific plugin data
            to Lavalink.

            Using this method may have unwanted side effects on your players and/or nodes.

        Parameters
        ----------
        method: :class:`str` | :data:`None`
            The method to use when making this request. Available methods are "GET", "POST", "PATCH",
            "PUT", "DELETE" and "OPTIONS". Defaults to "GET".
        path: str
            The path to make this request to. E.g. "stats", which will translate to "/v4/stats".
            Do not include the base URI of the node here or the "/v4" prefix.
        headers: :class:`~collections.abc.Mapping` | :data:`None`
            An optional dict of headers to send with this request. This is merged with the default
            headers used for the node, so you don't have to include authentication headers here. E.g. ``{"X-Thing": "Value"}``.
        params: :class:`~collections.abc.Mapping` | :data:`None`
            An optional dict of query parameters to send with your request. If you include your query
            parameters in the ``path`` parameter, do not pass them here as well. E.g. ``{"thing": 1, "other": 2}``
            would equate to "?thing=1&other=2".
        json: :class:`dict` | :data:`None`
            The optional JSON data to send along with your request.
        data: :class:`~typing.Any` | :data:`None`
            The optional data to send along with your request.

        Returns
        -------
        :class:`dict` | :class:`list` | :class:`str` | :class:`bytes` | :data:`None`
            The response body returned by Lavalink, if any. This can be a dict (if the response is a JSON object),
            a list (if the response is a JSON array), a string (if the response is text) or bytes (if the response is binary).
            If the response has no body or the request is out of lavalink's control, ``None`` is returned.

        Raises
        ------
        :exc:`msgspec.DecodeError`
            The response body could not be decoded.
        :exc:`sonolink.HTTPException`
            An error occurred while making the request.
        """
        return await self._rest.send(
            method,
            path,
            headers=headers,
            params=params,
            json=json,
            data=data,
        )

    async def cleanup(self) -> None:
        """
        A function that may be overridden in order to add custom clean-up
        logic to a node.

        This is automatically called by the library.
        """
        ...

    def _add_player(self, player: BasePlayer) -> None:
        """Internal helper to register a player to this node."""
        self._player_registry.add_player(player)

    def _remove_player(self, guild_id: int) -> None:
        """Internal helper to unregister a player from this node."""
        self._player_registry.remove_player(guild_id)

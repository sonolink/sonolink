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
from typing import TYPE_CHECKING, Any, Generic, Literal, overload

from typing_extensions import TypeVar

from sonolink import _registry
from sonolink._version import __version__
from sonolink.gateway.enums import NodeRegion, NodeStrategy
from sonolink.gateway.player import FrameworkLiteral, PlayerFactory
from sonolink.models.settings import CacheSettings, InactivitySettings
from sonolink.rest.enums import TrackSourceType

from ..node import Node
from ._base import DiscordClient
from ._factory import ClientFactory

if TYPE_CHECKING:
    from sonolink.models.responses import SearchResult
    from sonolink.models.track import Playable
    from sonolink.network import SessionType

    from .adapters._disnake import DisnakeClientProto
    from .adapters._dpy import DpyClientProto
    from .adapters._nextcord import NextcordClientProto
    from .adapters._pycord import PycordClientProto


__all__ = ("Client",)

_log = logging.getLogger(__name__)


N = TypeVar("N", bound=Node, default=Node)


class Client(Generic[N]):
    """
    Represents a SonoLink client.

    A client helps you manage all Node connections and players.

    Parameters
    ----------
    client: :class:`discord:discord.Client` (discord.py) | :class:`pycord:discord.Client` (py-cord) | :class:`disnake:disnake.Client`
        The Discord client this SonoLink client is attached to.
    node_cls: ``type[Node]``
        The class to use when creating new nodes. Defaults to :class:`Node`.
    framework: :class:`str` | :data:`None`
        The Discord framework to use. Accepted values are ``"discord.py"``,
        ``"pycord"``, ``"disnake"`` and ``"nextcord"``. When ``None``, the
        framework is detected automatically from whichever library is installed.
        If no supported framework is found, a :exc:`RuntimeError` is raised.
        If multiple are present, the one already imported is preferred; if that
        is ambiguous, the first available is used and a warning is logged.
        Defaults to ``None``.
    node_strategy: :class:`NodeStrategy`
        The strategy used to select a node for new players. Defaults to :attr:`NodeStrategy.BY_PENALTY`.

    Raises
    ------
    RuntimeError
        No supported Discord framework meeting the minimum version requirements
        was found, or a ``sonolink.Client`` is already attached to the given
        Discord client.
    """

    _framework: FrameworkLiteral
    _nodes: dict[str, N]
    _session: SessionType | None
    _node_tasks: dict[str, asyncio.Task[Any]]

    @overload
    def __init__(
        self,
        client: DpyClientProto,
        *,
        node_cls: type[N] = ...,
        framework: Literal["discord.py"] = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        client: PycordClientProto,
        *,
        node_cls: type[N] = ...,
        framework: Literal["pycord"] = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        client: DisnakeClientProto,
        *,
        node_cls: type[N] = ...,
        framework: Literal["disnake"] = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        client: NextcordClientProto,
        *,
        node_cls: type[N] = ...,
        framework: Literal["nextcord"] = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        client: Any,
        *,
        node_cls: type[N] = ...,
        framework: None = ...,
    ) -> None: ...

    def __init__(
        self,
        client: Any,
        *,
        node_cls: type[N] = Node,
        framework: FrameworkLiteral | None = None,
        node_strategy: NodeStrategy = NodeStrategy.PENALTY,
    ) -> None:
        framework = framework or PlayerFactory().detect_framework()
        os.environ["SONOLINK_FRAMEWORK"] = framework

        self._client: DiscordClient[Any] = ClientFactory.create(client, framework)

        self._framework = framework
        self._nodes = {}
        self._session = None
        self._node_tasks = {}
        self._node_cls: type[N] = node_cls
        self._node_strategy = node_strategy

        if self._client._client in _registry.clients:
            raise RuntimeError(
                f"sonolink.Client already attached to this {framework}.Client"
            )

        _registry.clients[self._client._client] = self

    def __repr__(self) -> str:
        return f"<sonolink.Client nodes={len(self._nodes)}>"

    @property
    def nodes(self) -> list[N]:
        """The active nodes attached to this client."""
        return list(self._nodes.values())

    @property
    def framework(self) -> FrameworkLiteral:
        """
        The Discord framework used by this client
        (``"discord.py"``, ``"pycord"``, ``"disnake"``, or ``"nextcord"``).
        """
        return self._framework

    @property
    def node_strategy(self) -> NodeStrategy:
        """The strategy used to select a node for new players."""
        return self._node_strategy

    @node_strategy.setter
    def node_strategy(self, strategy: NodeStrategy) -> None:
        """Set the strategy used to select a node for new players."""
        self._node_strategy = strategy

    @overload
    def create_node(
        self,
        *,
        host: str,
        port: int,
        password: str,
        id: str | None = ...,
        retries: int | None = ...,
        resume_timeout: float = 60.0,
        cache_settings: CacheSettings | None = ...,
        inactivity_settings: InactivitySettings | None = ...,
        session: SessionType | None = ...,
        regions: list[str | NodeRegion] | None = ...,
    ) -> N: ...

    @overload
    def create_node(
        self,
        *,
        uri: str,
        password: str,
        id: str | None = ...,
        retries: int | None = ...,
        resume_timeout: float = 60.0,
        cache_settings: CacheSettings | None = ...,
        inactivity_settings: InactivitySettings | None = ...,
        session: SessionType | None = ...,
        regions: list[str | NodeRegion] | None = ...,
    ) -> N: ...

    def create_node(
        self,
        *,
        password: str,
        uri: str | None = None,
        host: str | None = None,
        port: int | None = None,
        id: str | None = None,
        retries: int | None = None,
        resume_timeout: float = 60.0,
        cache_settings: CacheSettings | None = None,
        inactivity_settings: InactivitySettings | None = None,
        session: SessionType | None = None,
        auto_reconnect: bool = True,
        regions: list[str | NodeRegion] | None = None,
    ) -> N:
        """
        Creates a :class:`Node` attached to this client.

        Parameters
        ----------
        password: :class:`str`
            The password of the node.
        uri: :class:`str` | :data:`None`
            The URI the node will connect to. You should only provide the base URI without
            any routes, as the library will do it for you. This is mutually exclusive with providing ``host`` and ``port``.

            .. versionchanged:: 1.1.0
                This is optional now to accommodate users who prefer providing host and port separately.
        host: :class:`str` | :data:`None`
            The host of the node. This is mutually exclusive with providing ``uri``.

            .. versionadded:: 1.1.0
        port: :class:`int` | :data:`None`
            The port of the node. This is mutually exclusive with providing ``uri``.

            .. versionadded:: 1.1.0
        id: :class:`str` | :data:`None`
            The ID of this node. This is used internally to identify this node. If ``None`` is passed, it is
            generated automatically.
        retries: :class:`int` | :data:`None`
            The amount of retries to attempt when connecting or reconnecting this node. Whenever the limit
            is reached, it closes the node automatically. If this is set to ``None``, it retries indefinitely.
            Defaults to ``None``.
        resume_timeout: :class:`float`
            The maximum amount of seconds a resume can take before closing the node. Defaults to ``60.0``.
        cache_settings: :class:`CacheSettings` | :data:`None`
            The search result caching configuration.
            Defaults to ``CacheSettings.default()``.
        inactivity_settings: :class:`InactivitySettings` | :data:`None`
            The inactivity configuration for all players connected to this node.
            If ``None`` is passed, it uses ``InactivitySettings.default()``.
        session: ``aiohttp.ClientSession`` | ``curl_cffi.AsyncSession`` | :data:`None`
            The session this node should use. If ``None`` is provided, creates one. Defaults to ``None``.
        auto_reconnect: :class:`bool`
            Whether the node should attempt to reconnect automatically after an unexpected
            disconnect. Defaults to ``True``.

            .. versionadded:: 1.2.0
        regions: :class:`list[str | NodeRegion]` | :data:`None`
            The regions of this node. This is used to determine the best node to use based on
            the channel region. If ``None`` is passed, the node is considered to have no specific region.

        Raises
        ------
        ValueError
            Invalid combination of parameters. You must provide either
            ``uri`` or both ``host`` and ``port``, but not all three.

        Returns
        -------
        :class:`Node`
            The node that was created.
        """
        if (uri is not None) and (host is not None or port is not None):
            msg = "Cannot specify both uri and host/port."
            raise ValueError(msg)

        if (uri is None) and (host is None or port is None):
            msg = "Must specify either uri or host and port."
            raise ValueError(msg)

        i_settings = inactivity_settings or InactivitySettings.default()
        c_settings = cache_settings or CacheSettings.default()
        uri = uri or f"{host}:{port}"

        node = self._node_cls(
            client=self,
            uri=uri,
            password=password,
            id=id,
            retries=retries,
            resume_timeout=resume_timeout,
            cache_settings=c_settings,
            inactivity_settings=i_settings,
            session=session,
            auto_reconnect=auto_reconnect,
            regions=regions,
        )
        self._nodes[node.id] = node
        return node

    def get_node(self, id: str, /) -> N | None:
        """
        Retrieves a :class:`Node` by its ID.

        .. versionadded:: 1.1.0

        Parameters
        ----------
        id: :class:`str`
            The ID of the node to retrieve.

        Returns
        -------
        :class:`Node` | :data:`None`
            The node if found, otherwise ``None``.
        """
        return self._nodes.get(id)

    def remove_node(self, identifier: str, /) -> None:
        """
        Removes a Node from this client.

        Parameters
        ----------
        identifier: :class:`str`
            The ID of the node to remove.
        """

        try:
            node = self._nodes.pop(identifier)
        except KeyError:
            pass
        else:
            self._cleanup_node(node)

    def clear_nodes(self) -> None:
        """Clears all Nodes from this Client."""

        for node in self.nodes:
            self.remove_node(node.id)

    async def start(self) -> None:
        """
        Connects all registered nodes to their respective Lavalink servers.

        This method should typically be called after the discord client is logged in,
        often within the ``setup_hook`` (discord.py) or ``on_connect`` (py-cord, disnake and nextcord) event.
        """
        if not self._nodes:
            return

        for node in self.nodes:
            if node.is_connected:
                continue

            try:
                await node.connect()
            except Exception as exc:
                _log.exception(
                    "Ignoring exception while connecting Node %r", node, exc_info=exc
                )
                continue

    async def close(self) -> None:
        """
        Gracefully closes all :class:`Node` connections and cleans up internal resources.

        This will stop all active players and close the underlying websocket and HTTP sessions.
        """

        for node in self.nodes:
            if not node.is_connected:
                continue

            try:
                await node.close()
            except Exception as exc:
                _log.exception(
                    "Ignoring exception while closing Node %r", node, exc_info=exc
                )
                continue

        self._nodes.clear()

    def get_best_node(self, *, region: str | None = None) -> N:
        """
        Returns the best available :class:`Node` based on current load and connectivity.

        Parameters
        ----------
        region: :class:`str` | :data:`None`
            An optional voice region string. When provided and ``node_strategy`` is set to
            :attr:`NodeStrategy.REGION`, this is used to select the best matching node.
            If ``None``, omitted, or no matching regional node is found, selection falls back to
            penalty-based scoring.

        Returns
        -------
        :class:`Node`
            The node with the lowest penalty that is currently connected.

        Raises
        ------
        RuntimeError
            No nodes are currently connected to handle the request.
        """
        connected_nodes = [node for node in self.nodes if node.is_connected]
        if not connected_nodes:
            raise RuntimeError("No nodes are currently connected.")

        nodes_to_consider = connected_nodes

        if self.node_strategy is NodeStrategy.REGION and region is not None:
            normalized = region.removeprefix("vip-")
            nodes_to_consider = [
                node
                for node in connected_nodes
                if node.regions and normalized in node.regions
            ]

        return min(
            nodes_to_consider or connected_nodes,
            key=lambda node: node.stats.penalty if node.stats else float("inf"),
        )

    async def search_track(
        self,
        query: str,
        *,
        source: TrackSourceType | str = TrackSourceType.YOUTUBE,
        region: str | None = None,
    ) -> SearchResult:
        """
        Searches for ``query`` in the best Node available, obtained with :meth:`Client.get_best_node`.

        Parameters
        ----------
        query: :class:`str`
            The query to search. This can be a full URL, or headed by hosts specified by any plugin.
        source: :class:`TrackSourceType` | :class:`str`
            The source to search from. This is, essentially, providing a host to ``query``. The library
            provides default source types under :class:`TrackSourceType`, but custom ones can be passed
            with a raw string.
        region: :class:`str` | :data:`None`
            An optional voice region string. When provided and ``node_strategy`` is set to
            :attr:`NodeStrategy.REGION`, this is used to select the best matching node.
            If ``None``, omitted, or no matching regional node is found, selection falls back to
            penalty-based scoring.

        Returns
        -------
        :class:`SearchResult`
            The search result.
        """
        node = self.get_best_node(region=region)
        return await node.search_track(query, source=source)

    async def decode_track(
        self,
        encoded: str,
        *,
        region: str | None = None,
    ) -> Playable:
        """
        Decodes a track from its encoded data using the best Node available, obtained with
        :meth:`Client.get_best_node`.

        When a track is fetched, the encoded data can be found under
        :attr:`sonolink.rest.schemas.Track.encoded`.

        Parameters
        ----------
        encoded: :class:`str`
            The encoded data to resolve the track from.
        region: :class:`str` | :data:`None`
            An optional voice region string. When provided and ``node_strategy`` is set to
            :attr:`NodeStrategy.REGION`, this is used to select the best matching node.
            If ``None``, omitted, or no matching regional node is found, selection falls back to
            penalty-based scoring.

        Returns
        -------
        :class:`sonolink.models.Playable`
            The decoded resolved track.
        """
        node = self.get_best_node(region=region)
        return await node.decode_track(encoded)

    async def decode_tracks(
        self,
        *encoded: str,
        region: str | None = None,
    ) -> list[Playable]:
        """
        Bulk decode encoded tracks using the best Node available, obtained with :meth:`Client.get_best_node`.

        Parameters
        ----------
        *encoded: :class:`str`
            The encoded data for each track to be decoded.
        region: :class:`str` | :data:`None`
            An optional voice region string. When provided and ``node_strategy`` is set to
            :attr:`NodeStrategy.REGION`, this is used to select the best matching node.
            If ``None``, omitted, or no matching regional node is found, selection falls back to
            penalty-based scoring.

        Returns
        -------
        ``list[Playable]``
            The decoded resolved tracks.
        """
        node = self.get_best_node(region=region)
        return await node.decode_tracks(*encoded)

    def _cleanup_node(self, node: N) -> asyncio.Task[None]:
        if node.id in self._node_tasks:
            return self._node_tasks[node.id]

        task = asyncio.create_task(node.close(), name=f"sonolink:node-close:{node.id}")
        self._node_tasks[node.id] = task

        task.add_done_callback(lambda _: self._node_tasks.pop(node.id, None))
        return task

    def _dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        self._client.dispatch(f"sonolink_{event}", *args, **kwargs)

    def _build_ws_headers(self) -> dict[str, str]:
        if self._client.user is None:
            raise RuntimeError(
                "Cannot connect Nodes without the underlying client running."
            )

        return {
            "User-Id": str(self._client.user.id),
            "Client-Name": f"sonolink/{__version__}",
        }

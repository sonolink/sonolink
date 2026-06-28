"""
sonolink.rest.http
~~~~~~~~~~~~~~~~~~
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from sonolink.network import HTTPFactory
from sonolink.network.base import BaseHTTPManager, BaseWebsocketManager

from .info import InfoHTTPMixin
from .planner import RoutePlannerHTTPMixin
from .player import PlayerHTTPMixin
from .session import SessionHTTPMixin
from .track import TrackHTTPMixin

_log = logging.getLogger(__name__)

__all__ = ("RESTClient",)


class RESTClient(
    InfoHTTPMixin,
    RoutePlannerHTTPMixin,
    PlayerHTTPMixin,
    SessionHTTPMixin,
    TrackHTTPMixin,
):
    def __init__(
        self,
        manager: BaseHTTPManager[Any],
        *,
        base_url: str = "",
        headers: dict[str, str] | None = None,
    ) -> None:
        self._manager = manager
        self._base_url = base_url.removesuffix("/")
        self._default_headers = headers or {}

    async def __aenter__(self) -> RESTClient:
        await self.setup()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    def update_headers(self, headers: dict[str, str]) -> None:
        self._default_headers.update(headers)

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> Any:
        merged_headers = {**self._default_headers, **(headers or {})}
        full_url = self._build_full_url(url)
        _log.debug(
            "HTTP send %s %s (params=%s) %s with data json=%s ; data=%s",
            method,
            url,
            params,
            headers,
            json,
            data,
        )
        ret = await self._manager.request(
            method,
            full_url,
            headers=merged_headers or None,
            params=params,
            json=json,
            data=data,
        )
        _log.debug("HTTP receive %s %s with response %r", method, url, ret)
        return ret

    async def connect_ws(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> BaseWebsocketManager[Any, Any]:
        if not self._manager._session:
            raise RuntimeError("Cannot create websocket without a manager session")

        merged_headers = {**self._default_headers, **(headers or {})}
        full_url = self._build_ws_url(url)
        ws = HTTPFactory.create_websocket(self._manager._session)
        await ws.connect(full_url, headers=merged_headers)
        return ws

    def _build_full_url(self, url: str) -> str:
        return self._base_url + "/v4" + url if url.startswith("/") else url

    def _build_ws_url(self, url: str) -> str:
        is_secure = self._base_url.startswith("https://")
        ws_prefix = "wss://" if is_secure else "ws://"
        base = self._base_url.removeprefix("https://").removeprefix("http://")
        return ws_prefix + base + url if url.startswith("/") else url

    async def setup(self) -> None:
        await self._manager.setup()

    async def close(self) -> None:
        await self._manager.close()

    @property
    def is_closed(self) -> bool:
        return self._manager.is_closed

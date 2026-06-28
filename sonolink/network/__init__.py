"""sonolink.http
~~~~~~~~~~~~~~~~
"""

from __future__ import annotations

import importlib.util
from typing import TYPE_CHECKING, Any, cast

import aiohttp
from typing_extensions import TypeIs

from .base import BaseHTTPManager, BaseWebsocketManager

if TYPE_CHECKING:
    import curl_cffi
    # curl_cffi is only available with the [speed] extra

    SessionType = curl_cffi.AsyncSession[curl_cffi.Response] | aiohttp.ClientSession
    WebsocketType = curl_cffi.AsyncWebSocket | aiohttp.ClientWebSocketResponse


__all__ = (
    "BaseHTTPManager",
    "BaseWebsocketManager",
    "HTTPFactory",
)


class HTTPFactory:
    """HTTP/Websocket selector and factory."""

    HAS_CURL: bool = importlib.util.find_spec("curl_cffi") is not None

    @staticmethod
    def _select(curl_name: str, aiohttp_name: str) -> object:
        if HTTPFactory.HAS_CURL:
            module = __import__("sonolink.network._curl_cffi", fromlist=[curl_name])
            return getattr(module, curl_name)

        module = __import__("sonolink.network._aiohttp", fromlist=[aiohttp_name])
        return getattr(module, aiohttp_name)

    @classmethod
    def http_manager(cls) -> type[BaseHTTPManager[Any]]:
        return cast(
            type["BaseHTTPManager[Any]"],
            cls._select("CurlHTTPManager", "AioHTTPManager"),
        )

    @classmethod
    def websocket_manager(cls) -> type[BaseWebsocketManager[Any, Any]]:
        return cast(
            type["BaseWebsocketManager[Any, Any]"],
            cls._select("CurlWebsocketManager", "AioWebsocketManager"),
        )

    @staticmethod
    def _is_aiohttp_session(session: SessionType) -> TypeIs[aiohttp.ClientSession]:
        return isinstance(session, aiohttp.ClientSession)

    @classmethod
    def _is_ccffi_session(
        cls, session: SessionType
    ) -> TypeIs[curl_cffi.AsyncSession[curl_cffi.Response]]:
        if cls.HAS_CURL:
            import curl_cffi

            return isinstance(session, curl_cffi.AsyncSession)
        return False

    @classmethod
    def from_http(cls, session: SessionType) -> BaseHTTPManager[Any]:
        if cls._is_aiohttp_session(session):
            from ._aiohttp import AioHTTPManager

            return AioHTTPManager(session=session)

        from ._curl_cffi import CurlHTTPManager

        return CurlHTTPManager(session=session)

    @classmethod
    def create_websocket(cls, session: SessionType) -> BaseWebsocketManager[Any, Any]:
        if cls._is_aiohttp_session(session):
            from ._aiohttp import AioWebsocketManager

            return AioWebsocketManager(session)

        from ._curl_cffi import CurlWebsocketManager

        return CurlWebsocketManager(session)

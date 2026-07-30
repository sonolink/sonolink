from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from ..errors import FrameworkClientMismatch, FrameworkImportError
from ._base import DiscordClient

if TYPE_CHECKING:
    from sonolink.gateway.player import FrameworkLiteral


class ClientFactory:
    __slots__ = ()

    @staticmethod
    def create(client: Any, framework: FrameworkLiteral) -> DiscordClient[Any]:
        try:
            match framework:
                case "discord.py":
                    from .adapters._dpy import DpyClient as Client
                case "pycord":
                    from .adapters._pycord import PycordClient as Client
                case "disnake":
                    from .adapters._disnake import DisnakeClient as Client
                case "nextcord":
                    from .adapters._nextcord import NextcordClient as Client
                case _:  # pyright: ignore[reportUnnecessaryComparison]
                    raise ValueError(f"Unsupported framework: {framework}")

            adapter_cls = cast("type[DiscordClient[Any]]", Client)
            expected_type = adapter_cls.cls
            if not isinstance(client, expected_type):
                raise FrameworkClientMismatch(
                    expected_type=expected_type,
                    received_type=cast(type[Any], type(client)),
                    framework=framework,
                )
            return adapter_cls(client)
        except (ImportError, ModuleNotFoundError):
            raise FrameworkImportError(framework=framework) from None

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast, overload

from ..errors import FrameworkClientMismatch, FrameworkImportError
from ._base import DiscordClient

if TYPE_CHECKING:
    from sonolink.gateway.player import FrameworkLiteral

    from .adapters._disnake import DisnakeClient
    from .adapters._dpy import DpyClient
    from .adapters._nextcord import NextcordClient
    from .adapters._pycord import PycordClient


class ClientFactory:
    __slots__ = ()

    @overload
    @staticmethod
    def create(client: Any, framework: Literal["discord.py"]) -> DpyClient: ...

    @overload
    @staticmethod
    def create(client: Any, framework: Literal["pycord"]) -> PycordClient: ...

    @overload
    @staticmethod
    def create(client: Any, framework: Literal["disnake"]) -> DisnakeClient: ...

    @overload
    @staticmethod
    def create(client: Any, framework: Literal["nextcord"]) -> NextcordClient: ...

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
            received_type: type[Any] = type(client)  # pyright: ignore[reportUnknownVariableType]

            if not isinstance(client, expected_type):
                raise FrameworkClientMismatch(
                    expected_type=expected_type,
                    received_type=received_type,
                    framework=framework,
                )
            return adapter_cls(client)
        except (ImportError, ModuleNotFoundError):
            raise FrameworkImportError(framework=framework) from None

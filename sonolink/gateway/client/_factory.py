"""Apache License 2.0

Copyright (c) 2026-present SonoLink Development Team.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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

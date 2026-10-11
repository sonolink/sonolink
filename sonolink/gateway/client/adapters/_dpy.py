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

from typing import Any, ClassVar, Protocol

import discord

from .._base import DiscordClient

__all__ = (
    "DpyClient",
    "DpyClientProto",
)


class DpyClientProto(Protocol):
    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None: ...

    @property
    def user(self) -> discord.ClientUser | None: ...


class DpyClient(DiscordClient[discord.Client]):
    __slots__ = ()
    cls: ClassVar[type[discord.Client]] = discord.Client

    def dispatch(self, event_name: str, /, *args: Any, **kwargs: Any) -> None:
        self._client.dispatch(event_name, *args, **kwargs)

    @property
    def user(self) -> discord.ClientUser | None:
        return self._client.user

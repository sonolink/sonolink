"""MIT License

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

from typing import Any, ClassVar, Protocol

import disnake

from .._base import DiscordClient

__all__ = (
    "DisnakeClient",
    "DisnakeClientProto",
)


class DisnakeClientProto(Protocol):
    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None: ...

    @property
    def user(self) -> disnake.ClientUser | None: ...


class DisnakeClient(DiscordClient[disnake.Client]):
    __slots__ = ()
    cls: ClassVar[type[disnake.Client]] = disnake.Client

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        self._client.dispatch(event_name, *args, **kwargs)

    @property
    def user(self) -> disnake.ClientUser | None:
        return self._client.user

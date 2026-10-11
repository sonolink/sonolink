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

from typing import TYPE_CHECKING, Any
from weakref import WeakKeyDictionary

if TYPE_CHECKING:
    from .gateway.client import Client


__all__ = ("get_client",)

clients: WeakKeyDictionary[Any, Client[Any]] = WeakKeyDictionary()


def get_client(bot: Any) -> Client[Any] | None:
    """Get the SonoLink client associated with a Discord client instance.

    .. versionadded:: 1.1.0

    Parameters
    ----------
    bot: Any
        The Discord client instance to retrieve the client for.

    Returns
    -------
    Client[Any] | None
        The SonoLink client associated with the Discord client, if any. Otherwise, ``None``.

    """
    return clients.get(bot)

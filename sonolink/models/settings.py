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

from typing import Iterable

from sonolink.gateway.enums import AutoPlayMode, InactivityMode, SearchProvider

from ..utils.snowflake import Snowflake
from .base import BaseSettings

__all__ = (
    "AutoPlaySettings",
    "CacheSettings",
    "HistorySettings",
    "InactivitySettings",
)


class AutoPlaySettings(BaseSettings):
    """Configuration for the player's AutoPlay behavior.

    Attributes
    ----------
    mode: :class:`AutoPlayMode`
        The default discovery mode when the player starts. Defaults to DISABLED.
    max_seeds: :class:`int`
        The maximum number of track identifiers to store to prevent duplicates.
        Defaults to 100.
    provider: :class:`SearchProvider` | :class:`str`
        The provider used for discovery. Defaults to SearchProvider.YOUTUBE.
    discovery_count: :class:`int`
        The maximum number of discovered tracks to add to the queue at once.
        Defaults to 10.
    """

    __slots__ = (
        "discovery_count",
        "max_seeds",
        "mode",
        "provider",
    )

    def __init__(
        self,
        *,
        mode: AutoPlayMode = AutoPlayMode.DISABLED,
        max_seeds: int = 100,
        provider: SearchProvider = SearchProvider.YOUTUBE,
        discovery_count: int = 10,
    ) -> None:
        self.mode: AutoPlayMode = mode
        self.max_seeds: int = max_seeds
        self.provider: SearchProvider = provider
        self.discovery_count = discovery_count


class InactivitySettings(BaseSettings):
    """Configuration for player inactivity and auto-disconnection.

    Attributes
    ----------
    timeout: :class:`int` | :data:`None`
        The time in seconds to wait before disconnecting. Defaults to 300.
    mode: :class:`InactivityMode`
        The strategy used to determine if the channel is "inactive".
    user_ids: ``Iterable[Snowflake | int]``
        An iterable of user IDs or Discord objects that act as "Keep Alive" members.
    """

    __slots__ = (
        "mode",
        "timeout",
        "user_ids",
    )

    def __init__(
        self,
        *,
        timeout: int | None = 300,
        mode: InactivityMode = InactivityMode.ALL_BOTS,
        user_ids: Iterable[Snowflake | int] | None = None,
    ) -> None:
        self.timeout: int | None = timeout
        self.mode: InactivityMode = mode
        self.user_ids: Iterable[Snowflake | int] = user_ids or []


class HistorySettings(BaseSettings):
    """Configuration for player history tracking.

    Attributes
    ----------
    enabled: :class:`bool`
        Whether history tracking is enabled. Defaults to True.
    max_items: :class:`int` | :data:`None`
        The maximum number of items to keep in history.
    """

    __slots__ = (
        "enabled",
        "max_items",
    )

    def __init__(
        self,
        *,
        enabled: bool = True,
        max_items: int | None = None,
    ) -> None:
        self.enabled: bool = enabled
        self.max_items: int | None = max_items


class CacheSettings(BaseSettings):
    """Configuration for node caching.

    Attributes
    ----------
    enabled: :class:`bool`
        Whether caching is enabled. Defaults to True.
    max_items: :class:`int` | :data:`None`
        The maximum number of items to store in the LFU cache.
        Defaults to 1000.
    """

    __slots__ = (
        "enabled",
        "max_items",
    )

    def __init__(
        self,
        *,
        enabled: bool = True,
        max_items: int = 1000,
    ) -> None:
        self.enabled: bool = enabled
        self.max_items: int = max_items

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

import copy
from collections import deque
from typing import TYPE_CHECKING, Self

from sonolink.models.settings import HistorySettings

from .base import ReadableCollection

if TYPE_CHECKING:
    from sonolink.models.track import Playable


class History(ReadableCollection):
    """A specialized queue for tracking playback history.

    This class is intended to be read-only for users. Mutation methods
    will raise :exc:`AttributeError`.
    """

    __slots__ = ("_settings",)

    def __init__(self, settings: HistorySettings | None = None) -> None:
        super().__init__()
        self._settings = settings or HistorySettings.default()
        self._items: deque[Playable] = deque(maxlen=self._settings.max_items)

    @property
    def enabled(self) -> bool:
        """Whether history recording is enabled.

        .. versionadded:: 1.3.0

        Returns
        -------
        :class:`bool`
            ``True`` if history is enabled, ``False`` otherwise.
        """
        return self._settings.enabled

    def clear(self) -> None:
        """Remove all tracks from the history.

        .. versionadded:: 1.4.0
        """
        self._items.clear()

    def _push(self, track: Playable) -> None:
        if not self._settings.enabled:
            return
        self._items.append(track)

    def _copy(self) -> Self:
        new = self.__class__(settings=copy.copy(self._settings))
        new._items = deque(self._items, maxlen=self._settings.max_items)
        return new

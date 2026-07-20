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

    def _push(self, track: Playable) -> None:
        if not self._settings.enabled:
            return
        self._items.append(track)

    def _copy(self) -> Self:
        new = self.__class__(settings=self._settings)
        new._items = deque(self._items, maxlen=self._settings.max_items)
        return new

    def _clear(self) -> None:
        self._items.clear()

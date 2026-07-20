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

from collections import Counter, deque
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, overload

from typing_extensions import Any, Callable

from sonolink.models.track import Playable

if TYPE_CHECKING:
    from sonolink.models.playlist import Playlist


class ReadableCollection:
    """A base class for read-only collection operations."""

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: deque[Playable] = deque()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} size={len(self._items)}>"

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return len(self._items) > 0

    def __iter__(self) -> Iterator[Playable]:
        return iter(self._items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    @overload
    def __getitem__(self, index: int) -> Playable: ...

    @overload
    def __getitem__(self, index: slice) -> list[Playable]: ...

    def __getitem__(self, index: int | slice) -> Playable | list[Playable]:
        if isinstance(index, int):
            return self._items[index]
        return list(self._items)[index]

    @property
    def count(self) -> int:
        """The number of tracks in this collection.

        Returns
        -------
        :class:`int`
            The total number of tracks currently held.
        """
        return len(self._items)

    def _as_playable(self, value: object) -> Playable:
        if not isinstance(value, Playable):
            raise TypeError(f"Expected Playable, got {type(value).__name__}")
        return value


class MutableQueueBase(ReadableCollection):
    """A base class for collections that can be modified."""

    __slots__ = ()

    def _materialize_tracks(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        *,
        atomic: bool,
    ) -> list[Playable]:
        items = [tracks] if isinstance(tracks, Playable) else list(tracks)

        if not atomic:
            return [t for t in items if isinstance(t, Playable)]

        return [self._as_playable(item) for item in items]

    def put(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        atomic: bool = True,
    ) -> int:
        """Put one or more tracks at the end of the queue.

        Parameters
        ----------
        tracks: :class:`sonolink.models.Playable` | :class:`sonolink.models.Playlist` | Iterable[:class:`sonolink.models.Playable`]
            The track(s) or playlist to add to the queue.
        atomic: :class:`bool`
            Whether to insert the items atomically. If ``True``, all items must be
            Playable or a TypeError is raised and nothing is added. If ``False``,
            non-Playable items are filtered out. Defaults to ``True``.

        Returns
        -------
        :class:`int`
            The number of tracks added to the queue.

        Raises
        ------
        :exc:`TypeError`
            When ``atomic=True`` and a non-Playable item is encountered.
        """
        tracks = self._materialize_tracks(tracks, atomic=atomic)
        count = len(tracks)
        if count != 0:
            self._items.extend(tracks)
        return count

    def put_at(
        self,
        index: int,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        atomic: bool = True,
    ) -> int:
        """Put one or more tracks at ``index``.

        Parameters
        ----------
        index: :class:`int`
            The index to insert the track(s) to.
        tracks: :class:`sonolink.models.Playable` | :class:`sonolink.models.Playlist` | Iterable[:class:`sonolink.models.Playable`]
            The track(s) or playlist to add to the queue.
        atomic: :class:`bool`
            Whether to insert the items atomically. If ``True``, all items must be
            Playable or a TypeError is raised and nothing is added. If ``False``,
            non-Playable items are filtered out. Defaults to ``True``.

        Returns
        -------
        :class:`int`
            The number of tracks added to the queue.

        Raises
        ------
        :exc:`TypeError`
            When ``atomic=True`` and a non-Playable item is encountered.
        """
        tracks = self._materialize_tracks(tracks, atomic=atomic)
        count = len(tracks)

        if count == 0:
            return 0

        items_length = len(self._items)

        if index < 0:
            index += items_length

        index = max(0, min(index, items_length))

        if count == 1:
            self._items.insert(index, tracks[0])
            return 1

        tail = items_length - index

        if index <= tail:  # insertion point is closer to (or equidistant from) the left
            self._items.rotate(-index)
            self._items.extendleft(reversed(tracks))
            self._items.rotate(index)
        else:
            self._items.rotate(tail)
            self._items.extend(tracks)
            self._items.rotate(-tail)

        return count

    def remove(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        remove_all: bool = True,
        key: Callable[[Playable], Any] | None = None,
    ) -> int:
        """Remove one or more tracks from this queue.

        Parameters
        ----------
        tracks: :class:`sonolink.models.Playable` | :class:`sonolink.models.Playlist` | Iterable[:class:`sonolink.models.Playable`]
            The track(s) or playlist to remove from the queue.
        remove_all: :class:`bool`
            Whether to remove all occurrences of a track from this queue. When set to ``False``, only the first occurrence of each
            track is removed. Defaults to ``True``.
        key: Callable[[:class:`Playable`], Any] | None
            If provided, tracks are matched by comparing ``key(track)`` against
            each value in ``tracks`` instead of using equality directly. This lets
            you remove tracks without holding the original :class:`Playable`
            instance, e.g. ``queue.remove([track.identifier], key=lambda t: t.identifier)``.
            When ``key`` is set, items in ``tracks`` are used as-is and are not
            coerced to :class:`Playable`. Defaults to ``None``.

            .. versionadded:: 1.3.0

        Returns
        -------
        :class:`int`
            The number of tracks removed from the queue.
        """
        if key is None:
            to_remove = self._materialize_tracks(tracks, atomic=False)
        else:
            to_remove = (
                list(tracks)
                if isinstance(tracks, Iterable) and not isinstance(tracks, Playable)
                else [tracks]
            )

        if not to_remove:
            return 0

        before = len(self._items)

        if remove_all:
            lookup = set(to_remove)
            self._items = deque(
                track
                for track in self._items
                if (key(track) if key else track) not in lookup
            )
        else:
            counts = Counter(to_remove)
            new_items: deque[Playable] = deque()

            for track in self._items:
                value = key(track) if key else track
                if counts.get(value, 0) > 0:
                    counts[value] -= 1
                else:
                    new_items.append(track)

            self._items = new_items

        return before - len(self._items)

    def clear(self) -> None:
        """Remove all items from the queue."""
        self._items.clear()

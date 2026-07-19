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

import asyncio
import random
from collections import deque
from typing import TYPE_CHECKING, Any, Callable, Iterable

from sonolink.models.settings import HistorySettings
from sonolink.models.track import Playable

from ..enums import QueueMode
from ..errors import HistoryEmpty, QueueEmpty
from .base import MutableQueueBase
from .history import History

if TYPE_CHECKING:
    from sonolink.models.playlist import Playlist


class Queue(MutableQueueBase):
    """A queue implementation for managing playable tracks."""

    __slots__ = (
        "_autoplay_items",
        "_current_track",
        "_history",
        "_lock",
        "_mode",
        "_waiters",
    )

    def __init__(
        self,
        *,
        mode: QueueMode = QueueMode.NORMAL,
        history_settings: HistorySettings | None = None,
    ) -> None:
        super().__init__()

        self._mode: QueueMode = mode
        self._lock: asyncio.Lock = asyncio.Lock()
        self._waiters: deque[asyncio.Future[None]] = deque()

        self._history: History = History(settings=history_settings)
        self._current_track: Playable | None = None
        self._autoplay_items: deque[Playable] = deque()

    @property
    def current_track(self) -> Playable | None:
        """The currently loaded track.

        This track is typically the one being played or most recently played.

        This is also used when :attr:`mode` is set to :attr:`QueueMode.LOOP` to
        determine which track to repeat. This can be manually set too.

        Returns
        -------
        :class:`sonolink.models.Playable` | None
            The current track, or ``None`` if not set.
        """
        return self._current_track

    @current_track.setter
    def current_track(self, value: Playable | None) -> None:
        if value is not None:
            self._as_playable(value)
        self._current_track = value

    @property
    def history(self) -> History:
        """The queue history.

        Returns
        -------
        :class:`History` | None
            The queue history if history is enabled, otherwise ``None``.
        """
        return self._history

    @property
    def mode(self) -> QueueMode:
        """The current queue mode.

        - :attr:`QueueMode.NORMAL`: Tracks are played in order and removed from the queue.
        - :attr:`QueueMode.LOOP`: :attr:`current_track` is repeated indefinitely until manually changed.
        - :attr:`QueueMode.LOOP_ALL`: When the queue is empty, all tracks from history are restored
            to the queue and played again.

        Returns
        -------
        :class:`QueueMode`
            The current queue mode.
        """
        return self._mode

    @mode.setter
    def mode(self, value: QueueMode) -> None:
        self._mode = value

    @property
    def tracks(self) -> list[Playable]:
        """The list of tracks currently in the queue.

        This does not include the :attr:`current_track` or AutoPlay-discovered
        tracks. Modifying this list will not affect the actual queue; use methods
        like :meth:`put` or :meth:`pop_at` for modifications.

        Returns
        -------
        list[:class:`Playable`]
            A list of tracks in the queue.
        """
        return list(self._items)

    @property
    def autoplay_tracks(self) -> list[Playable]:
        """The list of AutoPlay-discovered tracks currently staged in the queue.

        These tracks are only played once all user-added tracks are exhausted.
        Modifying this list will not affect the actual queue.

        .. versionadded:: 1.1.0

        Returns
        -------
        list[:class:`Playable`]
            A list of AutoPlay tracks.
        """
        return list(self._autoplay_items)

    def get(self) -> Playable:
        """Get the next track from the queue, respecting the current queue mode.

        User-added tracks always take priority over AutoPlay-discovered tracks.
        If the user lane is empty, falls back to the AutoPlay lane.
        If the queue is in ``LOOP`` mode, returns the current track.
        If the queue is in ``LOOP_ALL`` mode and empty, restores tracks from history.

        Returns
        -------
        :class:`sonolink.models.Playable`
            The retrieved track.

        Raises
        ------
        :class:`QueueEmpty`
            Both the user queue and AutoPlay queue are empty.
        """
        if self._mode is QueueMode.LOOP and self._current_track is not None:
            return self._current_track

        if self._mode is QueueMode.LOOP_ALL and not self._items:
            if len(self._history) > 0:
                self._items.extend(self._history)
                self._history._clear()

            if self._current_track is not None:
                self._items.append(self._current_track)
                self._current_track = None

        if self._items:
            return self.pop()

        if self._autoplay_items:
            if self._current_track is not None:
                self._history._push(self._current_track)

            track = self._autoplay_items.popleft()
            self._current_track = track
            return track

        raise QueueEmpty("Queue is empty.")

    async def get_wait(self) -> Playable:
        """Asynchronously get a track from the queue, waits if necessary.

        This method will wait indefinitely until a track is available in the queue.
        This method can be used to implement a system that waits for a next track to
        play after the current track finishes, for example.

        Returns
        -------
        :class:`Playable`
            The retrieved track.
        """
        while True:
            try:
                return self.get()
            except QueueEmpty:
                pass

            waiter: asyncio.Future[None] = asyncio.get_running_loop().create_future()
            self._waiters.append(waiter)

            try:
                await waiter
            finally:
                waiter.cancel()
                if waiter in self._waiters:
                    self._waiters.remove(waiter)

                if self and not waiter.cancelled():
                    self._wakeup_next()

    def pop(self) -> Playable:
        """Remove and return the next track from the queue.

        The returned track is set as the current track.
        If history is enabled, the previous current track is added to history.

        Returns
        -------
        :class:`sonolink.models.Playable`
            The popped track.

        Raises
        ------
        :class:`QueueEmpty`
            The queue is empty.
        """
        if not self:
            raise QueueEmpty("Queue is empty.")

        if self._current_track is not None:
            self._history._push(self._current_track)

        track = self._items.popleft()
        self._current_track = track
        return track

    def pop_at(self, index: int) -> Playable:
        """Remove and return a track from a specific queue index.

        The returned track is set as the current track.
        If history is enabled, the previous current track is added to history.

        Parameters
        ----------
        index: :class:`int`
            The index to pop from.

        Returns
        -------
        :class:`sonolink.models.Playable`
            The popped track.

        Raises
        ------
        :class:`QueueEmpty`
            The queue is empty.
        :exc:`IndexError`
            There is no item at the given index.
        """
        if not self:
            raise QueueEmpty("Queue is empty.")

        track = self._items[index]
        del self._items[index]

        if self._current_track is not None:
            self._history._push(self._current_track)

        self._current_track = track
        return track

    def previous(self) -> Playable:
        """Pop the most recent track from history and set it as current.

        The current track is pushed back to the front of the queue.

        Returns
        -------
        :class:`sonolink.models.Playable`
            The track retrieved from history.

        Raises
        ------
        :class:`QueueEmpty`
            The history is empty.
        """
        if len(self._history) == 0:
            raise HistoryEmpty("History is empty.")

        if self._current_track is not None:
            self._items.appendleft(self._current_track)

        track = self._history._items.pop()
        self._current_track = track
        return track

    def put(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        atomic: bool = True,
    ) -> int:
        count = super().put(tracks, atomic=atomic)
        self._wakeup_next()
        return count

    async def put_wait(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        atomic: bool = True,
    ) -> int:
        """Asynchronously put one or more tracks into the queue.

        This method is thread-safe and maintains insert order through a lock.

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
        async with self._lock:
            count = self.put(tracks, atomic=atomic)

        if count != 0:
            await asyncio.sleep(0)
        return count

    def put_autoplay(
        self,
        tracks: Iterable[Playable] | Playable,
        /,
    ) -> int:
        """Add AutoPlay-discovered tracks to the AutoPlay lane.

        These tracks are only played once all user-added tracks are exhausted.
        Each track is automatically tagged with :attr:`~sonolink.models.Playable.autoplay`.

        Parameters
        ----------
        tracks: :class:`sonolink.models.Playable` | Iterable[:class:`sonolink.models.Playable`]
            The AutoPlay track(s) to stage.

        Returns
        -------
        :class:`int`
            The number of tracks added.

        .. versionadded:: 1.1.0
        """
        if isinstance(tracks, Playable):
            tracks = (tracks,)

        tracks = list(tracks)
        for track in tracks:
            track._autoplay = True

        self._autoplay_items.extend(tracks)
        count = len(tracks)

        if count:
            self._wakeup_next()

        return count

    async def remove_wait(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        remove_all: bool = True,
    ) -> int:
        """Asynchronously remove one or more tracks from the queue.

        This method is thread-safe.

        Parameters
        ----------
        tracks: :class:`sonolink.models.Playable` | :class:`sonolink.models.Playlist` | Iterable[:class:`sonolink.models.Playable`]
            The track(s) or playlist to remove from the queue.
        remove_all: :class:`bool`
            Whether to remove all occurrences of a track from this queue. When set to ``False``, only the first occurrence of each
            track is removed. Defaults to ``True``.

        Returns
        -------
        :class:`int`
            The number of tracks removed from the queue.
        """
        async with self._lock:
            count = self.remove(tracks, remove_all=remove_all)

        if count != 0:
            await asyncio.sleep(0)
        return count

    def copy(self) -> Queue:
        """Create a shallow copy of the queue.

        Returns
        -------
        :class:`Queue`
            A shallow copy of the queue with the same items, mode, and history.
        """
        new_queue = self.__class__(
            mode=self._mode,
            history_settings=self._history._settings,
        )
        new_queue._items = deque(self._items)
        new_queue._current_track = self._current_track
        new_queue._history = self._history._copy()
        new_queue._autoplay_items = deque(self._autoplay_items)
        return new_queue

    def reverse(self) -> None:
        """Reverse the queue in place.

        This does not return anything.
        """
        self._items = deque[Playable](reversed(self._items))

    def sort(
        self,
        *,
        key: Callable[[Playable], Any],
        reverse: bool = False,
    ) -> None:
        """Sort the queue in place.

        Parameters
        ----------
        key: Callable[[:class:`~sonolink.models.Playable`], Any]
            A function that takes a track and returns a value to sort by,
            e.g. ``key=lambda track: track.title``.
        reverse: :class:`bool`
            Whether to sort in descending order. Defaults to ``False``.
        """
        self._items = deque[Playable](sorted(self._items, key=key, reverse=reverse))

    def dedupe(self, *, key: Callable[[Playable], Any] = lambda t: t.identifier) -> int:
        """Remove duplicate tracks in place, keeping the first occurrence of each.

        Parameters
        ----------
        key: Callable[[:class:`~sonolink.models.Playable`], Any]
            A function that returns the value used to determine duplicates.
            Defaults to comparing by :attr:`~sonolink.models.Playable.identifier`.

        Returns
        -------
        :class:`int`
            The number of tracks removed.
        """
        seen: set[Any] = set()
        before = len(self._items)
        self._items = deque[Playable](
            track
            for track in self._items
            if (k := key(track)) not in seen and not seen.add(k)
        )
        return before - len(self._items)

    def shuffle(self) -> None:
        """Shuffle the queue in place.

        This does not return anything.
        """
        self._items = deque(random.sample(self._items, k=len(self._items)))

    def swap(self, old: int, new: int) -> None:
        """Swap two tracks in the queue by index.

        Parameters
        ----------
        old: :class:`int`
            The index of the first track.
        new: :class:`int`
            The index of the second track.

        Raises
        ------
        :exc:`IndexError`
            One or both indices are out of range.
        """
        self._items[old], self._items[new] = self._items[new], self._items[old]

    def clear_history(self) -> None:
        """Clear the queue history if history is enabled."""
        self._history._clear()

    def reset(self) -> None:
        """Reset the queue to its default state.

        This will:

        - Clear all items from the queue
        - Clear AutoPlay-discovered tracks
        - Clear history
        - Reset the mode to :class:`QueueMode.NORMAL`
        - Clear the current track
        - Cancel all waiting futures
        """
        self.clear()
        self.clear_history()

        self._current_track = None
        self._mode = QueueMode.NORMAL
        self._autoplay_items.clear()

        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.cancel()

        self._waiters.clear()

    def _wakeup_next(self) -> None:
        while self._waiters:
            waiter = self._waiters.popleft()

            if waiter.done():
                continue

            waiter.set_result(None)
            break

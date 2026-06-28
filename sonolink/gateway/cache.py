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

import collections
from typing import Any, Final

import msgspec

from sonolink.models.settings import CacheSettings

UNSET: Final = msgspec.UNSET


class CacheNode[K, V]:
    __slots__ = ("freq", "key", "next", "prev", "value")

    def __init__(self, key: K, value: V, freq: int = 1) -> None:
        self.key: K = key
        self.value: V = value
        self.freq: int = freq

        self.prev: CacheNode[K, V] = self
        self.next: CacheNode[K, V] = self


class LFUCache[K, V]:
    """LFU cache utilizing Circular Doubly Linked Lists."""

    __slots__ = ("_cache", "_freq_map", "_min_freq", "_settings")

    def __init__(self, settings: CacheSettings | None = None) -> None:
        self._settings = settings or CacheSettings.default()

        self._cache: dict[K, CacheNode[K, V]] = {}
        self._freq_map: dict[int, CacheNode[Any, Any]] = collections.defaultdict(
            lambda: CacheNode(None, None, 0)
        )
        self._min_freq: int = 0

    def __repr__(self) -> str:
        return f"<LFUCache entries={len(self._cache)} max_items={self._settings.max_items}>"

    def __len__(self) -> int:
        return len(self._cache)

    def _unlink(self, node: CacheNode[K, V]) -> None:
        """Remove a node from its current circular list."""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _link(self, sentinel: CacheNode[Any, Any], node: CacheNode[K, V]) -> None:
        """Add a node to the end of a circular list (just before the sentinel)."""
        node.next = sentinel
        node.prev = sentinel.prev
        sentinel.prev.next = node
        sentinel.prev = node

    def get(self, key: K, default: Any = UNSET) -> V | Any:
        if not self._settings.enabled or (node := self._cache.get(key)) is None:
            return default

        self._unlink(node)

        # If the min_freq list is empty (sentinel points to itself)
        if (
            node.freq == self._min_freq
            and self._freq_map[node.freq].next is self._freq_map[node.freq]
        ):
            self._min_freq += 1

        node.freq += 1
        self._link(self._freq_map[node.freq], node)
        return node.value

    def put(self, key: K, value: V) -> None:
        if not self._settings.enabled or self._settings.max_items <= 0:
            return

        if key in self._cache:
            node = self._cache[key]
            node.value = value
            self.get(key)
            return

        if len(self._cache) >= self._settings.max_items:
            # Evict the oldest node from the lowest freq. list
            sentinel = self._freq_map[self._min_freq]
            evicted = sentinel.next
            self._unlink(evicted)
            del self._cache[evicted.key]

        new_node = CacheNode(key, value)
        self._cache[key] = new_node
        self._link(self._freq_map[1], new_node)
        self._min_freq = 1

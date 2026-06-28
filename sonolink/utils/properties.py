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

from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar, overload

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

__all__ = ("cached_property",)


class _cached_property(Generic[T, T_co]):
    _name: str
    _function: Callable[[T], T_co]
    _setter: Callable[[T, T_co], None] | None
    _deleter: Callable[[T], None] | None

    def __init__(self, name: str, function: Callable[[T], T_co]) -> None:
        self._name = name
        self._function = function
        self._setter = None
        self._deleter = None
        self.__doc__ = getattr(function, "__doc__")

    @overload
    def __get__(self, instance: None, owner: type[T]) -> _cached_property[T, T_co]: ...

    @overload
    def __get__(self, instance: T, owner: type[T]) -> T_co: ...

    def __get__(self, instance: T | None, owner: type[T]) -> Any:
        if instance is None:
            return self

        try:
            return getattr(instance, self._name)
        except AttributeError:
            value = self._function(instance)
            setattr(instance, self._name, value)
            return value

    def _reset_cache(self, instance: T) -> None:
        if hasattr(instance, self._name):
            delattr(instance, self._name)

    def __set__(self, instance: T, value: Any) -> None:
        if not self._setter:
            return
        self._setter(instance, value)
        self._reset_cache(instance)

    def __delete__(self, instance: T) -> None:
        if not self._deleter:
            return
        self._deleter(instance)
        self._reset_cache(instance)

    def setter(self, func: Callable[[T, T_co], None]) -> Self:
        self._setter = func
        return self

    def deleter(self, func: Callable[[T], None]) -> Self:
        self._deleter = func
        return self


def cached_property(
    attribute: str,
) -> Callable[[Callable[[T], T_co]], _cached_property[T, T_co]]:
    """Creates a cached property that stores the result under ``class.attribute``."""

    def inner(func: Callable[[T], T_co]) -> _cached_property[T, T_co]:
        return _cached_property(attribute, func)

    return inner

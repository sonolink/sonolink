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
    """Create a cached property that stores the result under ``class.attribute``."""

    def inner(func: Callable[[T], T_co]) -> _cached_property[T, T_co]:
        return _cached_property(attribute, func)

    return inner

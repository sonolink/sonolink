"""MIT License

Copyright (c) 2026-present SonoLink Development Team

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

import copy
from typing import TYPE_CHECKING, Any, ClassVar, Self

import msgspec

if TYPE_CHECKING:
    from ..gateway.client import Client


class BaseModel[D: msgspec.Struct]:
    """A base class for all sonolink models.

    This class provides the connection to the :class:`sonolink.Client`
    and holds the raw msgspec data structure.
    """

    __slots__ = (
        "_client",
        "_data",
    )

    def __init__(self, *, client: Client[Any] | None, data: D) -> None:
        self._client: Client[Any] | None = client
        self._data: D = data

    def __repr__(self) -> str:
        fields = getattr(self._data, "__struct_fields__", ())

        parts = [
            f"{field}={value!r}"
            for field in fields
            if (value := getattr(self._data, field)) is not None
            and not isinstance(value, (list, dict))
        ]

        attrs = f" {', '.join(parts)}" if parts else ""
        return f"<sonolink.{self.__class__.__name__} {attrs}>"

    @property
    def client(self) -> Client[Any] | None:
        """The :class:`sonolink.Client` instance associated with this object."""
        return self._client

    @property
    def data(self) -> D:
        """The raw msgspec schema object holding the data for this model."""
        return self._data


class BaseSettings:
    """A base class for configuration proxies in sonolink.

    This class provides utility methods for immutable-style updates
    and fluent attribute setting (chaining).
    """

    __slots__ = ()

    @classmethod
    def default(cls) -> Self:
        """Returns a fresh instance of this settings class with defaults."""
        return cls()

    def replace(self, **kwargs: Any) -> Self:
        """Returns a new instance of the settings with updated values.

        This uses a shallow copy to ensure the original configuration
        instance remains immutable.
        """
        new = copy.copy(self)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(new, key, value)
        return new


class BaseFilter[D: msgspec.Struct](BaseModel[D]):
    """A base class for all single Lavalink filter models.

    Subclasses must declare ``_schema_cls`` as a class variable pointing
    to the corresponding msgspec schema type.
    """

    __slots__ = ()

    _schema_cls: ClassVar[type]

    def __init__(self, *, client: Client[Any] | None = None, **kwargs: Any) -> None:
        data = self._schema_cls(**{k: self._set(v) for k, v in kwargs.items()})
        super().__init__(client=client, data=data)

    @classmethod
    def _from_data(cls, client: Client[Any], data: D) -> Self:
        fields: tuple[str, ...] = getattr(data, "__struct_fields__", ())
        instance = cls(**{field: cls._get(getattr(data, field)) for field in fields})
        instance._client = client
        return instance

    @staticmethod
    def _get[T](value: T | msgspec.UnsetType) -> T | None:
        return value if value is not msgspec.UNSET else None

    @staticmethod
    def _set[T](value: T | None) -> T | msgspec.UnsetType:
        return value if value is not None else msgspec.UNSET

    def __or__(self, other: object) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.combine(other)

    def __ior__(self, other: object) -> Self:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.merge(other)

    def merge(self, other: BaseFilter[D]) -> Self:
        """Merges another filter into this one, preferring the other's values.

        This method mutates the current instance and returns it for chaining.

        See also :meth:`combine` for a non-mutating version that returns a new instance.

        Parameters
        ----------
        other: :class:`BaseFilter`
            The other filter to merge into this one. Must be of the same type.

        Returns
        -------
        :class:`BaseFilter`
            The current instance with merged values.

        """
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot merge an object of type {type(other).__name__} into {self.__class__.__name__}"
            )

        for field in msgspec.structs.fields(self.data):
            attr_name: str = field.name
            self_value = getattr(self, attr_name)
            other_value = getattr(other, attr_name)
            if other_value is not None and other_value != self_value:
                setattr(self, attr_name, other_value)

        return self

    def combine(self, other: BaseFilter[D]) -> Self:
        """Combines this filter with another, preferring the other's values.

        This method does not mutate the current instance and returns a new one.
        See also :meth:`merge` for an in-place version that mutates the current instance.

        Parameters
        ----------
        other: :class:`BaseFilter`
            The other filter to combine with this one. Must be of the same type.

        Returns
        -------
        :class:`BaseFilter`
            A new instance with merged values from both filters.

        """
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"Cannot merge an object of type {type(other).__name__} into {self.__class__.__name__}"
            )

        kws = {
            field.name: getattr(self, field.name)
            for field in msgspec.structs.fields(self.data)
        }
        return self.__class__(**kws).merge(other)

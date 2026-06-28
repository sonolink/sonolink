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

import msgspec

from ..enums import IPBlockType, RoutePlannerType

__all__ = (
    "DetailsObject",
    "FailingAddressObject",
    "IPBlockObject",
    "RoutePlannerStatusResponse",
    "UnmarkAllFailedAddressesResponse",
    "UnmarkFailedAddressRequest",
    "UnmarkFailedAddressResponse",
)


class DetailsObject(msgspec.Struct, kw_only=True):
    """Represents route planner details.

    Provides runtime information about the active IP rotation strategy.
    Some attributes are only present for specific route planner types.
    """

    ip_block: IPBlockObject = msgspec.field(name="ipBlock")
    """IP block configuration currently used (:class:`IPBlockObject`)."""

    failing_addresses: list[FailingAddressObject] = msgspec.field(
        name="failingAddresses",
        default_factory=lambda: list[FailingAddressObject](),
    )
    """List of addresses currently marked as failing (``FailingAddressObject``)."""

    rotate_index: str | None = msgspec.field(name="rotateIndex", default=None)
    """Number of performed rotations. Available for ``RotatingIpRoutePlanner``."""

    ip_index: int | None = msgspec.field(name="ipIndex", default=None)
    """Current offset within the IP block. Available for ``RotatingIpRoutePlanner``."""

    block_index: int | None = msgspec.field(name="blockIndex", default=None)
    """
    Index of the active ``/64`` block. This value increases whenever an address
    block is rotated due to bans. Available for ``RotatingNanoIpRoutePlanner``.
    """

    current_address: str | None = msgspec.field(name="currentAddress", default=None)
    """Currently selected outbound IP address. Available for ``RotatingIpRoutePlanner``."""

    current_address_index: int | None = msgspec.field(
        name="currentAddressIndex",
        default=None,
    )
    """
    Offset of the active address inside the IP block.
    Available for ``NanoIpRoutePlanner`` and ``RotatingNanoIpRoutePlanner``.
    """


class IPBlockObject(msgspec.Struct, kw_only=True):
    """Represents an IP block used by the route planner."""

    type_: IPBlockType = msgspec.field(name="type")
    """Type of IP block (:class:`IPBlockType`)."""

    size: str
    """The size of the IP block."""


class FailingAddressObject(msgspec.Struct, kw_only=True):
    """Represents an address marked as failing by the route planner.

    Addresses are temporarily excluded after connection failures.
    """

    address: str = msgspec.field(name="failingAddress")
    """The failing IP address."""

    timestamp: int = msgspec.field(name="failingTimestamp")
    """Failure timestamp in Unix milliseconds."""

    time: str = msgspec.field(name="failingTime")
    """Human-readable failure time string."""


class RoutePlannerStatusResponse(msgspec.Struct, kw_only=True):
    """Represents the response from GET `/v4/routeplanner/status`."""

    class_: RoutePlannerType | None = msgspec.field(name="class", default=None)
    """The type of route planner in use (:class:`RoutePlannerType`)."""

    details: DetailsObject | None = None
    """Status details (:class:`DetailsObject`), or ``None`` if not enabled."""


class UnmarkFailedAddressRequest(msgspec.Struct, kw_only=True):
    """Represents a request to unmark a previously failing address."""

    address: str
    """The address to unmark as failed. Must belong to the same IP block."""


UnmarkFailedAddressResponse = None
"""
Represents a successful response from unmarking a failed address.
No content is returned by the server (HTTP 204).
"""

UnmarkAllFailedAddressesResponse = None
"""
Represents a successful response from unmarking all failed addresses.
No content is returned by the server (HTTP 204).
"""

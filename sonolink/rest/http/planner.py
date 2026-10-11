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

from typing import TYPE_CHECKING

import msgspec

from ..schemas import planner

if TYPE_CHECKING:
    from .base import HTTPClient


class RoutePlannerHTTPMixin:
    """Mixin for Planner related HTTP operations."""

    async def status(
        self: HTTPClient,
    ) -> planner.RoutePlannerStatusResponse | None:
        url = "/routeplanner/status"
        res = await self.request("GET", url)

        if res is None:
            return None

        return msgspec.json.decode(res, type=planner.RoutePlannerStatusResponse)

    async def unmark_failed_address(
        self: HTTPClient, data: planner.UnmarkFailedAddressRequest
    ) -> None:
        url = "/routeplanner/free/address"
        await self.request(
            "POST",
            url,
            data=msgspec.json.encode(data),
            headers={"Content-Type": "application/json"},
        )

    async def unmark_all_failed_addresses(self: HTTPClient) -> None:
        url = "/routeplanner/free/all"
        await self.request("POST", url)

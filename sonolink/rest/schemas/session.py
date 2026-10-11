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

import msgspec

__all__ = (
    "UpdateSessionRequest",
    "UpdateSessionResponse",
)


class UpdateSessionRequest(msgspec.Struct, kw_only=True):
    """Represents a request to update a Lavalink session.

    Sent via PATCH `/v4/sessions/{sessionId}` to modify the resuming state
    or the session timeout.
    """

    resuming: bool | None = None
    """Optional. Whether resuming is enabled for this session."""

    timeout: int | None = None
    """Optional. Timeout in seconds for resuming. Defaults to 60s."""


UpdateSessionResponse = UpdateSessionRequest
"""Represents the response from updating a session, mirroring the request payload."""

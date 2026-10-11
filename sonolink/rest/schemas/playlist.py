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

__all__ = ("PlaylistInfo",)


class PlaylistInfo(msgspec.Struct, kw_only=True):
    """Represents metadata for a loaded playlist.

    This object is embedded in playlist load responses.
    """

    name: str
    """Name of the playlist."""

    selected_track: int = msgspec.field(name="selectedTrack")
    """Index of the selected track within the playlist, or ``-1`` if no track is selected."""

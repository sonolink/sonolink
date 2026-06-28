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

__all__ = (
    "CPUObject",
    "FrameStatsObject",
    "GitObject",
    "InfoResponse",
    "MemoryObject",
    "PluginObject",
    "StatsResponse",
    "VersionObject",
    "VersionResponse",
)


class InfoResponse(msgspec.Struct, kw_only=True):
    """Represents the Lavalink Info response payload."""

    version: VersionObject
    """Version metadata of the Lavalink server."""

    build_time: int = msgspec.field(name="buildTime")
    """Build timestamp in Unix milliseconds."""

    git: GitObject
    """Git repository information for this build."""

    jvm: str
    """JVM version used to run Lavalink."""

    lavaplayer: str
    """Embedded Lavaplayer version."""

    source_managers: list[str] = msgspec.field(name="sourceManagers")
    """Enabled source managers."""

    filters: list[str]
    """Names of supported audio filters."""

    plugins: list[PluginObject]
    """Installed Lavalink plugins."""


class VersionObject(msgspec.Struct, kw_only=True, frozen=True):
    """Represents Lavalink version metadata."""

    semver: str
    """Full semantic version string."""

    major: int
    """Major version number."""

    minor: int
    """Minor version number."""

    patch: int
    """Patch version number."""

    pre_release: str | None = msgspec.field(name="preRelease", default=None)
    """Pre-release identifier if present."""

    build: str | None = None
    """Optional build metadata string."""


class GitObject(msgspec.Struct, kw_only=True, frozen=True):
    """Represents Git metadata for the Lavalink build."""

    branch: str
    """Git branch name."""

    commit: str
    """Commit hash."""

    commit_time: int = msgspec.field(name="commitTime")
    """Commit timestamp in Unix milliseconds."""


class PluginObject(msgspec.Struct, kw_only=True, frozen=True):
    """Represents an installed Lavalink plugin."""

    name: str
    """Plugin name."""

    version: str
    """Plugin version string."""


class StatsResponse(msgspec.Struct, kw_only=True):
    """Represents the Lavalink Stats response payload.

    Returned periodically over WebSocket and via ``/v4/stats``.
    """

    players: int
    """Total number of players."""

    playing_players: int = msgspec.field(name="playingPlayers")
    """Number of actively playing players."""

    uptime: int
    """Node uptime in milliseconds."""

    memory: MemoryObject
    """JVM memory usage statistics."""

    cpu: CPUObject
    """CPU usage statistics."""

    frame_stats: FrameStatsObject | None = msgspec.field(
        name="frameStats", default=None
    )
    """Optional audio frame statistics."""

    @property
    def penalty(self) -> float:
        """Calculate node penalty; Lower - better."""
        player_penalty: int = self.playing_players
        cpu_penalty: float = 1.05 ** (100 * self.cpu.system_load) * 10 - 10

        null_frame_penalty: float = 0.0
        deficit_frame_penalty: float = 0.0

        if self.frame_stats:
            null_frame_penalty = (
                (1.03 ** (500 * (self.frame_stats.nulled / 3000))) * 300 - 300
            ) * 2
            deficit_frame_penalty = (
                1.03 ** (500 * (self.frame_stats.deficit / 3000))
            ) * 600 - 600

        return player_penalty + cpu_penalty + null_frame_penalty + deficit_frame_penalty


class MemoryObject(msgspec.Struct, kw_only=True):
    """Represents JVM memory usage statistics."""

    free: int
    """Free memory in bytes."""

    used: int
    """Used memory in bytes."""

    allocated: int
    """Allocated memory in bytes."""

    reservable: int
    """Maximum reservable memory in bytes."""


class CPUObject(msgspec.Struct, kw_only=True):
    """Represents CPU usage statistics."""

    cores: int
    """Number of available CPU cores."""

    system_load: float = msgspec.field(name="systemLoad")
    """System CPU load as a fraction."""

    lavalink_load: float = msgspec.field(name="lavalinkLoad")
    """CPU load caused by Lavalink."""


class FrameStatsObject(msgspec.Struct, kw_only=True):
    """Represents audio frame delivery statistics."""

    sent: int
    """Number of frames successfully sent."""

    nulled: int
    """Number of frames that were missing audio data."""

    deficit: int
    """
    Frame deficit relative to the expected rate (3000 frames/player).
    Negative means excess frames, positive means insufficient frames.
    """


VersionResponse = str
"""Represents a Lavalink version string in `x.y.z` format."""

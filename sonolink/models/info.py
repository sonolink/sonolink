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

import datetime
from typing import TYPE_CHECKING

from sonolink.utils import cached_property

from ..rest.schemas.info import (
    GitObject as GitPayload,
    InfoResponse as ServerInfoPayload,
    VersionObject as VersionPayload,
)
from .base import BaseModel

if TYPE_CHECKING:
    from ..rest.schemas.info import PluginObject


__all__ = ("GitInfo", "ServerInfo", "Version")


class Version(BaseModel[VersionPayload]):
    """Represents a Lavalink server's version metadata.

    Wraps the raw :class:`sonolink.rest.schemas.info.VersionObject` struct and
    provides comparison operators and convenience properties.
    """

    __slots__ = ()

    def __str__(self) -> str:
        return self._data.semver

    @property
    def semver(self) -> str:
        """The full semantic version string, e.g. ``4.2.2``."""
        return self._data.semver

    @property
    def major(self) -> int:
        """The major version number."""
        return self._data.major

    @property
    def minor(self) -> int:
        """The minor version number."""
        return self._data.minor

    @property
    def patch(self) -> int:
        """The patch version number."""
        return self._data.patch

    @property
    def pre_release(self) -> str | None:
        """The pre-release identifier, if any, e.g. ``alpha.1``."""
        return self._data.pre_release

    @property
    def build(self) -> str | None:
        """Optional build metadata string."""
        return self._data.build

    @property
    def is_stable(self) -> bool:
        """Whether this is a stable release (no pre-release identifier)."""
        return self._data.pre_release is None


class GitInfo(BaseModel[GitPayload]):
    """Represents the Git metadata of a Lavalink build.

    Wraps the raw :class:`sonolink.rest.schemas.info.GitObject` struct and
    exposes ``commit_time`` as a :class:`datetime.datetime`.
    """

    __slots__ = ("_cs_commit_time",)

    def __str__(self) -> str:
        return f"{self._data.branch}@{self._data.commit}"

    @property
    def branch(self) -> str:
        """The Git branch this build was made from."""
        return self._data.branch

    @property
    def commit(self) -> str:
        """The commit hash of this build."""
        return self._data.commit

    @cached_property("_cs_commit_time")
    def commit_time(self) -> datetime.datetime:
        """A :class:`datetime.datetime` representing when this commit was made."""
        return datetime.datetime.fromtimestamp(
            self._data.commit_time / 1000, tz=datetime.timezone.utc
        )


class ServerInfo(BaseModel[ServerInfoPayload]):
    """Represents a Lavalink server's metadata & stats information.

    This class wraps the raw :class:`sonolink.rest.schemas.InfoResponse` schema and provides
    a high-level interface for accessing Lavalink servers stats and metadata.
    """

    __slots__ = (
        "_cs_build_time",
        "_cs_version",
        "_cs_git",
    )

    @cached_property("_cs_version")
    def version(self) -> Version:
        """A :class:`Version` object denoting the version of this node."""
        return Version(client=self._client, data=self._data.version)

    @cached_property("_cs_build_time")
    def build_time(self) -> datetime.datetime:
        """A datetime.datetime object representing the timestamp on which the Lavalink
        jar was built.
        """
        return datetime.datetime.fromtimestamp(
            self._data.build_time / 1000, tz=datetime.timezone.utc
        )

    @cached_property("_cs_git")
    def git(self) -> GitInfo:
        """A :class:`GitInfo` object denoting the git version of the Lavalink server."""
        return GitInfo(client=self._client, data=self._data.git)

    @property
    def jvm(self) -> str:
        """The JVM version used to run the Lavalink server."""
        return self._data.jvm

    @property
    def lavaplayer(self) -> str:
        """The Lavaplayer version being used by the Lavalink server."""
        return self._data.lavaplayer

    @property
    def source_managers(self) -> list[str]:
        """The enabled source managers of the Lavalink server."""
        return self._data.source_managers

    @property
    def filters(self) -> list[str]:
        """The enabled filters of the Lavalink server."""
        return self._data.filters

    @property
    def plugins(self) -> list[PluginObject]:
        """A list of structs denoting the available plugins of the Lavalink server."""
        return self._data.plugins

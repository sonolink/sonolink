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

from typing import Literal, NamedTuple

__all__ = ("__version__", "version_info")


class VersionInfo(NamedTuple):
    major: int
    minor: int
    patch: int
    release_level: Literal["alpha", "beta", "candidate", "final"]

    def __str__(self) -> str:
        return self.as_str()

    def as_str(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        suffixes = {"alpha": "a0", "beta": "b0", "candidate": "rc0"}
        suffix = suffixes.get(self.release_level, "")
        return base + suffix


version_info = VersionInfo(major=1, minor=5, patch=0, release_level="alpha")
__version__ = version_info.as_str()

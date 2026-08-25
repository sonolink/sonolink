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

import importlib.metadata
import logging
import os
import sys
from typing import ClassVar, Literal, cast

from packaging.version import Version

from ._base import BasePlayer

FrameworkLiteral = Literal["discord.py", "pycord", "disnake", "nextcord"]

_log = logging.getLogger(__name__)


class PlayerFactory:
    _FRAMEWORK_DATA: ClassVar[dict[str, dict[str, str]]] = {
        "discord.py": {"pkg": "discord.py", "import_name": "discord", "min": "2.7"},
        "pycord": {"pkg": "py-cord", "import_name": "discord", "min": "2.8"},
        "disnake": {"pkg": "disnake", "import_name": "disnake", "min": "2.12"},
        "nextcord": {"pkg": "nextcord", "import_name": "nextcord", "min": "3.2"},
    }

    _available: ClassVar[dict[str, bool]] = {}
    _player_classes: ClassVar[dict[str, type[BasePlayer]]] = {}

    def __new__(cls) -> PlayerFactory:
        instance = super().__new__(cls)

        if cls._available:
            return instance

        pkg_to_providers = dict(importlib.metadata.packages_distributions())
        known_pkgs = {cls._normalize(d["pkg"]) for d in cls._FRAMEWORK_DATA.values()}

        for name, data in cls._FRAMEWORK_DATA.items():
            cls._available[name] = cls._check_available(
                data, pkg_to_providers, known_pkgs
            )

        return instance

    def get_player(
        self,
        framework: FrameworkLiteral,
    ) -> type[BasePlayer]:
        """Return the appropriate VoiceProtocol based on the framework string."""
        if framework in self._player_classes:
            return self._player_classes[framework]

        if not self._available.get(framework, False):
            min_ver = self._FRAMEWORK_DATA[framework]["min"]
            raise RuntimeError(
                f"Framework '{framework}' is not installed or does not meet "
                f"the minimum version requirement (v{min_ver}+)."
            )

        match framework:
            case "discord.py":
                from .adapters._dpy import DpyPlayer

                player_class = DpyPlayer
            case "pycord":
                from .adapters._pycord import PycordPlayer

                player_class = PycordPlayer
            case "disnake":
                from .adapters._disnake import DisnakePlayer

                player_class = DisnakePlayer
            case "nextcord":
                from .adapters._nextcord import NextcordPlayer

                player_class = NextcordPlayer

        self._player_classes[framework] = player_class
        return player_class

    def detect_framework(self) -> FrameworkLiteral:
        if env := os.environ.get("SONOLINK_FRAMEWORK"):
            return cast(FrameworkLiteral, env)

        available = [name for name, ok in self._available.items() if ok]

        if not available:
            raise RuntimeError(
                "No supported framework detected meeting the minimum version requirements.\n"
                "Ensure one of the following is installed: "
                "discord.py >= 2.7, py-cord >= 2.8, disnake >= 2.12 or nextcord >= 3.1.1"
            )

        if len(available) > 1:
            imported = [
                name
                for name in available
                if self._FRAMEWORK_DATA[name]["import_name"] in sys.modules
            ]
            if len(imported) == 1:
                return cast(FrameworkLiteral, imported[0])

            _log.warning(
                "Multiple frameworks detected: %s, using '%s'.\n"
                "Override this by passing 'framework' to sonolink.Client.",
                available,
                available[0],
            )

        return cast(FrameworkLiteral, available[0])

    def has_framework(self, framework: FrameworkLiteral) -> bool:
        return self._available.get(framework, False)

    @classmethod
    def _check_available(
        cls,
        data: dict[str, str],
        pkg_to_providers: dict[str, list[str]],
        known_pkgs: set[str],
    ) -> bool:
        pkg, import_name, min_ver = data["pkg"], data["import_name"], data["min"]

        try:
            installed = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            return False

        if Version(installed).release < Version(min_ver).release:
            _log.warning("Found %s v%s, but v%s+ is required.", pkg, installed, min_ver)
            return False

        providers = {cls._normalize(p) for p in pkg_to_providers.get(import_name, [])}
        return (providers & known_pkgs) == {cls._normalize(pkg)}

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().casefold().replace("_", "-").replace(".", "-")

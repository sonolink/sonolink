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

from enum import IntFlag
from typing import Any

import msgspec.json


class MessageType(IntFlag):
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    PING = 0x9
    PONG = 0xA
    CLOSE = 0x8


class Message:
    __slots__ = ("data", "flags")

    data: bytes | bytearray | str | None
    flags: MessageType

    def __init__(
        self,
        data: bytes | bytearray | str,
        flags: MessageType,
    ) -> None:
        self.data = data
        self.flags = flags

    def __repr__(self) -> str:
        return f"Message(flags={self.flags!r}, data_type={type(self.data).__name__})"

    def json(self) -> Any:
        if not isinstance(self.data, (bytes, bytearray)):
            raise TypeError("JSON decoding requires bytes-like data")
        return msgspec.json.decode(self.data)

    def text(self) -> str:
        if isinstance(self.data, (bytes, bytearray)):
            return self.data.decode("utf-8")
        return str(self.data)

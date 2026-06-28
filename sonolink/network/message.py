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

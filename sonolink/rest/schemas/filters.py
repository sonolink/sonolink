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

from typing import Any

import msgspec

__all__ = (
    "ChannelMixFilter",
    "DistortionFilter",
    "EqualizerFilter",
    "KaraokeFilter",
    "LowPassFilter",
    "PlayerFilters",
    "RotationFilter",
    "TimescaleFilter",
    "TremoloFilter",
    "VibratoFilter",
)


class PlayerFilters(msgspec.Struct, kw_only=True):
    """Represents the full filter payload for a Lavalink player.

    This object is sent in :class:`UpdatePlayerRequest` under ``filters``.
    Only provided attributes are updated; attributes set to ``None`` are ignored,
    allowing partial filter updates without resetting other filters.
    """

    volume: float | msgspec.UnsetType = msgspec.UNSET
    """Linear volume multiplier from ``0.0`` to ``5.0``. ``1.0`` is 100% volume. Values above ``1.0`` may clip."""

    equalizer: list[EqualizerFilter] | msgspec.UnsetType = msgspec.UNSET
    """List of :class:`EqualizerFilter` entries for bands ``0..14``."""

    karaoke: KaraokeFilter | msgspec.UnsetType = msgspec.UNSET
    """Karaoke configuration (:class:`KaraokeFilter`)."""

    timescale: TimescaleFilter | msgspec.UnsetType = msgspec.UNSET
    """Time-domain transform configuration (:class:`TimescaleFilter`)."""

    tremolo: TremoloFilter | msgspec.UnsetType = msgspec.UNSET
    """Volume oscillation configuration (:class:`TremoloFilter`)."""

    vibrato: VibratoFilter | msgspec.UnsetType = msgspec.UNSET
    """Pitch oscillation configuration (:class:`VibratoFilter`)."""

    rotation: RotationFilter | msgspec.UnsetType = msgspec.UNSET
    """Stereo rotation configuration (:class:`RotationFilter`)."""

    distortion: DistortionFilter | msgspec.UnsetType = msgspec.UNSET
    """Wave-shaping configuration (:class:`DistortionFilter`)."""

    channel_mix: ChannelMixFilter | msgspec.UnsetType = msgspec.field(
        name="channelMix",
        default=msgspec.UNSET,
    )
    """Cross-channel matrix configuration (:class:`ChannelMixFilter`)."""

    low_pass: LowPassFilter | msgspec.UnsetType = msgspec.field(
        name="lowPass", default=msgspec.UNSET
    )
    """Low-pass configuration (:class:`LowPassFilter`)."""

    plugin_filters: dict[str, Any] | msgspec.UnsetType = msgspec.field(
        name="pluginFilters",
        default=msgspec.UNSET,
    )
    """
    Plugin-defined filter payloads keyed by plugin name.
    Values are plugin-specific and passed through as-is.
    """


class EqualizerFilter(msgspec.Struct, kw_only=True):
    """Represents a single Lavalink equalizer band.

    Lavalink exposes 15 bands indexed ``0..14``. The frequencies are approximately:
    ``25, 40, 63, 100, 160, 250, 400, 630, 1000, 1600, 2500, 4000, 6300, 10000, 16000`` Hz.
    """

    band: int
    """Target band index from ``0`` to ``14``."""

    gain: float
    """Band gain multiplier from ``-0.25`` to ``1.0``. ``-0.25`` mutes the band and ``0.25`` roughly doubles it."""


class KaraokeFilter(msgspec.Struct, kw_only=True):
    """Represents karaoke filter configuration.

    This filter reduces content in a target frequency region, commonly used for
    vocal reduction.
    """

    level: float | msgspec.UnsetType = msgspec.UNSET
    """Overall effect intensity from ``0.0`` to ``1.0``."""

    mono_level: float | msgspec.UnsetType = msgspec.field(
        name="monoLevel", default=msgspec.UNSET
    )
    """Mono signal amount from ``0.0`` to ``1.0``."""

    filter_band: float | msgspec.UnsetType = msgspec.field(
        name="filterBand", default=msgspec.UNSET
    )
    """Center frequency in Hz for the target region."""

    filter_width: float | msgspec.UnsetType = msgspec.field(
        name="filterWidth", default=msgspec.UNSET
    )
    """Bandwidth around ``filter_band`` in Hz."""


class TimescaleFilter(msgspec.Struct, kw_only=True):
    """Represents timescale filter configuration.

    This filter changes perceived playback speed, pitch, and rate. In Lavalink,
    omitted values are treated as ``1.0``.
    """

    speed: float | msgspec.UnsetType = msgspec.UNSET
    """Playback speed multiplier (``0.0 <= x``). ``1.0`` is normal."""

    pitch: float | msgspec.UnsetType = msgspec.UNSET
    """Pitch multiplier (``0.0 <= x``). ``1.0`` is unchanged."""

    rate: float | msgspec.UnsetType = msgspec.UNSET
    """Internal rate multiplier (``0.0 <= x``)."""


class TremoloFilter(msgspec.Struct, kw_only=True):
    """Represents tremolo filter configuration.

    Tremolo rapidly oscillates output volume.
    """

    frequency: float | msgspec.UnsetType = msgspec.UNSET
    """Oscillation frequency in Hz (``0.0 < x``)."""

    depth: float | msgspec.UnsetType = msgspec.UNSET
    """Effect depth (``0.0 < x <= 1.0``)."""


class VibratoFilter(msgspec.Struct, kw_only=True):
    """Represents vibrato filter configuration.

    Vibrato rapidly oscillates output pitch.
    """

    frequency: float | msgspec.UnsetType = msgspec.UNSET
    """Oscillation frequency in Hz (``0.0 < x <= 14.0``)."""

    depth: float | msgspec.UnsetType = msgspec.UNSET
    """Effect depth (``0.0 < x <= 1.0``)."""


class RotationFilter(msgspec.Struct, kw_only=True):
    """Represents stereo rotation filter configuration."""

    rotation_hz: float | msgspec.UnsetType = msgspec.field(
        name="rotationHz", default=msgspec.UNSET
    )
    """Rotation frequency in Hz. ``0.2`` is a common slow rotation."""


class DistortionFilter(msgspec.Struct, kw_only=True):
    """Represents distortion filter configuration.

    Distortion combines sinusoidal and linear transforms. Small changes can
    produce large audible differences, so tune incrementally.
    """

    sin_offset: float | msgspec.UnsetType = msgspec.field(
        name="sinOffset", default=msgspec.UNSET
    )
    """Sine input offset component."""

    sin_scale: float | msgspec.UnsetType = msgspec.field(
        name="sinScale", default=msgspec.UNSET
    )
    """Sine scaling component."""

    cos_offset: float | msgspec.UnsetType = msgspec.field(
        name="cosOffset", default=msgspec.UNSET
    )
    """Cosine input offset component."""

    cos_scale: float | msgspec.UnsetType = msgspec.field(
        name="cosScale", default=msgspec.UNSET
    )
    """Cosine scaling component."""

    tan_offset: float | msgspec.UnsetType = msgspec.field(
        name="tanOffset", default=msgspec.UNSET
    )
    """Tangent input offset component."""

    tan_scale: float | msgspec.UnsetType = msgspec.field(
        name="tanScale", default=msgspec.UNSET
    )
    """Tangent scaling component."""

    offset: float | msgspec.UnsetType = msgspec.UNSET
    """Linear output offset applied after shaping."""

    scale: float | msgspec.UnsetType = msgspec.UNSET
    """Linear output scaling applied after shaping."""


class ChannelMixFilter(msgspec.Struct, kw_only=True):
    """Represents channel mix filter configuration.

    All coefficients satisfy ``0.0 <= x <= 1.0``.
    The default matrix keeps channels independent. Setting all coefficients to
    ``0.5`` yields dual-mono output.
    """

    left_to_left: float | msgspec.UnsetType = msgspec.field(
        name="leftToLeft", default=msgspec.UNSET
    )
    """Contribution of left input to left output."""

    left_to_right: float | msgspec.UnsetType = msgspec.field(
        name="leftToRight", default=msgspec.UNSET
    )
    """Contribution of left input to right output."""

    right_to_left: float | msgspec.UnsetType = msgspec.field(
        name="rightToLeft", default=msgspec.UNSET
    )
    """Contribution of right input to left output."""

    right_to_right: float | msgspec.UnsetType = msgspec.field(
        name="rightToRight", default=msgspec.UNSET
    )
    """Contribution of right input to right output."""


class LowPassFilter(msgspec.Struct, kw_only=True):
    """Represents low-pass filter configuration.

    Low-pass filtering suppresses higher frequencies while preserving lower ones.
    """

    smoothing: float | msgspec.UnsetType = msgspec.UNSET
    """Smoothing factor (``x > 1.0``). Values ``<= 1.0`` disable this filter."""

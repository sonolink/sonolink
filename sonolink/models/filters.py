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

import copy
from typing import TYPE_CHECKING, Any, Self

import msgspec

from ..rest.schemas import filters
from .base import BaseFilter, BaseModel

if TYPE_CHECKING:
    from ..gateway.client import Client

type FilterModelTypes = (
    Equalizer
    | Karaoke
    | Timescale
    | Tremolo
    | Vibrato
    | Rotation
    | Distortion
    | ChannelMix
    | LowPass
)

_SINGLE_FILTER_ATTRS: tuple[str, ...] = (
    "karaoke",
    "timescale",
    "tremolo",
    "vibrato",
    "rotation",
    "distortion",
    "channel_mix",
    "low_pass",
)


__all__ = (
    "ChannelMix",
    "Distortion",
    "Equalizer",
    "Filters",
    "Karaoke",
    "LowPass",
    "Rotation",
    "Timescale",
    "Tremolo",
    "Vibrato",
)


class Equalizer(BaseFilter[filters.EqualizerFilter]):
    """Represents a single Lavalink equalizer band.

    Parameters
    ----------
    band: :class:`int`
        The target band index (0 to 14).
    gain: :class:`float`
        The band gain multiplier (-0.25 to 1.0).
    """

    __slots__ = ()
    _schema_cls = filters.EqualizerFilter

    def __init__(
        self,
        *,
        band: int,
        gain: float,
    ) -> None:
        super().__init__(
            band=band,
            gain=gain,
        )

    @property
    def band(self) -> int:
        """The target band index (0 to 14)."""
        return self._data.band

    @band.setter
    def band(self, value: int) -> None:
        self._data.band = value

    @property
    def gain(self) -> float:
        """The band gain multiplier (-0.25 to 1.0)."""
        return self._data.gain

    @gain.setter
    def gain(self, value: float) -> None:
        self._data.gain = value


class Karaoke(BaseFilter[filters.KaraokeFilter]):
    """Filter that reduces vocal levels in a track, useful for karaoke.

    Parameters
    ----------
    level: :class:`float` | :data:`None`
        Overall effect intensity (0.0 to 1.0).
    mono_level: :class:`float` | :data:`None`
        Mono signal amount (0.0 to 1.0).
    filter_band: :class:`float` | :data:`None`
        Center frequency in Hz for the target region.
    filter_width: :class:`float` | :data:`None`
        Bandwidth around the filter band in Hz.
    """

    __slots__ = ()
    _schema_cls = filters.KaraokeFilter

    def __init__(
        self,
        *,
        level: float | None = None,
        mono_level: float | None = None,
        filter_band: float | None = None,
        filter_width: float | None = None,
    ) -> None:
        super().__init__(
            level=level,
            mono_level=mono_level,
            filter_band=filter_band,
            filter_width=filter_width,
        )

    @property
    def level(self) -> float | None:
        """Overall effect intensity (0.0 to 1.0)."""
        return self._get(self._data.level)

    @level.setter
    def level(self, value: float | None) -> None:
        self._data.level = self._set(value)

    @property
    def mono_level(self) -> float | None:
        """Mono signal amount (0.0 to 1.0)."""
        return self._get(self._data.mono_level)

    @mono_level.setter
    def mono_level(self, value: float | None) -> None:
        self._data.mono_level = self._set(value)

    @property
    def filter_band(self) -> float | None:
        """Center frequency in Hz for the target region."""
        return self._get(self._data.filter_band)

    @filter_band.setter
    def filter_band(self, value: float | None) -> None:
        self._data.filter_band = self._set(value)

    @property
    def filter_width(self) -> float | None:
        """Bandwidth around the filter band in Hz."""
        return self._get(self._data.filter_width)

    @filter_width.setter
    def filter_width(self, value: float | None) -> None:
        self._data.filter_width = self._set(value)


class Timescale(BaseFilter[filters.TimescaleFilter]):
    """Adjusts the speed, pitch, and rate of audio playback.

    Parameters
    ----------
    speed: :class:`float` | :data:`None`
        Playback speed multiplier (``0.0 <= x``).
    pitch: :class:`float` | :data:`None`
        Pitch multiplier (``0.0 <= x``).
    rate: :class:`float` | :data:`None`
        Internal rate multiplier (``0.0 <= x``).
    """

    __slots__ = ()
    _schema_cls = filters.TimescaleFilter

    def __init__(
        self,
        *,
        speed: float | None = None,
        pitch: float | None = None,
        rate: float | None = None,
    ) -> None:
        super().__init__(
            speed=speed,
            pitch=pitch,
            rate=rate,
        )

    @property
    def speed(self) -> float | None:
        """Playback speed multiplier (>= 0.0)."""
        return self._get(self._data.speed)

    @speed.setter
    def speed(self, value: float | None) -> None:
        self._data.speed = self._set(value)

    @property
    def pitch(self) -> float | None:
        """Pitch multiplier (>= 0.0)."""
        return self._get(self._data.pitch)

    @pitch.setter
    def pitch(self, value: float | None) -> None:
        self._data.pitch = self._set(value)

    @property
    def rate(self) -> float | None:
        """Internal rate multiplier (>= 0.0)."""
        return self._get(self._data.rate)

    @rate.setter
    def rate(self, value: float | None) -> None:
        self._data.rate = self._set(value)


class Tremolo(BaseFilter[filters.TremoloFilter]):
    """Rapidly oscillates the volume of the audio.

    Parameters
    ----------
    frequency: :class:`float` | :data:`None`
        Oscillation frequency in Hz (``0.0 < x``).
    depth: :class:`float` | :data:`None`
        Effect depth (``0.0 < x <= 1.0``).
    """

    __slots__ = ()
    _schema_cls = filters.TremoloFilter

    def __init__(
        self,
        *,
        frequency: float | None = None,
        depth: float | None = None,
    ) -> None:
        super().__init__(
            frequency=frequency,
            depth=depth,
        )

    @property
    def frequency(self) -> float | None:
        """Oscillation frequency in Hz (> 0.0)."""
        return self._get(self._data.frequency)

    @frequency.setter
    def frequency(self, value: float | None) -> None:
        self._data.frequency = self._set(value)

    @property
    def depth(self) -> float | None:
        """Effect depth (0.0 < x <= 1.0)."""
        return self._get(self._data.depth)

    @depth.setter
    def depth(self, value: float | None) -> None:
        self._data.depth = self._set(value)


class Vibrato(BaseFilter[filters.VibratoFilter]):
    """Rapidly oscillates the pitch of the audio.

    Parameters
    ----------
    frequency: :class:`float` | :data:`None`
        Oscillation frequency in Hz (``0.0 < x <= 14.0``).
    depth: :class:`float` | :data:`None`
        Effect depth (``0.0 < x <= 1.0``).
    """

    __slots__ = ()
    _schema_cls = filters.VibratoFilter

    def __init__(
        self,
        *,
        frequency: float | None = None,
        depth: float | None = None,
    ) -> None:
        super().__init__(
            frequency=frequency,
            depth=depth,
        )

    @property
    def frequency(self) -> float | None:
        """Oscillation frequency in Hz (0.0 < x <= 14.0)."""
        return self._get(self._data.frequency)

    @frequency.setter
    def frequency(self, value: float | None) -> None:
        self._data.frequency = self._set(value)

    @property
    def depth(self) -> float | None:
        """Effect depth (0.0 < x <= 1.0)."""
        return self._get(self._data.depth)

    @depth.setter
    def depth(self, value: float | None) -> None:
        self._data.depth = self._set(value)


class Rotation(BaseFilter[filters.RotationFilter]):
    """Rotates the audio across the stereo channels (panning effect).

    Parameters
    ----------
    rotation_hz: :class:`float` | :data:`None`
        Rotation frequency in Hz.
    """

    __slots__ = ()
    _schema_cls = filters.RotationFilter

    def __init__(
        self,
        *,
        rotation_hz: float | None = None,
    ) -> None:
        super().__init__(rotation_hz=rotation_hz)

    @property
    def rotation_hz(self) -> float | None:
        """Rotation frequency in Hz."""
        return self._get(self._data.rotation_hz)

    @rotation_hz.setter
    def rotation_hz(self, value: float | None) -> None:
        self._data.rotation_hz = self._set(value)


class Distortion(BaseFilter[filters.DistortionFilter]):
    """Applies distortion effects using sine, cosine, and tangent transforms.

    Parameters
    ----------
    sin_offset: :class:`float` | :data:`None`
        The sine input offset component.
    sin_scale: :class:`float` | :data:`None`
        The sine scaling component.
    cos_offset: :class:`float` | :data:`None`
        The cosine input offset component.
    cos_scale: :class:`float` | :data:`None`
        The cosine scaling component.
    tan_offset: :class:`float` | :data:`None`
        The tangent input offset component.
    tan_scale: :class:`float` | :data:`None`
        The tangent scaling component.
    offset: :class:`float` | :data:`None`
        The input offset component.
    scale: :class:`float` | :data:`None`
        The scaling component.
    """

    __slots__ = ()
    _schema_cls = filters.DistortionFilter

    def __init__(
        self,
        *,
        sin_offset: float | None = None,
        sin_scale: float | None = None,
        cos_offset: float | None = None,
        cos_scale: float | None = None,
        tan_offset: float | None = None,
        tan_scale: float | None = None,
        offset: float | None = None,
        scale: float | None = None,
    ) -> None:
        super().__init__(
            sin_offset=sin_offset,
            sin_scale=sin_scale,
            cos_offset=cos_offset,
            cos_scale=cos_scale,
            tan_offset=tan_offset,
            tan_scale=tan_scale,
            offset=offset,
            scale=scale,
        )

    @property
    def sin_offset(self) -> float | None:
        """The sine input offset component."""
        return self._get(self._data.sin_offset)

    @sin_offset.setter
    def sin_offset(self, value: float | None) -> None:
        self._data.sin_offset = self._set(value)

    @property
    def sin_scale(self) -> float | None:
        """The sine scaling component."""
        return self._get(self._data.sin_scale)

    @sin_scale.setter
    def sin_scale(self, value: float | None) -> None:
        self._data.sin_scale = self._set(value)

    @property
    def cos_offset(self) -> float | None:
        """The cosine input offset component."""
        return self._get(self._data.cos_offset)

    @cos_offset.setter
    def cos_offset(self, value: float | None) -> None:
        self._data.cos_offset = self._set(value)

    @property
    def cos_scale(self) -> float | None:
        """The cosine scaling component."""
        return self._get(self._data.cos_scale)

    @cos_scale.setter
    def cos_scale(self, value: float | None) -> None:
        self._data.cos_scale = self._set(value)

    @property
    def tan_offset(self) -> float | None:
        """The tangent input offset component."""
        return self._get(self._data.tan_offset)

    @tan_offset.setter
    def tan_offset(self, value: float | None) -> None:
        self._data.tan_offset = self._set(value)

    @property
    def tan_scale(self) -> float | None:
        """The tangent scaling component."""
        return self._get(self._data.tan_scale)

    @tan_scale.setter
    def tan_scale(self, value: float | None) -> None:
        self._data.tan_scale = self._set(value)

    @property
    def offset(self) -> float | None:
        """The input offset component."""
        return self._get(self._data.offset)

    @offset.setter
    def offset(self, value: float | None) -> None:
        self._data.offset = self._set(value)

    @property
    def scale(self) -> float | None:
        """The scaling component."""
        return self._get(self._data.scale)

    @scale.setter
    def scale(self, value: float | None) -> None:
        self._data.scale = self._set(value)


class ChannelMix(BaseFilter[filters.ChannelMixFilter]):
    """Mixes left and right audio channels to manipulate stereo separation.

    Parameters
    ----------
    left_to_left: :class:`float` | :data:`None`
        The left to left channel mix factor (``0.0 <= x <= 1.0``).
    left_to_right: :class:`float` | :data:`None`
        The left to right channel mix factor (``0.0 <= x <= 1.0``).
    right_to_left: :class:`float` | :data:`None`
        The right to left channel mix factor (``0.0 <= x <= 1.0``).
    right_to_right: :class:`float` | :data:`None`
        The right to right channel mix factor (``0.0 <= x <= 1.0``).
    """

    __slots__ = ()
    _schema_cls = filters.ChannelMixFilter

    def __init__(
        self,
        *,
        left_to_left: float | None = None,
        left_to_right: float | None = None,
        right_to_left: float | None = None,
        right_to_right: float | None = None,
    ) -> None:
        super().__init__(
            left_to_left=left_to_left,
            left_to_right=left_to_right,
            right_to_left=right_to_left,
            right_to_right=right_to_right,
        )

    @property
    def left_to_left(self) -> float | None:
        """The contribution of the left input channel to the left output channel."""
        return self._get(self._data.left_to_left)

    @left_to_left.setter
    def left_to_left(self, value: float | None) -> None:
        self._data.left_to_left = self._set(value)

    @property
    def left_to_right(self) -> float | None:
        """The contribution of the left input channel to the right output channel."""
        return self._get(self._data.left_to_right)

    @left_to_right.setter
    def left_to_right(self, value: float | None) -> None:
        self._data.left_to_right = self._set(value)

    @property
    def right_to_left(self) -> float | None:
        """The contribution of the right input channel to the left output channel."""
        return self._get(self._data.right_to_left)

    @right_to_left.setter
    def right_to_left(self, value: float | None) -> None:
        self._data.right_to_left = self._set(value)

    @property
    def right_to_right(self) -> float | None:
        """The contribution of the right input channel to the right output channel."""
        return self._get(self._data.right_to_right)

    @right_to_right.setter
    def right_to_right(self, value: float | None) -> None:
        self._data.right_to_right = self._set(value)


class LowPass(BaseFilter[filters.LowPassFilter]):
    """Suppresses higher frequencies in the audio signal.

    Parameters
    ----------
    smoothing: :class:`float` | :data:`None`
        The smoothing factor (``x > 1.0``).
    """

    __slots__ = ()
    _schema_cls = filters.LowPassFilter

    def __init__(
        self,
        *,
        smoothing: float | None = None,
    ) -> None:
        super().__init__(smoothing=smoothing)

    @property
    def smoothing(self) -> float | None:
        """Smoothing factor (x > 1.0)."""
        return self._get(self._data.smoothing)

    @smoothing.setter
    def smoothing(self, value: float | None) -> None:
        self._data.smoothing = self._set(value)


class Filters(BaseModel[filters.PlayerFilters]):
    """The main container for all active player filters.

    This class provides a Pythonic interface to the underlying Lavalink filter state.
    Active filters are sent to Lavalink via the :meth:`payload` property.

    Parameters
    ----------
    volume: float
        The linear volume multiplier. Defaults to 1.0.
    equalizer: list[Equalizer] | None
        A list of active equalizer bands.
    karaoke: :class:`Karaoke` | :data:`None`
        The active karaoke filter settings.
    timescale: :class:`Timescale` | :data:`None`
        The active timescale (speed/pitch) filter settings.
    tremolo: :class:`Tremolo` | :data:`None`
        The active tremolo (volume oscillation) filter settings.
    vibrato: :class:`Vibrato` | :data:`None`
        The active vibrato (pitch oscillation) filter settings.
    rotation: :class:`Rotation` | :data:`None`
        The active rotation (panning) filter settings.
    distortion: :class:`Distortion` | :data:`None`
        The active distortion filter settings.
    channel_mix: :class:`ChannelMix` | :data:`None`
        The active channel mix filter settings.
    low_pass: :class:`LowPass` | :data:`None`
        The active low pass filter settings.
    plugin_filters: :class:`dict` | :data:`None`
        A dictionary of raw plugin-defined filter payloads.
    """

    __slots__ = (
        "channel_mix",
        "distortion",
        "equalizer",
        "karaoke",
        "low_pass",
        "plugin_filters",
        "rotation",
        "timescale",
        "tremolo",
        "vibrato",
        "volume",
    )

    def __init__(
        self,
        *,
        equalizer: list[Equalizer] | None = None,
        karaoke: Karaoke | None = None,
        timescale: Timescale | None = None,
        tremolo: Tremolo | None = None,
        vibrato: Vibrato | None = None,
        rotation: Rotation | None = None,
        distortion: Distortion | None = None,
        channel_mix: ChannelMix | None = None,
        low_pass: LowPass | None = None,
        volume: float = 1.0,
        plugin_filters: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(client=None, data=filters.PlayerFilters())
        self.equalizer: list[Equalizer] = equalizer or []
        self.karaoke: Karaoke | None = karaoke
        self.timescale: Timescale | None = timescale
        self.tremolo: Tremolo | None = tremolo
        self.vibrato: Vibrato | None = vibrato
        self.rotation: Rotation | None = rotation
        self.distortion: Distortion | None = distortion
        self.channel_mix: ChannelMix | None = channel_mix
        self.low_pass: LowPass | None = low_pass
        self.volume: float = volume
        self.plugin_filters: dict[str, Any] = plugin_filters or {}

    @classmethod
    def _from_data(cls, client: Client[Any], data: filters.PlayerFilters) -> Self:
        eq_raw = data.equalizer if data.equalizer is not msgspec.UNSET else []

        instance = cls(
            equalizer=[Equalizer._from_data(client, e) for e in eq_raw],
            karaoke=cls._wrap(Karaoke, client, data.karaoke),
            timescale=cls._wrap(Timescale, client, data.timescale),
            tremolo=cls._wrap(Tremolo, client, data.tremolo),
            vibrato=cls._wrap(Vibrato, client, data.vibrato),
            rotation=cls._wrap(Rotation, client, data.rotation),
            distortion=cls._wrap(Distortion, client, data.distortion),
            channel_mix=cls._wrap(ChannelMix, client, data.channel_mix),
            low_pass=cls._wrap(LowPass, client, data.low_pass),
            volume=data.volume if data.volume is not msgspec.UNSET else 1.0,
            plugin_filters=data.plugin_filters
            if data.plugin_filters is not msgspec.UNSET
            else None,
        )

        instance._client = client
        instance._data = data
        return instance

    @classmethod
    def _wrap[C: FilterModelTypes](
        cls, model: type[C], client: Client[Any], data: Any
    ) -> C | None:
        return (
            model._from_data(client=client, data=data)
            if data is not msgspec.UNSET
            else None
        )

    def __or__(self, other: object) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.combine(other)

    def __ior__(self, other: object) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.merge(other)

    @property
    def payload(self) -> filters.PlayerFilters:
        """Returns the underlying msgspec schema for API requests."""
        return filters.PlayerFilters(
            volume=self.volume,
            equalizer=[e._data for e in self.equalizer] or msgspec.UNSET,
            karaoke=self.karaoke._data if self.karaoke else msgspec.UNSET,
            timescale=self.timescale._data if self.timescale else msgspec.UNSET,
            tremolo=self.tremolo._data if self.tremolo else msgspec.UNSET,
            vibrato=self.vibrato._data if self.vibrato else msgspec.UNSET,
            rotation=self.rotation._data if self.rotation else msgspec.UNSET,
            distortion=self.distortion._data if self.distortion else msgspec.UNSET,
            channel_mix=self.channel_mix._data if self.channel_mix else msgspec.UNSET,
            low_pass=self.low_pass._data if self.low_pass else msgspec.UNSET,
            plugin_filters=self.plugin_filters or msgspec.UNSET,
        )

    def merge(self, other: Filters) -> Self:
        """Merge another filter set into this instance in place.

        This mutates ``self``. Use :meth:`combine` when you need a new
        merged :class:`Filters` instance without changing either input.

        Parameters
        ----------
        other: :class:`Filters`
            The other filter to merge with.

        Returns
        -------
        :class:`Filters`
            This filter instance after merging.
        """
        if not isinstance(other, type(self)):
            raise TypeError(
                f"Can only merge filters of the same type, got {type(other).__name__}"
            )

        for attr in _SINGLE_FILTER_ATTRS:
            self_filter = getattr(self, attr)
            other_filter = getattr(other, attr)

            if self_filter and other_filter:
                self_filter.merge(other_filter)
            elif other_filter:
                setattr(self, attr, other_filter)

        if other.equalizer:
            if self.equalizer:
                self.equalizer.extend(other.equalizer)
            else:
                self.equalizer = other.equalizer
            self.equalizer.sort(key=lambda f: f.band)

        if other.plugin_filters:
            if self.plugin_filters:
                self.plugin_filters.update(other.plugin_filters)
            else:
                self.plugin_filters = other.plugin_filters

        if other.volume != 1.0 and other.volume != self.volume:
            self.volume = other.volume

        return self

    def combine(self, other: Filters) -> Self:
        """Return a new filter set with ``other`` merged into a copy of this one.

        This does not mutate either input. Use :meth:`merge` when you want
        in-place mutation of the current instance.

        Parameters
        ----------
        other: :class:`Filters`
            The other filter to combine with.

        Returns
        -------
        :class:`Filters`
            This filter instance after combining.
        """
        if not isinstance(other, type(self)):
            raise TypeError(
                f"Can only combine filters of the same type, got {type(other).__name__}"
            )

        return copy.deepcopy(self).merge(other)

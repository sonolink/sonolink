from __future__ import annotations

from typing import Any, cast

import msgspec
import pytest

from sonolink.models import (
    ChannelMix,
    Distortion,
    Equalizer,
    Filters,
    Karaoke,
    LowPass,
    Rotation,
    Timescale,
    Tremolo,
    Vibrato,
)


class TestIndividualFilters:
    @pytest.mark.parametrize(
        ("filter_model", "expected"),
        [
            (Karaoke(), (None, None, None, None)),
            (Timescale(), (None, None, None)),
            (Tremolo(), (None, None)),
            (Vibrato(), (None, None)),
            (Rotation(), (None,)),
            (Distortion(), (None, None, None, None, None, None, None, None)),
            (ChannelMix(), (None, None, None, None)),
            (LowPass(), (None,)),
        ],
    )
    def test_optional_fields_default_to_none(
        self,
        filter_model: Karaoke
        | Timescale
        | Tremolo
        | Vibrato
        | Rotation
        | Distortion
        | ChannelMix
        | LowPass,
        expected: tuple[None, ...],
    ) -> None:
        values = tuple(
            getattr(filter_model, field)
            for field in filter_model.data.__struct_fields__
        )

        assert values == expected
        assert all(
            getattr(filter_model.data, field) is msgspec.UNSET
            for field in filter_model.data.__struct_fields__
        )

    def test_merge_prefers_other_non_none_fields(self) -> None:
        base = Timescale(speed=1.0, pitch=0.9)
        other = Timescale(speed=1.2, rate=1.1)

        result = base.merge(other)

        assert result is base
        assert (base.speed, base.pitch, base.rate) == (1.2, 0.9, 1.1)

    def test_combine_does_not_mutate_inputs(self) -> None:
        base = Timescale(speed=1.0, pitch=0.9)
        other = Timescale(speed=1.2, rate=1.1)

        result = base.combine(other)

        assert isinstance(result, Timescale)
        assert result is not base
        assert (result.speed, result.pitch, result.rate) == (1.2, 0.9, 1.1)
        assert (base.speed, base.pitch, base.rate) == (1.0, 0.9, None)
        assert (other.speed, other.pitch, other.rate) == (1.2, None, 1.1)

    def test_wrong_type_merge_and_combine_raise(self) -> None:
        timescale = Timescale(speed=1.0)

        with pytest.raises(TypeError, match=r"Cannot merge.*Karaoke.*Timescale"):
            timescale.merge(cast(Any, Karaoke()))
        with pytest.raises(TypeError, match=r"Cannot merge.*Karaoke.*Timescale"):
            timescale.combine(cast(Any, Karaoke()))


class TestFilters:
    def test_defaults_build_partial_wire_payload(self) -> None:
        filters = Filters()
        payload = filters.payload

        assert filters.volume == 1.0
        assert not filters.equalizer
        assert filters.plugin_filters == {}
        assert payload.volume == 1.0
        assert all(
            getattr(payload, field) is msgspec.UNSET
            for field in payload.__struct_fields__
            if field != "volume"
        )

    def test_documented_combination_builds_wire_payload(self) -> None:
        filters = Filters(
            equalizer=[Equalizer(band=0, gain=0.15)],
            timescale=Timescale(speed=1.1, pitch=1.1),
            rotation=Rotation(rotation_hz=0.2),
            tremolo=Tremolo(frequency=4.0, depth=0.3),
            plugin_filters={"plugin": {"strength": 0.75}},
            volume=0.8,
        )
        payload = filters.payload

        assert payload.volume == 0.8
        assert isinstance(payload.equalizer, list)
        assert not isinstance(payload.timescale, msgspec.UnsetType)
        assert not isinstance(payload.rotation, msgspec.UnsetType)
        assert not isinstance(payload.tremolo, msgspec.UnsetType)
        assert payload.equalizer[0].band == 0
        assert payload.equalizer[0].gain == 0.15
        assert payload.timescale.speed == 1.1
        assert payload.timescale.pitch == 1.1
        assert payload.rotation.rotation_hz == 0.2
        assert payload.tremolo.frequency == 4.0
        assert payload.tremolo.depth == 0.3
        assert payload.plugin_filters == {"plugin": {"strength": 0.75}}
        assert payload.karaoke is msgspec.UNSET

    def test_merge_mutates_and_prefers_other_values(self) -> None:
        base = Filters(
            equalizer=[Equalizer(band=2, gain=0.1)],
            timescale=Timescale(speed=1.0, pitch=0.9),
            plugin_filters={"shared": 1, "base": True},
            volume=0.8,
        )
        other = Filters(
            equalizer=[Equalizer(band=0, gain=0.2)],
            timescale=Timescale(speed=1.2, rate=1.1),
            rotation=Rotation(rotation_hz=0.2),
            plugin_filters={"shared": 2},
            volume=0.7,
        )

        result = base.merge(other)

        assert result is base
        assert isinstance(result, Filters)
        assert isinstance(base.timescale, Timescale)
        assert (base.timescale.speed, base.timescale.pitch, base.timescale.rate) == (
            1.2,
            0.9,
            1.1,
        )
        assert base.rotation is other.rotation
        assert [(band.band, band.gain) for band in base.equalizer] == [
            (0, 0.2),
            (2, 0.1),
        ]
        assert base.plugin_filters == {"shared": 2, "base": True}
        assert base.volume == 0.7

    def test_combine_and_or_do_not_mutate_original(self) -> None:
        base = Filters(timescale=Timescale(speed=1.0))
        other = Filters(rotation=Rotation(rotation_hz=0.2))

        combined = base.combine(other)
        operated = base | other

        assert isinstance(combined, Filters)
        assert combined is not base
        assert operated.payload == combined.payload
        assert base.rotation is None
        assert isinstance(base.timescale, Timescale)
        assert base.timescale.speed == 1.0
        assert other.timescale is None

    def test_ior_matches_merge_and_preserves_identity(self) -> None:
        explicit = Filters(timescale=Timescale(speed=1.0))
        operated = Filters(timescale=Timescale(speed=1.0))
        extra = Filters(rotation=Rotation(rotation_hz=0.2))
        original_id = id(operated)

        explicit.merge(extra)
        operated |= extra

        assert id(operated) == original_id
        assert operated.payload == explicit.payload

    def test_wrong_type_merge_and_combine_raise(self) -> None:
        filters = Filters()

        with pytest.raises(TypeError, match="same type, got Timescale"):
            filters.merge(cast(Any, Timescale()))
        with pytest.raises(TypeError, match="same type, got Timescale"):
            filters.combine(cast(Any, Timescale()))

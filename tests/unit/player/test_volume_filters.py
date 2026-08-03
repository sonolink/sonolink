from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from sonolink.models.filters import Filters

from ...helpers import ConcreteTestPlayer


class TestPlayerVolume:

    def test_default_volume(self, ready_player: ConcreteTestPlayer) -> None:
        assert ready_player.volume == 100

    async def test_set_volume_updates_property(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        await ready_player.set_volume(50)
        assert ready_player.volume == 50

    async def test_set_volume_notifies_node(
        self, ready_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
    ) -> None:
        await ready_player.set_volume(75)

        data = mock_rest_manager.update_player.await_args.kwargs["data"]
        assert data.volume == 75

    async def test_set_volume_accepts_bounds(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        await ready_player.set_volume(0)
        assert ready_player.volume == 0

        await ready_player.set_volume(1000)
        assert ready_player.volume == 1000

    async def test_set_volume_rejects_negative(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        with pytest.raises(ValueError, match="between 0 and 1000"):
            await ready_player.set_volume(-1)

    async def test_set_volume_rejects_over_max(
        self, ready_player: ConcreteTestPlayer
    ) -> None:
        with pytest.raises(ValueError, match="between 0 and 1000"):
            await ready_player.set_volume(1001)


class TestPlayerFilters:

    def test_default_filters_is_empty(self, ready_player: ConcreteTestPlayer) -> None:
        assert isinstance(ready_player.filters, Filters)

    async def test_set_filters_notifies_node(
        self, ready_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
    ) -> None:
        filters = Filters(volume=1.5)
        await ready_player.set_filters(filters)

        data = mock_rest_manager.update_player.await_args.kwargs["data"]
        assert data.filters == filters.payload

    async def test_set_filters_without_seek_updates_once(
        self, ready_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
    ) -> None:
        await ready_player.set_filters(Filters())

        assert mock_rest_manager.update_player.await_count == 1

    async def test_set_filters_with_seek_also_seeks(
        self, ready_player: ConcreteTestPlayer, mock_rest_manager: MagicMock
    ) -> None:
        await ready_player.set_filters(Filters(), seek=True)

        assert mock_rest_manager.update_player.await_count == 2

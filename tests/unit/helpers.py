from __future__ import annotations

from sonolink.rest.schemas.info import (
    CPUObject,
    FrameStatsObject,
    MemoryObject,
    StatsResponse,
)


def make_stats(
    *,
    players: int = 0,
    playing_players: int = 0,
    uptime: int = 60000,
    system_load: float = 0.0,
    lavalink_load: float = 0.0,
    cores: int = 4,
    frame_stats: FrameStatsObject | None = None,
) -> StatsResponse:
    return StatsResponse(
        players=players,
        playing_players=playing_players,
        uptime=uptime,
        memory=MemoryObject(
            free=1_000_000,
            used=500_000,
            allocated=1_500_000,
            reservable=2_000_000,
        ),
        cpu=CPUObject(
            cores=cores,
            system_load=system_load,
            lavalink_load=lavalink_load,
        ),
        frame_stats=frame_stats,
    )

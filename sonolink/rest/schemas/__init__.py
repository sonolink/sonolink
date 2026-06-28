"""
sonolink.rest.schemas
~~~~~~~~~~~~~~~~~~~~~

Submodule containing all the schemas used in the rest module.

:copyright: (c) 2026-present SonoLink Development Team
:license: MIT
"""

from .filters import *
from .info import *
from .planner import *
from .player import *
from .playlist import *
from .session import *
from .track import *

__all__ = (
    "CPUObject",
    "ChannelMixFilter",
    "DestroyPlayerResponse",
    "DetailsObject",
    "DistortionFilter",
    "EqualizerFilter",
    "FailingAddressObject",
    "FrameStatsObject",
    "GetPlayerResponse",
    "GetPlayersResponse",
    "GitObject",
    "IPBlockObject",
    "InfoResponse",
    "KaraokeFilter",
    "LowPassFilter",
    "MemoryObject",
    "Player",
    "PlayerFilters",
    "PlayerState",
    "PlayerVoiceState",
    "PlaylistData",
    "PlaylistInfo",
    "PluginObject",
    "RotationFilter",
    "RoutePlannerStatusResponse",
    "StatsResponse",
    "TimescaleFilter",
    "Track",
    "TrackDecodeResponse",
    "TrackInfo",
    "TrackLoadingResponse",
    "TracksDecodeResponse",
    "TremoloFilter",
    "UnmarkAllFailedAddressesResponse",
    "UnmarkFailedAddressRequest",
    "UnmarkFailedAddressResponse",
    "UpdatePlayerRequest",
    "UpdatePlayerResponse",
    "UpdatePlayerTrackRequest",
    "UpdateSessionRequest",
    "UpdateSessionResponse",
    "VersionObject",
    "VersionResponse",
    "VibratoFilter",
)

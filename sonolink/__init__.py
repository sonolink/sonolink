"""
sonolink
~~~~~~~~

A high-performance Lavalink v4 wrapper for Python, inspired by WaveLink.

:copyright: (c) 2026-present SonoLink Development Team
:license: MIT
"""

from . import gateway, models, rest, utils
from ._registry import get_client
from ._version import __version__, version_info
from .gateway import *
from .network.errors import *
from .rest import *
from .utils import *

__all__ = (
    "AutoPlayMode",
    "Client",
    "DisconnectTriggerType",
    "ErrorResponseType",
    "ExceptionSeverity",
    "HTTPException",
    "History",
    "HistoryEmpty",
    "IPBlockType",
    "InactivityMode",
    "InvalidNodePassword",
    "Node",
    "NodeError",
    "NodeRegion",
    "NodeStatus",
    "NodeURINotFound",
    "Player",
    "PlayerConnectionState",
    "PlayerDisconnectEvent",
    "Queue",
    "QueueEmpty",
    "QueueMode",
    "RoutePlannerType",
    "SearchProvider",
    "TrackEndReason",
    "TrackExceptionSeverity",
    "TrackLoadResult",
    "TrackSourceType",
    "WebSocketClosedEvent",
    "WebSocketError",
    "__version__",
    "cached_property",
    "gateway",
    "get_client",
    "models",
    "rest",
    "utils",
    "version_info",
)

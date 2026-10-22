"""
sonolink.gateway
~~~~~~~~~~~~~~~~

Module that handles gateway-related objects.

:copyright: (c) 2026-present SonoLink Development Team
:license: Apache-2.0
"""

from .client import *
from .enums import *
from .errors import *
from .event_models import *
from .node import *
from .player import *
from .queue import *

__all__ = (
    "AutoPlayMode",
    "AutoPlaySeedMissing",
    "Client",
    "DisconnectTriggerType",
    "EventModel",
    "FrameworkClientMismatch",
    "FrameworkImportError",
    "History",
    "HistoryEmpty",
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
    "PlayerUpdateEvent",
    "Queue",
    "QueueEmpty",
    "QueueMode",
    "ReadyEvent",
    "SearchProvider",
    "ShuffleMode",
    "StatsEvent",
    "TrackEndEvent",
    "TrackEndReason",
    "TrackExceptionEvent",
    "TrackExceptionSeverity",
    "TrackStartEvent",
    "TrackStuckEvent",
    "WebSocketClosedEvent",
)

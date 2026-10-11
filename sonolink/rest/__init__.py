"""
sonolink.rest
~~~~~~~~~~~~~

Module that handles rest-related objects.

:copyright: (c) 2026-present SonoLink Development Team
:license: Apache-2.0
"""

from .enums import *
from .errors import *

__all__ = (
    "ErrorResponseType",
    "ExceptionSeverity",
    "HTTPException",
    "IPBlockType",
    "RoutePlannerType",
    "TrackLoadResult",
    "TrackSourceType",
)

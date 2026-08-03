from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def error_context() -> MagicMock:
    context = MagicMock()
    context.operation = None
    context.expected_error = None
    context.error_message = None
    return context

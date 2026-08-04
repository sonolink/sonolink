from __future__ import annotations

import pytest

import sonolink


class TestErrorCatching:
    def test_catch_sonolink_exception(self) -> None:
        try:
            raise sonolink.SonoLinkException("test")
        except sonolink.SonoLinkException:
            pass  # Expected

    def test_catch_node_error_as_sonolink_exception(self) -> None:
        try:
            raise sonolink.NodeError("test")
        except sonolink.SonoLinkException:
            pass  # Expected

    def test_catch_specific_error(self) -> None:
        node = object()
        with pytest.raises(sonolink.NodeURINotFound):
            raise sonolink.NodeURINotFound(node)  # type: ignore[arg-type]

    def test_cannot_catch_wrong_error_type(self) -> None:
        with pytest.raises(sonolink.NodeError):
            try:
                raise sonolink.NodeError("test")
            except sonolink.QueueEmpty:
                pass  # Should not reach here


class TestErrorHandlingScenarios:
    def test_handle_queue_empty(self) -> None:

        def operation_requiring_queue() -> None:
            raise sonolink.QueueEmpty("Queue is empty.")

        with pytest.raises(sonolink.QueueEmpty):
            operation_requiring_queue()

    def test_handle_history_empty(self) -> None:

        def history_operation() -> None:
            raise sonolink.HistoryEmpty("History is empty.")

        with pytest.raises(sonolink.HistoryEmpty):
            history_operation()

    def test_handle_node_uri_not_found(self) -> None:

        def get_node(node_id: str) -> object:
            if node_id == "nonexistent":
                raise sonolink.NodeURINotFound(object())  # type: ignore[arg-type]
            return object()

        with pytest.raises(sonolink.NodeURINotFound):
            get_node("nonexistent")


class TestErrorFallthrough:
    def test_error_fallthrough_to_general(self) -> None:

        def operation() -> None:
            raise sonolink.NodeError("specific error")

        try:
            operation()
        except sonolink.SonoLinkException as e:
            assert isinstance(e, sonolink.NodeError)

    def test_multiple_error_types(self) -> None:
        errors: list[sonolink.SonoLinkException] = [
            sonolink.NodeError("node error"),
            sonolink.QueueEmpty("queue error"),
            sonolink.HistoryEmpty("history error"),
        ]

        for error in errors:
            assert isinstance(error, sonolink.SonoLinkException)

from __future__ import annotations

import sonolink


class TestErrorInstantiation:
    def test_sonolink_exception_message(self) -> None:
        error = sonolink.SonoLinkException("Test error")
        assert str(error) == "Test error"

    def test_node_error_message(self) -> None:
        error = sonolink.NodeError("Node failed")
        assert "Node failed" in str(error)

    def test_queue_empty_message(self) -> None:
        error = sonolink.QueueEmpty("Queue is empty.")
        error_str = str(error)
        assert "empty" in error_str.lower()

    def test_history_empty_message(self) -> None:
        error = sonolink.HistoryEmpty("History is empty.")
        assert "empty" in str(error).lower()

    def test_node_uri_not_found_message(self) -> None:
        error = sonolink.NodeURINotFound(object())  # type: ignore[arg-type]
        assert str(error) is not None

    def test_invalid_node_password_message(self) -> None:
        error = sonolink.InvalidNodePassword(object())  # type: ignore[arg-type]
        assert str(error) is not None


class TestErrorWithDetails:
    def test_node_error_with_node_id(self) -> None:
        node_id = "primary-node"
        error = sonolink.NodeError(f"Node {node_id} failed")
        assert node_id in str(error)

    def test_queue_empty_with_context(self) -> None:
        guild_id = 123456789
        error = sonolink.QueueEmpty(f"Guild {guild_id} queue is empty.")
        assert str(guild_id) in str(error)

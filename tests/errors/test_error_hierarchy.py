from __future__ import annotations

import sonolink


class TestErrorHierarchy:

    def test_sonolink_exception_is_exception(self) -> None:
        assert issubclass(sonolink.SonoLinkException, Exception)

    def test_node_error_inherits_sonolink_exception(self) -> None:
        assert issubclass(sonolink.NodeError, sonolink.SonoLinkException)

    def test_invalid_node_password_inherits_node_error(self) -> None:
        assert issubclass(sonolink.InvalidNodePassword, sonolink.NodeError)

    def test_node_uri_not_found_inherits_node_error(self) -> None:
        assert issubclass(sonolink.NodeURINotFound, sonolink.NodeError)

    def test_history_empty_inherits_sonolink_exception(self) -> None:
        assert issubclass(sonolink.HistoryEmpty, sonolink.SonoLinkException)

    def test_queue_empty_inherits_sonolink_exception(self) -> None:
        assert issubclass(sonolink.QueueEmpty, sonolink.SonoLinkException)

    def test_autoplay_seed_missing_inherits_exception(self) -> None:
        assert issubclass(sonolink.AutoPlaySeedMissing, Exception)


class TestErrorInheritanceChain:

    def test_invalid_node_password_inheritance_chain(self) -> None:
        node = object()
        error = sonolink.InvalidNodePassword(node)  # type: ignore[arg-type]

        assert isinstance(error, sonolink.InvalidNodePassword)
        assert isinstance(error, sonolink.NodeError)
        assert isinstance(error, sonolink.SonoLinkException)
        assert isinstance(error, Exception)

    def test_node_uri_not_found_inheritance_chain(self) -> None:
        node = object()
        error = sonolink.NodeURINotFound(node)  # type: ignore[arg-type]

        assert isinstance(error, sonolink.NodeURINotFound)
        assert isinstance(error, sonolink.NodeError)
        assert isinstance(error, sonolink.SonoLinkException)
        assert isinstance(error, Exception)

    def test_history_empty_inheritance_chain(self) -> None:
        error = sonolink.HistoryEmpty("History is empty.")

        assert isinstance(error, sonolink.HistoryEmpty)
        assert isinstance(error, sonolink.SonoLinkException)
        assert isinstance(error, Exception)

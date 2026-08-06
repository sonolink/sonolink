from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from sonolink import Client


class TestClientInitialization:
    def test_client_init_with_discord_py(self, mock_discord_client: MagicMock) -> None:
        mock_discord_client.__class__.__module__ = "discord"

        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock(),
        ):
            client = Client(mock_discord_client, framework="discord.py")

            assert client.framework == "discord.py"
            assert client.nodes == []
            assert len(client._nodes) == 0

    def test_client_init_with_auto_framework_detection(
        self, client: Client[MagicMock]
    ) -> None:
        assert client.framework == "discord.py"

    def test_client_init_duplicate_client_raises_error(
        self, mock_discord_client: MagicMock
    ) -> None:
        with (
            patch(
                "sonolink.gateway.client._factory.ClientFactory.create",
                return_value=MagicMock(),
            ),
            patch(
                "sonolink.gateway.player.PlayerFactory.detect_framework",
                return_value="discord.py",
            ),
        ):
            Client(mock_discord_client)

            with pytest.raises(RuntimeError, match="already attached"):
                Client(mock_discord_client)

    def test_client_repr(self, client: Client[MagicMock]) -> None:
        assert "Client" in repr(client)

from unittest.mock import MagicMock, patch

import pytest

from sonolink import Client
from sonolink.gateway.player._factory import FrameworkLiteral


class TestFrameworkDetection:

    def test_discord_py_framework(self) -> None:
        mock_discord_client = MagicMock()
        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock()
        ):
            client = Client(mock_discord_client, framework="discord.py")
            assert client.framework == "discord.py"

    def test_pycord_framework(self) -> None:
        mock_client = MagicMock()
        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock()
        ):
            client = Client(mock_client, framework="pycord")
            assert client.framework == "pycord"

    def test_disnake_framework(self) -> None:
        mock_client = MagicMock()
        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock()
        ):
            client = Client(mock_client, framework="disnake")
            assert client.framework == "disnake"

    def test_nextcord_framework(self) -> None:
        mock_client = MagicMock()
        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock()
        ):
            client = Client(mock_client, framework="nextcord")
            assert client.framework == "nextcord"


class TestAutoFrameworkDetection:

    def test_auto_detect_discord_py(self) -> None:
        mock_discord_client = MagicMock()
        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock()
        ):
            with patch(
                "sonolink.gateway.player.PlayerFactory.detect_framework",
                return_value="discord.py"
            ):
                client = Client(mock_discord_client)
                assert client.framework == "discord.py"

    def test_auto_detect_pycord(self) -> None:
        mock_client = MagicMock()
        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock()
        ):
            with patch(
                "sonolink.gateway.player.PlayerFactory.detect_framework",
                return_value="pycord"
            ):
                client = Client(mock_client)
                assert client.framework == "pycord"


class TestFrameworkInteroperability:

    @pytest.mark.parametrize(
        "framework", ["discord.py", "pycord", "disnake", "nextcord"]
    )
    async def test_operations_framework_agnostic(
        self, framework: FrameworkLiteral
    ) -> None:
        mock_client = MagicMock()
        with patch(
            "sonolink.gateway.client._factory.ClientFactory.create",
            return_value=MagicMock()
        ):
            client = Client(mock_client, framework=framework)

            # Create node (should work with any framework)
            node = client.create_node(
                uri="ws://localhost:2333",
                password="test"
            )
            assert node in client.nodes

            # Get node (should work with any framework)
            assert client.get_node(node.id) is node

"""
This example requires the discord.py[voice] (https://pypi.org/project/discord.py/) library to be installed.

This example covers the procedure of creating a simple music bot using sonolink,
with event handlers for track lifecycle and node events.

This requires an active Lavalink server, for more information on setting up one
you can check the guide at: https://sonolink.readthedocs.io/en/latest/guides/lavalink-setup.html

:copyright: (c) 2026-present SonoLink Development Team
"""

from typing import Any

import discord
from discord.ext import commands

import sonolink


# We subclass commands.Bot to hold our sonolink.Client instance cleanly.
# This avoids relying on globals and makes the client easy to access anywhere.
class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents(guilds=True, voice_states=True)

        super().__init__(
            intents=intents,
            command_prefix=[],  # We won't be using prefix commands in this example, so we can set it to an empty list
        )

        self.sl_client: sonolink.Client[Any] = sonolink.Client(self)

    async def setup_hook(self) -> None:
        # discord.py will automatically call 'setup_hook', and is the
        # safest place to start our client.
        await self.sl_client.start()
        print("SonoLink nodes connected successfully!")


bot = Bot()

# Register the node we want to connect to. You can register multiple nodes
# and sonolink will automatically load-balance between them via 'get_best_node'.
bot.sl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
)


# Fired when a node has successfully connected and is ready to accept players.
# 'event.resumed' tells us whether this was a fresh connection or a resume.
@bot.event
async def on_sonolink_node_ready(event: sonolink.gateway.ReadyEvent) -> None:
    print(f"Node {event.node.id!r} is ready! (resumed={event.resumed})")


# Fired when a node connection is lost or manually closed.
@bot.event
async def on_sonolink_node_close(node: sonolink.Node) -> None:
    print(f"Node {node.id!r} closed.")


# Fired when Lavalink sends a statistics update for the node.
# 'event.players' and 'event.playing_players' give player counts,
# 'event.uptime' is the node uptime in milliseconds,
# and 'event.memory' / 'event.cpu' contain resource usage stats.
@bot.event
async def on_sonolink_stats_receive(
    node: sonolink.Node, event: sonolink.gateway.StatsEvent
) -> None:
    print(
        f"Node {node.id!r}: {event.playing_players}/{event.players} players, "
        f"uptime={event.uptime}ms"
    )


# Fired when the voice WebSocket connection to Lavalink is closed.
# 'event.code' is the WebSocket close code, 'event.reason' describes why,
# and 'event.by_remote' indicates whether the close was initiated by the remote end.
@bot.event
async def on_sonolink_websocket_closed(
    player: sonolink.Player, event: sonolink.gateway.WebSocketClosedEvent
) -> None:
    print(
        f"[{player.guild}] Voice WS closed. "
        f"code={event.code}, reason={event.reason!r}, by_remote={event.by_remote}"
    )


# Fired each time Lavalink sends a position/state update for a player.
# This happens frequently (roughly every 5 seconds by default).
@bot.event
async def on_sonolink_player_update(
    player: sonolink.Player, event: sonolink.gateway.PlayerUpdateEvent
) -> None:
    # This event fires very often; avoid heavy work here.
    pass


# Fired when a track begins playing.
@bot.event
async def on_sonolink_track_start(
    player: sonolink.Player, event: sonolink.gateway.TrackStartEvent
) -> None:
    print(f"[{player.guild}] Started: {event.track.title!r} by {event.track.author!r}")


# Fired when a track finishes, is skipped, or is replaced.
# 'event.reason' is a TrackEndReason enum describing why it ended.
# NOTE: sonolink automatically calls 'player.skip()' internally when the reason
# allows starting the next track, so you do not need to advance the queue here.
@bot.event
async def on_sonolink_track_end(
    player: sonolink.Player, event: sonolink.gateway.TrackEndEvent
) -> None:
    print(f"[{player.guild}] Ended: {event.track.title!r} (reason={event.reason})")


# Fired when Lavalink encounters an error while playing a track.
# 'event.exception.message' contains the error description from Lavalink.
@bot.event
async def on_sonolink_track_exception(
    player: sonolink.Player, event: sonolink.gateway.TrackExceptionEvent
) -> None:
    print(
        f"[{player.guild}] Exception on {event.track.title!r}: "
        f"{event.exception.message}"
    )


# Fired when a track gets stuck and stops progressing.
# 'event.threshold' is the number of milliseconds Lavalink waited before giving up.
@bot.event
async def on_sonolink_track_stuck(
    player: sonolink.Player, event: sonolink.gateway.TrackStuckEvent
) -> None:
    print(
        f"[{player.guild}] Track {event.track.title!r} got stuck "
        f"after {event.threshold}ms."
    )


if __name__ == "__main__":
    bot.run("TOKEN")

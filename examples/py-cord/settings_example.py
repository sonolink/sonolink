"""
This example requires the py-cord[voice] (https://pypi.org/project/py-cord/) library to be installed.

This example covers how to configure sonolink's settings objects and wire them
into your bot. Settings are split into two groups:

- Node-level: CacheSettings, InactivitySettings (shared across all players)
- Player-level: AutoPlaySettings, HistorySettings (unique per player)

This requires an active Lavalink server, for more information on setting up one
you can check the guide at: https://sonolink.readthedocs.io/en/latest/guides/lavalink-setup.html

:copyright: (c) 2026-present SonoLink Development Team
"""

from typing import Any

import discord

import sonolink
import sonolink.models
from sonolink.gateway.enums import (
    AutoPlayMode,
    InactivityMode,
    QueueMode,
    SearchProvider,
)
from sonolink.models import (
    AutoPlaySettings,
    CacheSettings,
    HistorySettings,
    InactivitySettings,
)


# We subclass discord.Bot to hold our sonolink.Client instance cleanly.
# This avoids relying on globals and makes the client easy to access anywhere.
class Bot(discord.Bot):
    def __init__(self) -> None:
        intents = discord.Intents(guilds=True, voice_states=True)

        super().__init__(intents=intents)

        self.sl_client: sonolink.Client[Any] = sonolink.Client(self)

    async def on_connect(self) -> None:
        await super().on_connect()

        await self.sl_client.start()
        print("SonoLink nodes connected successfully!")


bot = Bot()

# CacheSettings and InactivitySettings apply to every player on the node.
bot.sl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
    cache_settings=CacheSettings(
        enabled=True,
        max_items=500,
    ),
    inactivity_settings=InactivitySettings(
        timeout=300,
        mode=InactivityMode.ALL_BOTS,
        # mode=InactivityMode.ONLY_SELF,
        # mode=InactivityMode.IGNORED_USERS,
        # user_ids=[discord.Object(id=YOUR_USER_ID)],  # required for IGNORED_USERS
    ),
)


@bot.slash_command(name="play", description="Plays a song.")
@discord.option("query", description="The song name or URL to search for.")
async def play(ctx: discord.ApplicationContext, query: str) -> None:
    await ctx.defer()

    assert isinstance(ctx.author, discord.Member)
    vc = ctx.guild.voice_client if ctx.guild else None

    if vc is None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.respond("You must be in a voice channel!")
            return

        # AutoPlaySettings and HistorySettings are per-player, so they are
        # passed when creating the player via Node.create_player().
        node = bot.sl_client.get_best_node()
        player = node.create_player(
            queue_mode=QueueMode.NORMAL,
            autoplay_settings=AutoPlaySettings(
                mode=AutoPlayMode.ENABLED,
                # mode=AutoPlayMode.PARTIAL,
                # mode=AutoPlayMode.DISABLED,
                provider=SearchProvider.YOUTUBE,
                # provider=SearchProvider.SPOTIFY,
                # provider=SearchProvider.DEEZER,
                max_seeds=100,
                discovery_count=10,
            ),
            history_settings=HistorySettings(
                enabled=True,
                max_items=50,
            ),
        )

        vc = await ctx.author.voice.channel.connect(cls=player)

    assert isinstance(vc, sonolink.Player)

    result = await bot.sl_client.search_track(query)

    if result.is_error() or result.is_empty() or result.result is None:
        await ctx.respond("Could not find any tracks!")
        return

    data = result.result
    track = (
        data[0]
        if isinstance(data, list)
        else (data.tracks[0] if isinstance(data, sonolink.models.Playlist) else data)
    )

    vc.queue.put(track)

    if not vc.current:
        to_play = vc.queue.get()
        await vc.play(to_play)
        await ctx.respond(f"Now playing `{to_play.title}` by `{to_play.author}`!")
    else:
        await ctx.respond(f"Added `{track.title}` by `{track.author}` to the queue!")


# AutoPlay mode can also be changed on an existing player at any time.
# Note: this raises RuntimeError if history is disabled on the player.
@bot.slash_command(name="autoplay", description="Toggles AutoPlay on or off.")
async def autoplay(ctx: discord.ApplicationContext) -> None:
    vc = ctx.guild.voice_client if ctx.guild else None

    if not isinstance(vc, sonolink.Player):
        await ctx.respond("Not connected to a voice channel!")
        return

    if vc.autoplay is AutoPlayMode.DISABLED:
        vc.autoplay = AutoPlayMode.ENABLED
        await ctx.respond("AutoPlay enabled!")
    else:
        vc.autoplay = AutoPlayMode.DISABLED
        await ctx.respond("AutoPlay disabled!")


if __name__ == "__main__":
    bot.run("TOKEN")

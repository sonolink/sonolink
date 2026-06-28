# This example requires the py-cord[voice] (https://pypi.org/project/py-cord/) library to be installed.
#
# This example covers how to configure sonolink's settings objects and wire them
# into your bot. Settings are split into two groups:
#
# - Node-level: CacheSettings, InactivitySettings (shared across all players)
# - Player-level: AutoPlaySettings, HistorySettings (unique per player)
#
# This requires an active Lavalink server, for more information on setting up one
# you can check the guide at: https://sonolink.readthedocs.io/en/latest/guides/lavalink-setup.html

from typing import Any, cast

import discord

import sonolink
import sonolink.models


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

# Register the node we want to connect to. You can register multiple nodes
# and sonolink will automatically load-balance between them via 'get_best_node'.
bot.sl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
)


# Here we will define some simple play, pause, resume, stop and skip commands.


@bot.slash_command(name="play", description="Plays a song.")
@discord.option("query", description="The song name or URL to search for.")
async def play(ctx: discord.ApplicationContext, query: str) -> None:
    await ctx.defer()

    # Here we must check whether we have an active player on the guild
    # if we don't, we will connect to the author voice channel, if available.

    assert isinstance(ctx.author, discord.Member)
    vc = ctx.guild.voice_client if ctx.guild else None

    if vc is None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.respond("You must be in a voice channel!")
            return

        vc = await ctx.author.voice.channel.connect(cls=sonolink.Player)

    assert isinstance(vc, sonolink.Player)

    # Now, we will search 'query' with Lavalink and play the obtained track, if available
    result = await bot.sl_client.search_track(query)

    if result.is_error() or result.is_empty() or result.result is None:
        await ctx.respond("Could not find any tracks!")
        return

    data = result.result

    if isinstance(data, list):
        track = data[0]
    elif isinstance(data, sonolink.models.Playlist):
        track = data.tracks[0]
    else:
        track = data

    # Add our track to the queue, and play it if there is no current song
    vc.queue.put(track)

    if not vc.current:
        to_play = vc.queue.get()
        await vc.play(to_play)
        await ctx.respond(f"Now playing `{to_play.title}` by `{to_play.author}`!")
    else:
        await ctx.respond(f"Added `{track.title}` by `{track.author}` to the queue!")


@bot.slash_command(name="pause", description="Pauses the current playing song.")
async def pause(ctx: discord.ApplicationContext) -> None:
    vc = ctx.voice_client

    if not isinstance(vc, sonolink.Player):
        await ctx.respond("Not connected to a voice channel!")
        return

    await vc.pause()
    await ctx.respond("Paused!")


@bot.slash_command(name="resume", description="Resumes the current playing song.")
async def resume(ctx: discord.ApplicationContext) -> None:
    vc = ctx.voice_client if ctx.voice_client else None

    if not isinstance(vc, sonolink.Player):
        await ctx.respond("Not connected to a voice channel!")
        return

    await vc.resume()
    await ctx.respond("Resumed!")


@bot.slash_command(name="stop", description="Stops playback and disconnect the bot.")
async def stop(ctx: discord.ApplicationContext) -> None:
    vc = ctx.voice_client if ctx.voice_client else None

    if not isinstance(vc, sonolink.Player):
        await ctx.respond("Already disconnected!")
        return

    await cast(sonolink.Player, vc).disconnect()
    await ctx.respond("Disconnected!")


@bot.slash_command(name="skip", description="Skips the current song.")
async def skip(ctx: discord.ApplicationContext) -> None:
    vc = ctx.voice_client if ctx.voice_client else None

    if not isinstance(vc, sonolink.Player):
        await ctx.respond("Not connected to a voice channel!")
        return

    # 'skip' will raise 'QueueEmpty' if there are no tracks in queue
    try:
        track = await vc.skip()
    except sonolink.QueueEmpty:
        await ctx.respond("There is no track to skip to!")
    else:
        if not track:
            await ctx.respond("Skipped!")
            return

        await ctx.respond(f"Skipped to `{track.title}` by `{track.author}`!")


if __name__ == "__main__":
    bot.run("TOKEN")

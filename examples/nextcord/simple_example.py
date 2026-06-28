# This example requires the nextcord[voice] (https://pypi.org/project/nextcord/) library to be installed.
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

import nextcord
from nextcord.ext import commands

import sonolink
import sonolink.models


# We subclass commands.Bot to hold our sonolink.Client instance cleanly.
# This avoids relying on globals and makes the client easy to access anywhere.
class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = nextcord.Intents(guilds=True, voice_states=True)
        super().__init__(intents=intents)

        self.sl_client: sonolink.Client[Any] = sonolink.Client(self)


bot = Bot()

# Register the node we want to connect to. You can register multiple nodes
# and sonolink will automatically load-balance between them via 'get_best_node'.
bot.sl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
)


# Called when the bot has successfully connected to Discord.
# We start the sonolink client here so nodes are ready before events fire.
@bot.listen()
async def on_connect() -> None:
    await bot.sl_client.start()
    print("SonoLink nodes connected successfully!")


# We will define some simple play, pause, resume, stop and skip commands.


@bot.slash_command(name="play", description="Plays a song.")
async def play(
    inter: nextcord.Interaction[Bot],
    query: str = nextcord.SlashOption(
        description="The song name or URL to search for.",
        required=True,
    ),
) -> None:
    await inter.response.defer()

    # Ensure we are in a guild and the author is a Member to resolve 'voice' type
    if not inter.guild or not isinstance(inter.user, nextcord.Member):
        await inter.followup.send("This command must be used in a server!")
        return

    vc = inter.guild.voice_client

    if vc is None:
        if not inter.user.voice or not inter.user.voice.channel:
            await inter.followup.send("You must be in a voice channel!")
            return

        vc = await inter.user.voice.channel.connect(cls=sonolink.Player)

    assert isinstance(vc, sonolink.Player)

    # Now, we will search 'query' with Lavalink and play the obtained track, if available
    result = await bot.sl_client.search_track(query)

    if result.is_error() or result.is_empty() or result.result is None:
        await inter.followup.send("Could not find any tracks!")
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
        await inter.followup.send(
            f"Now playing `{to_play.title}` by `{to_play.author}`!"
        )
    else:
        await inter.followup.send(
            f"Added `{track.title}` by `{track.author}` to the queue!"
        )


@bot.slash_command(name="pause", description="Pauses the current playing song.")
async def pause(inter: nextcord.Interaction[Bot]) -> None:
    vc = inter.guild.voice_client if inter.guild else None

    if not isinstance(vc, sonolink.Player):
        await inter.response.send_message("Not connected to a voice channel!")
        return

    await vc.pause()
    await inter.response.send_message("Paused!")


@bot.slash_command(name="resume", description="Resumes the current playing song.")
async def resume(inter: nextcord.Interaction[Bot]) -> None:
    vc = inter.guild.voice_client if inter.guild else None

    if not isinstance(vc, sonolink.Player):
        await inter.response.send_message("Not connected to a voice channel!")
        return

    await vc.resume()
    await inter.response.send_message("Resumed!")


@bot.slash_command(name="stop", description="Stops playback and disconnect the bot.")
async def stop(inter: nextcord.Interaction[Bot]) -> None:
    vc = inter.guild.voice_client if inter.guild else None

    if not isinstance(vc, sonolink.Player):
        await inter.response.send_message("Already disconnected!")
        return

    await cast(sonolink.Player, vc).disconnect()
    await inter.response.send_message("Disconnected!")


@bot.slash_command(name="skip", description="Skips the current song.")
async def skip(inter: nextcord.Interaction[Bot]) -> None:
    vc = inter.guild.voice_client if inter.guild else None

    if not isinstance(vc, sonolink.Player):
        await inter.response.send_message("Not connected to a voice channel!")
        return

    # 'skip' will raise 'QueueEmpty' if there are no tracks in queue
    try:
        track = await vc.skip()
    except sonolink.QueueEmpty:
        await inter.response.send_message("There is no track to skip to!")
    else:
        if not track:
            await inter.response.send_message("Skipped!")
            return

        await inter.response.send_message(
            f"Skipped to `{track.title}` by `{track.author}`!"
        )


if __name__ == "__main__":
    bot.run("TOKEN")

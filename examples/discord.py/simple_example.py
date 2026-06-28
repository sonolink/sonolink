# This example requires the discord.py[voice] (https://pypi.org/project/discord.py/) library to be installed.
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
from discord import app_commands
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

        # Sync slash commands to Discord
        await self.tree.sync()
        print("Slash commands synced!")


bot = Bot()

# Register the node we want to connect to. You can register multiple nodes
# and sonolink will automatically load-balance between them via 'get_best_node'.
bot.sl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
)

# We will define some simple play, pause, resume, stop and skip commands.


@bot.tree.command(name="play", description="Plays a song.")
@app_commands.describe(query="The song name or URL to search for.")
async def play(interaction: discord.Interaction, query: str) -> None:
    await interaction.response.defer()

    # Here we must check whether we have an active player on the guild
    # if we don't, we will connect to the author voice channel, if available.

    assert isinstance(interaction.user, discord.Member)
    vc = interaction.guild.voice_client if interaction.guild else None

    if vc is None:
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You must be in a voice channel!")
            return

        vc = await interaction.user.voice.channel.connect(cls=sonolink.Player)

    assert isinstance(vc, sonolink.Player)

    # Now, we will search 'query' with Lavalink and play the obtained track, if available
    result = await bot.sl_client.search_track(query)

    if result.is_error() or result.is_empty() or result.result is None:
        await interaction.followup.send("Could not find any tracks!")
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
        await interaction.followup.send(
            f"Now playing `{to_play.title}` by `{to_play.author}`!"
        )
    else:
        await interaction.followup.send(
            f"Added `{track.title}` by `{track.author}` to the queue!"
        )


@bot.tree.command(name="pause", description="Pauses the current playing song.")
async def pause(interaction: discord.Interaction) -> None:
    vc = interaction.guild.voice_client if interaction.guild else None

    if not isinstance(vc, sonolink.Player):
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    await vc.pause()
    await interaction.response.send_message("Paused!")


@bot.tree.command(name="resume", description="Resumes the current playing song.")
async def resume(interaction: discord.Interaction) -> None:
    vc = interaction.guild.voice_client if interaction.guild else None

    if not isinstance(vc, sonolink.Player):
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    await vc.resume()
    await interaction.response.send_message("Resumed!")


@bot.tree.command(name="stop", description="Stops playback and disconnect the bot.")
async def stop(interaction: discord.Interaction) -> None:
    vc = interaction.guild.voice_client if interaction.guild else None

    if not isinstance(vc, sonolink.Player):
        await interaction.response.send_message("Already disconnected!")
        return

    await cast(sonolink.Player, vc).disconnect()
    await interaction.response.send_message("Disconnected!")


@bot.tree.command(name="skip", description="Skips the current song.")
async def skip(interaction: discord.Interaction) -> None:
    vc = interaction.guild.voice_client if interaction.guild else None

    if not isinstance(vc, sonolink.Player):
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    # 'skip' will raise 'QueueEmpty' if there are no tracks in queue
    try:
        track = await vc.skip()
    except sonolink.QueueEmpty:
        await interaction.response.send_message("There is no track to skip to!")
    else:
        if not track:
            await interaction.response.send_message("Skipped!")
            return

        await interaction.response.send_message(
            f"Skipped to `{track.title}` by `{track.author}`!"
        )


if __name__ == "__main__":
    bot.run("TOKEN")

# This example requires the discord.py[voice] (https://pypi.org/project/discord.py/) library to be installed.
#
# This example covers an advanced music bot using sonolink, featuring a full
# queue system, volume control, track history, seeking, and playlist support.
#
# This requires an active Lavalink server, for more information on setting up one
# you can check the guide at: https://sonolink.readthedocs.io/en/latest/guides/lavalink-setup.html

from typing import Any, Literal

import discord
from discord import app_commands
from discord.ext import commands

import sonolink
import sonolink.models
from sonolink.gateway.enums import NodeRegion, QueueMode
from sonolink.rest.enums import TrackSourceType


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

# Register the nodes we want to connect to. You can omit 'regions' for normal
# penalty-based selection, or provide regions for region-aware selection.
# Matching node regions are preferred when the Discord voice channel exposes
# an rtc_region; otherwise selection falls back to penalty-based load balancing
# across all connected nodes.
bot.sl_client.create_node(
    uri="YOUR_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
    id="default",
)
bot.sl_client.create_node(
    uri="YOUR_US_EAST_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
    id="us-east",
    regions=[NodeRegion.US_EAST, NodeRegion.US_CENTRAL],
)
bot.sl_client.create_node(
    uri="YOUR_EU_LAVALINK_URI",
    password="YOUR_LAVALINK_PASSWORD",
    id="rotterdam",
    regions=[NodeRegion.ROTTERDAM],
)


# Helper function for DRY (Don't Repeat Yourself)
def _player_check(interaction: discord.Interaction) -> sonolink.Player | None:
    """Return the active Player for this guild, or None if not connected."""
    vc = interaction.guild.voice_client if interaction.guild else None
    return vc if isinstance(vc, sonolink.Player) else None


# -----------------
# Playback commands
# -----------------


async def query_autocomplete(
    _: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    if not current:
        return []

    result = await bot.sl_client.search_track(current, source=TrackSourceType.YOUTUBE)

    if result.is_error() or result.is_empty() or result.result is None:
        return []

    data = result.result

    if isinstance(data, sonolink.models.Playlist):
        return [app_commands.Choice(name=data.name[:100], value=data.name)]

    tracks = data if isinstance(data, list) else [data]
    return [
        app_commands.Choice(
            name=f"{t.title} - {t.author}"[:100], value=t.uri or t.title
        )
        for t in tracks
        if t.title
    ][:25]


@bot.tree.command(name="play", description="Plays a track or playlist.")
@app_commands.describe(query="The song name or URL to search for.")
@app_commands.autocomplete(query=query_autocomplete)
async def play(interaction: discord.Interaction, query: str) -> None:
    """Plays a track or playlist, or adds it to the queue if something is already playing.

    Supports plain search queries as well as direct URLs (YouTube, SoundCloud, etc.).
    When a playlist URL is provided, all tracks are enqueued.
    """
    # Defer since searching/connecting can take longer than 3 seconds
    await interaction.response.defer()

    assert isinstance(interaction.user, discord.Member)
    vc = interaction.guild.voice_client if interaction.guild else None

    # Connect to the author's voice channel if we are not already in one.
    if vc is None:
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You must be in a voice channel!")
            return

        vc = await interaction.user.voice.channel.connect(cls=sonolink.Player)

    assert isinstance(vc, sonolink.Player)

    # Search for the query. By default this searches YouTube; pass a
    # 'source' kwarg (e.g. TrackSourceType.SOUNDCLOUD) to change that.
    result = await bot.sl_client.search_track(query, source=TrackSourceType.YOUTUBE)

    if result.is_error() or result.is_empty() or result.result is None:
        await interaction.followup.send("Could not find any tracks!")
        return

    data = result.result

    # Depending on the result type we either get a single track, a list of
    # search results, or a full playlist. We handle all three cases here.
    if isinstance(data, sonolink.models.Playlist):
        # Playlist: play the first track immediately and queue the rest.
        first, *rest = data.tracks
        vc.queue.put(first)

        if rest:
            vc.queue.put(rest)

        if not vc.current:
            await vc.play(vc.queue.get())
            await interaction.followup.send(
                f"Now playing `{first.title}` and queued {len(rest)} more tracks "
                f"from playlist `{data.name}`!"
            )
        else:
            await interaction.followup.send(
                f"Added `{data.name}` ({len(data.tracks)} tracks) to the queue!"
            )
        return

    # Single track or top search result.
    track = data[0] if isinstance(data, list) else data
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


@bot.tree.command(name="pause", description="Pauses the current track.")
async def pause(interaction: discord.Interaction) -> None:
    """Pauses the current track."""
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    if vc.paused:
        await interaction.response.send_message(
            "Already paused! Use `/resume` to continue."
        )
        return

    await vc.pause()
    await interaction.response.send_message("Paused!")


@bot.tree.command(name="resume", description="Resumes the player if it is paused.")
async def resume(interaction: discord.Interaction) -> None:
    """Resumes the player if it is paused."""
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    if not vc.paused:
        await interaction.response.send_message("Not paused!")
        return

    await vc.resume()
    await interaction.response.send_message("Resumed!")


@bot.tree.command(name="skip", description="Skips the current track.")
async def skip(interaction: discord.Interaction) -> None:
    """Skips the current track and plays the next one in the queue."""
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    # 'skip' raises QueueEmpty when there are no further tracks to advance to.
    try:
        track = await vc.skip()
    except sonolink.QueueEmpty:
        await interaction.response.send_message(
            "The queue is empty — nothing to skip to!"
        )
        return

    if track:
        await interaction.response.send_message(
            f"Skipped to `{track.title}` by `{track.author}`!"
        )
    else:
        await interaction.response.send_message("Skipped! Nothing left in the queue.")


@bot.tree.command(name="previous", description="Goes back to the previous track.")
async def previous(interaction: discord.Interaction) -> None:
    """Goes back to the previous track in the history."""
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    # 'previous' raises HistoryEmpty when there is no track to go back to.
    try:
        track = await vc.previous()
    except sonolink.HistoryEmpty:
        await interaction.response.send_message("No previous track in history!")
        return

    await interaction.response.send_message(
        f"Going back to `{track.title}` by `{track.author}`!"
    )


@bot.tree.command(name="seek", description="Seeks to a position (seconds).")
@app_commands.describe(seconds="The position in seconds to jump to.")
async def seek(interaction: discord.Interaction, seconds: int) -> None:
    """Seeks to a position in the current track (in seconds).

    Example: /seek 90  →  jumps to the 1:30 mark.
    """
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    if not vc.current:
        await interaction.response.send_message("Nothing is playing!")
        return

    await vc.seek(seconds * 1000)
    await interaction.response.send_message(f"Sought to {seconds}s!")


@bot.tree.command(name="stop", description="Stops playback and disconnects.")
async def stop(interaction: discord.Interaction) -> None:
    """Stop playback, clear the queue, and disconnects the bot."""
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Already disconnected!")
        return

    await vc.disconnect()
    await interaction.response.send_message("Disconnected and cleared the queue!")


# --------------
# Queue commands
# --------------


@bot.tree.command(name="queue", description="Display the current queue.")
async def queue(interaction: discord.Interaction) -> None:
    """Display the current queue (up to 10 upcoming tracks)."""
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    tracks = vc.queue.tracks
    autoplay_tracks = vc.queue.autoplay_tracks

    if not tracks and not autoplay_tracks and not vc.current:
        await interaction.response.send_message("The queue is empty!")
        return

    lines: list[str] = []

    if vc.current:
        ap_label = " `[AutoPlay]`" if vc.current.autoplay else ""
        lines.append(
            f"**Now playing:** `{vc.current.title}` by `{vc.current.author}`{ap_label}\n"
        )

    if tracks:
        lines.append("**Up next:**")
        for i, track in enumerate(tracks[:10], start=1):
            lines.append(f"`{i}.` `{track.title}` by `{track.author}`")
        if len(tracks) > 10:
            lines.append(f"*...and {len(tracks) - 10} more.*")

    if autoplay_tracks:
        lines.append("\n**AutoPlay suggestions:**")
        for i, track in enumerate(autoplay_tracks[:5], start=1):
            lines.append(f"`{i}.` `{track.title}` by `{track.author}`")
        if len(autoplay_tracks) > 5:
            lines.append(f"*...and {len(autoplay_tracks) - 5} more.*")

    await interaction.response.send_message("\n".join(lines))


@bot.tree.command(name="shuffle", description="Shuffles the current queue.")
async def shuffle(interaction: discord.Interaction) -> None:
    """Shuffles the current queue in place."""
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    if not vc.queue.tracks:
        await interaction.response.send_message("The queue is empty!")
        return

    vc.queue.shuffle()
    await interaction.response.send_message("Queue shuffled!")


@bot.tree.command(name="loop", description="Set the loop mode.")
@app_commands.describe(mode="Choose from: track, all, off")
async def loop(
    interaction: discord.Interaction, mode: Literal["track", "all", "off"] = "track"
) -> None:
    """Set the loop mode. Options: 'track', 'all', 'off'.

    - track: repeats the current track indefinitely.
    - all:   loops the entire queue once it finishes.
    - off:   disables looping.
    """
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    mapping = {
        "track": QueueMode.LOOP,
        "all": QueueMode.LOOP_ALL,
        "off": QueueMode.NORMAL,
    }

    # Literal type ensures 'mode' is one of the valid strings
    vc.queue.mode = mapping[mode]
    await interaction.response.send_message(f"Loop mode set to `{mode}`!")


# ---------------
# Player settings
# ---------------


@bot.tree.command(name="volume", description="Set the player volume (0–1000).")
@app_commands.describe(value="Volume level between 0 and 1000.")
async def volume(
    interaction: discord.Interaction, value: app_commands.Range[int, 0, 1000]
) -> None:
    """Set the player volume (0–1000). Default is 100."""
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    # app_commands.Range ensures the value stays between 0 and 1000 in the UI
    await vc.set_volume(value)
    await interaction.response.send_message(f"Volume set to `{value}`!")


@bot.tree.command(name="nowplaying", description="Shows current track info.")
async def nowplaying(interaction: discord.Interaction) -> None:
    """Show information about the currently playing track."""
    vc = _player_check(interaction)
    if not vc:
        await interaction.response.send_message("Not connected to a voice channel!")
        return

    track = vc.current
    if not track:
        await interaction.response.send_message("Nothing is playing right now!")
        return

    # Convert milliseconds to a readable mm:ss position / duration.
    def fmt(ms: int) -> str:
        s = ms // 1000
        return f"{s // 60}:{s % 60:02d}"

    await interaction.response.send_message(
        f"**Now playing:** `{track.title}` by `{track.author}`\n"
        f"**Position:** `{fmt(vc.position)}` / `{fmt(track.length)}`\n"
        f"**Volume:** `{vc.volume}` | **Loop:** `{vc.queue.mode.name.lower()}`"
    )


if __name__ == "__main__":
    bot.run("TOKEN")

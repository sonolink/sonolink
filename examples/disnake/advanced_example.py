# This example requires the disnake[voice] (https://pypi.org/project/disnake/) library to be installed.
#
# This example covers an advanced music bot using sonolink, featuring a full
# queue system, volume control, track history, seeking, and playlist support.
#
# This requires an active Lavalink server, for more information on setting up one
# you can check the guide at: https://sonolink.readthedocs.io/en/latest/guides/lavalink-setup.html

from typing import Any

import disnake
from disnake.ext import commands

import sonolink
import sonolink.models
from sonolink.gateway.enums import NodeRegion, QueueMode, ShuffleMode
from sonolink.rest.enums import TrackSourceType


# We subclass commands.InteractionBot to hold our sonolink.Client instance cleanly.
# This avoids relying on globals and makes the client easy to access anywhere.
class Bot(commands.InteractionBot):
    def __init__(self) -> None:
        intents = disnake.Intents(guilds=True, voice_states=True)
        super().__init__(intents=intents)

        self.sl_client: sonolink.Client[Any] = sonolink.Client(self)


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


# Called when the bot has successfully connected to Discord.
# We start the sonolink client here so nodes are ready before events fire.
@bot.listen()
async def on_connect() -> None:
    await bot.sl_client.start()
    print("SonoLink nodes connected successfully!")


# Helper function for DRY (Don't Repeat Yourself)
def _player_check(
    inter: disnake.ApplicationCommandInteraction[Bot],
) -> sonolink.Player | None:
    """Return the active Player for this guild, or None if not connected."""
    vc = inter.guild.voice_client if inter.guild else None
    return vc if isinstance(vc, sonolink.Player) else None


# -----------------
# Playback commands
# -----------------


async def query_autocomplete(
    _: disnake.ApplicationCommandInteraction[Bot],
    string: str,
) -> list[str]:
    if not string:
        return []

    result = await bot.sl_client.search_track(string, source=TrackSourceType.YOUTUBE)

    if result.is_error() or result.is_empty() or result.result is None:
        return []

    data = result.result

    if isinstance(data, sonolink.models.Playlist):
        return [data.name[:100]]

    tracks = data if isinstance(data, list) else [data]
    return [f"{t.title} - {t.author}"[:100] for t in tracks if t.title][:25]


@bot.slash_command(name="play", description="Plays a track or playlist.")
async def play(
    inter: disnake.ApplicationCommandInteraction[Bot],
    query: str = commands.Param(  # pyright: ignore[reportUnknownMemberType]
        description="The song name or URL to search for.",
        autocomplete=query_autocomplete,
    ),
) -> None:
    """Plays a track or playlist, or adds it to the queue if something is already playing.

    Supports plain search queries as well as direct URLs (YouTube, SoundCloud, etc.).
    When a playlist URL is provided, all tracks are enqueued.
    """
    # Defer since searching/connecting can take longer than 3 seconds
    await inter.response.defer()

    # Ensure we are in a guild and the author is a Member to resolve 'voice' type
    if not inter.guild or not isinstance(inter.author, disnake.Member):
        await inter.followup.send("This command can only be used in a server.")
        return

    vc = inter.guild.voice_client

    if vc is None:
        if not inter.author.voice or not inter.author.voice.channel:
            await inter.followup.send("You must be in a voice channel!")
            return

        vc = await inter.author.voice.channel.connect(cls=sonolink.Player)

    assert isinstance(vc, sonolink.Player)

    # Search for the query. By default this searches YouTube; pass a
    # 'source' kwarg (e.g. TrackSourceType.SOUNDCLOUD) to change that.
    result = await bot.sl_client.search_track(query, source=TrackSourceType.YOUTUBE)

    if result.is_error() or result.is_empty() or result.result is None:
        await inter.followup.send("Could not find any tracks!")
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
            await inter.followup.send(
                f"Now playing `{first.title}` and queued {len(rest)} more tracks "
                f"from playlist `{data.name}`!"
            )
        else:
            await inter.followup.send(
                f"Added `{data.name}` ({len(data.tracks)} tracks) to the queue!"
            )
        return

    # Single track or top search result.
    track = data[0] if isinstance(data, list) else data
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


@bot.slash_command(name="pause", description="Pauses the current track.")
async def pause(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Pauses the current track."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    if vc.paused:
        await inter.response.send_message("Already paused! Use `/resume` to continue.")
        return

    await vc.pause()
    await inter.response.send_message("Paused!")


@bot.slash_command(name="resume", description="Resumes the player if it is paused.")
async def resume(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Resumes the player if it is paused."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    if not vc.paused:
        await inter.response.send_message("Not paused!")
        return

    await vc.resume()
    await inter.response.send_message("Resumed!")


@bot.slash_command(name="skip", description="Skips the current track.")
async def skip(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Skips the current track and plays the next one in the queue."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    # 'skip' raises QueueEmpty when there are no further tracks to advance to.
    try:
        track = await vc.skip()
    except sonolink.QueueEmpty:
        await inter.response.send_message("The queue is empty — nothing to skip to!")
        return

    if track:
        await inter.response.send_message(
            f"Skipped to `{track.title}` by `{track.author}`!"
        )
    else:
        await inter.response.send_message("Skipped! Nothing left in the queue.")


@bot.slash_command(name="previous", description="Goes back to the previous track.")
async def previous(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Goes back to the previous track in the history."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    # 'previous' raises HistoryEmpty when there is no track to go back to.
    try:
        track = await vc.previous()
    except sonolink.HistoryEmpty:
        await inter.response.send_message("No previous track in history!")
        return

    await inter.response.send_message(
        f"Going back to `{track.title}` by `{track.author}`!"
    )


@bot.slash_command(name="seek", description="Seeks to a position (seconds).")
async def seek(
    inter: disnake.ApplicationCommandInteraction[Bot],
    seconds: int = commands.Param(  # pyright: ignore[reportUnknownMemberType]
        description="The position in seconds to jump to.",
    ),
) -> None:
    """Seeks to a position in the current track (in seconds).

    Example: /seek 90  →  jumps to the 1:30 mark.
    """
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    if not vc.current:
        await inter.response.send_message("Nothing is playing!")
        return

    await vc.seek(seconds * 1000)
    await inter.response.send_message(f"Sought to {seconds}s!")


@bot.slash_command(name="stop", description="Stops playback and disconnects.")
async def stop(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Stop playback, clear the queue, and disconnect the bot."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Already disconnected!")
        return

    await vc.disconnect()
    await inter.response.send_message("Disconnected and cleared the queue!")


# --------------
# Queue commands
# --------------


# All queue management commands live under a single '/queue' group,
# e.g. '/queue show', '/queue shuffle', '/queue sort'.
@bot.slash_command(name="queue", description="Queue management commands.")
async def queue_group(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    # This parent command is never invoked directly; only its sub-commands are.
    pass


@queue_group.sub_command(name="show", description="Display the current queue.")
async def queue_show(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Display the current queue (up to 10 upcoming tracks)."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    tracks = vc.queue.tracks
    autoplay_tracks = vc.queue.autoplay_tracks

    if not tracks and not autoplay_tracks and not vc.current:
        await inter.response.send_message("The queue is empty!")
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

    await inter.response.send_message("\n".join(lines))


@queue_group.sub_command(name="shuffle", description="Shuffles the current queue.")
async def queue_shuffle(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Shuffles the current queue in place."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    if not vc.queue.tracks:
        await inter.response.send_message("The queue is empty!")
        return

    vc.queue.shuffle()
    await inter.response.send_message("Queue shuffled!")


@queue_group.sub_command(
    name="shuffle-mode", description="Toggle persistent shuffle mode."
)
async def queue_shuffle_mode(
    inter: disnake.ApplicationCommandInteraction[Bot],
    mode: str = commands.Param(  # pyright: ignore[reportUnknownMemberType]
        description="Choose from: on, off",
        default="on",
        choices=["on", "off"],
    ),
) -> None:
    """Toggle persistent shuffle mode."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    mapping = {
        "on": ShuffleMode.PERSISTENT,
        "off": ShuffleMode.DEFAULT,
    }

    vc.queue.shuffle_mode = mapping[mode]
    await inter.response.send_message(f"Persistent shuffle mode turned `{mode}`!")


@queue_group.sub_command(name="reverse", description="Reverses the current queue.")
async def queue_reverse(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Reverses the current queue in place."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    if not vc.queue.tracks:
        await inter.response.send_message("The queue is empty!")
        return

    vc.queue.reverse()
    await inter.response.send_message("Queue reversed!")


@queue_group.sub_command(name="sort", description="Sorts the queue.")
async def queue_sort(
    inter: disnake.ApplicationCommandInteraction[Bot],
    by: str = commands.Param(  # pyright: ignore[reportUnknownMemberType]
        description="What to sort the queue by.",
        default="title",
        choices=["title", "author", "length"],
    ),
    descending: bool = commands.Param(  # pyright: ignore[reportUnknownMemberType]
        description="Whether to sort in descending order.",
        default=False,
    ),
) -> None:
    """Sorts the queue in place by title, author, or track length."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    if not vc.queue.tracks:
        await inter.response.send_message("The queue is empty!")
        return

    # 'sort' requires a key function that returns the value to sort by.
    keys = {
        "title": lambda t: t.title.lower(),
        "author": lambda t: t.author.lower(),
        "length": lambda t: t.length,
    }
    vc.queue.sort(key=keys[by], reverse=descending)
    await inter.response.send_message(f"Queue sorted by `{by}`!")


@queue_group.sub_command(
    name="dedupe", description="Removes duplicate tracks from the queue."
)
async def queue_dedupe(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Remove duplicate tracks from the queue, keeping the first occurrence."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    if not vc.queue.tracks:
        await inter.response.send_message("The queue is empty!")
        return

    # By default duplicates are detected by track identifier; pass your own
    # 'key' (e.g. key=lambda t: t.title) to change that.
    removed = vc.queue.dedupe()
    if removed:
        await inter.response.send_message(
            f"Removed {removed} duplicate track(s) from the queue!"
        )
    else:
        await inter.response.send_message("No duplicates found!")


@queue_group.sub_command(name="loop", description="Set the loop mode.")
async def queue_loop(
    inter: disnake.ApplicationCommandInteraction[Bot],
    mode: str = commands.Param(  # pyright: ignore[reportUnknownMemberType]
        description="Choose from: track, all, off",
        default="track",
        choices=["track", "all", "off"],
    ),
) -> None:
    """Set the loop mode. Options: 'track', 'all', 'off'.

    - track: repeats the current track indefinitely.
    - all:   loops the entire queue once it finishes.
    - off:   disables looping.
    """
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    mapping = {
        "track": QueueMode.LOOP,
        "all": QueueMode.LOOP_ALL,
        "off": QueueMode.NORMAL,
    }

    vc.queue.mode = mapping[mode]
    await inter.response.send_message(f"Loop mode set to `{mode}`!")


# ---------------
# Player settings
# ---------------


@bot.slash_command(name="volume", description="Set the player volume (0–1000).")
async def volume(
    inter: disnake.ApplicationCommandInteraction[Bot],
    value: int = commands.Param(  # pyright: ignore[reportUnknownMemberType]
        description="Volume level between 0 and 1000.",
        ge=0,
        le=1000,
    ),
) -> None:
    """Set the player volume (0–1000). Default is 100."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    # commands.Param with ge/le ensures the value stays between 0 and 1000 in the UI
    await vc.set_volume(value)
    await inter.response.send_message(f"Volume set to `{value}`!")


@bot.slash_command(name="nowplaying", description="Shows current track info.")
async def nowplaying(inter: disnake.ApplicationCommandInteraction[Bot]) -> None:
    """Show information about the currently playing track."""
    vc = _player_check(inter)
    if not vc:
        await inter.response.send_message("Not connected to a voice channel!")
        return

    track = vc.current
    if not track:
        await inter.response.send_message("Nothing is playing right now!")
        return

    # Convert milliseconds to a readable mm:ss position / duration.
    def fmt(ms: int) -> str:
        s = ms // 1000
        return f"{s // 60}:{s % 60:02d}"

    await inter.response.send_message(
        f"**Now playing:** `{track.title}` by `{track.author}`\n"
        f"**Position:** `{fmt(vc.position)}` / `{fmt(track.length)}`\n"
        f"**Volume:** `{vc.volume}` | **Loop:** `{vc.queue.mode.name.lower()}`"
    )


if __name__ == "__main__":
    bot.run("TOKEN")

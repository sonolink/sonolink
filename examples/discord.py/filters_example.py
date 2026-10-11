"""
This example requires the discord.py[voice] (https://pypi.org/project/discord.py/) library to be installed.

This example covers the procedure of handling filters with sonolink, allowing you to apply audio filters to your players.
It demonstrates full usage of every filter type: Equalizer, Timescale, Karaoke,
Tremolo, Vibrato, Rotation, Distortion, ChannelMix, and LowPass.
https://sonolink.readthedocs.io/en/latest/guides/filters.html

This requires an active Lavalink server, for more information on setting up one
you can check the guide at: https://sonolink.readthedocs.io/en/latest/guides/lavalink-setup.html

:copyright: (c) 2026-present SonoLink Development Team
"""

from enum import StrEnum
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

import sonolink
from sonolink.models import filters


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


class Filter(StrEnum):
    # Equalizer presets
    BASS = "bass"
    BASSBOOST = "bassboost"
    BASSBOOSTHIGH = "bassboosthigh"
    CLASSICAL = "classical"
    ELECTRONIC = "electronic"
    ERRAPE = "errape"
    GAMING = "gaming"
    HIGHFULL = "highfull"
    HIGHVOICE = "highvoice"
    PARTY = "party"
    POP = "pop"
    RADIO = "radio"
    ROCK = "rock"
    TREBLEBASS = "treblebass"

    # Timescale presets
    DARTHVADOR = "darthvador"
    NIGHTCORE = "nightcore"
    LOVENIGHTCORE = "lovenightcore"
    SUPERFAST = "superfast"
    VAPOREWAVE = "vaporewave"

    # Single-filter presets
    EIGHTD = "eightd"  # Rotation
    KARAOKE = "karaoke"
    SOFT = "soft"  # LowPass
    TREMOLO = "tremolo"
    VIBRATO = "vibrato"


FILTERS: dict[Filter, filters.Filters] = {
    # ----------------------------------------------------------
    # Equalizer presets: specific frequency bands (0–14).
    # Gain range: -0.25 (cut) to 1.0 (boost).
    # ----------------------------------------------------------
    Filter.BASS: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.6),
            filters.Equalizer(band=1, gain=0.7),
            filters.Equalizer(band=2, gain=0.8),
            filters.Equalizer(band=3, gain=0.55),
            filters.Equalizer(band=4, gain=0.25),
            filters.Equalizer(band=5, gain=0),
            filters.Equalizer(band=6, gain=-0.25),
            filters.Equalizer(band=7, gain=-0.45),
            filters.Equalizer(band=8, gain=-0.55),
            filters.Equalizer(band=9, gain=-0.7),
            filters.Equalizer(band=10, gain=-0.3),
            filters.Equalizer(band=11, gain=-0.25),
            filters.Equalizer(band=12, gain=0),
            filters.Equalizer(band=13, gain=0),
            filters.Equalizer(band=14, gain=0),
        ],
    ),
    Filter.BASSBOOST: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.6),
            filters.Equalizer(band=1, gain=0.67),
            filters.Equalizer(band=2, gain=0.67),
            filters.Equalizer(band=3, gain=0),
            filters.Equalizer(band=4, gain=-0.5),
            filters.Equalizer(band=5, gain=0.15),
            filters.Equalizer(band=6, gain=-0.45),
            filters.Equalizer(band=7, gain=0.23),
            filters.Equalizer(band=8, gain=0.35),
            filters.Equalizer(band=9, gain=0.45),
            filters.Equalizer(band=10, gain=0.55),
            filters.Equalizer(band=11, gain=0.6),
            filters.Equalizer(band=12, gain=0.55),
            filters.Equalizer(band=13, gain=0),
        ],
    ),
    Filter.BASSBOOSTHIGH: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.1875),
            filters.Equalizer(band=1, gain=0.375),
            filters.Equalizer(band=2, gain=-0.375),
            filters.Equalizer(band=3, gain=-0.1875),
            filters.Equalizer(band=4, gain=0),
            filters.Equalizer(band=5, gain=-0.0125),
            filters.Equalizer(band=6, gain=-0.025),
            filters.Equalizer(band=7, gain=-0.0175),
            filters.Equalizer(band=8, gain=0),
            filters.Equalizer(band=9, gain=0),
            filters.Equalizer(band=10, gain=0.0125),
            filters.Equalizer(band=11, gain=0.025),
            filters.Equalizer(band=12, gain=0.375),
            filters.Equalizer(band=13, gain=0.125),
            filters.Equalizer(band=14, gain=0.125),
        ],
    ),
    Filter.CLASSICAL: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.375),
            filters.Equalizer(band=1, gain=0.350),
            filters.Equalizer(band=2, gain=0.125),
            filters.Equalizer(band=3, gain=0),
            filters.Equalizer(band=4, gain=0),
            filters.Equalizer(band=5, gain=0.125),
            filters.Equalizer(band=6, gain=0.550),
            filters.Equalizer(band=7, gain=0.050),
            filters.Equalizer(band=8, gain=0.125),
            filters.Equalizer(band=9, gain=0.250),
            filters.Equalizer(band=10, gain=0.200),
            filters.Equalizer(band=11, gain=0.250),
            filters.Equalizer(band=12, gain=0.300),
            filters.Equalizer(band=13, gain=0.250),
            filters.Equalizer(band=14, gain=0.300),
        ],
    ),
    Filter.ELECTRONIC: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.375),
            filters.Equalizer(band=1, gain=0.350),
            filters.Equalizer(band=2, gain=0.125),
            filters.Equalizer(band=3, gain=0),
            filters.Equalizer(band=4, gain=0),
            filters.Equalizer(band=5, gain=-0.125),
            filters.Equalizer(band=6, gain=-0.125),
            filters.Equalizer(band=7, gain=0),
            filters.Equalizer(band=8, gain=0.25),
            filters.Equalizer(band=9, gain=0.125),
            filters.Equalizer(band=10, gain=0.15),
            filters.Equalizer(band=11, gain=0.2),
            filters.Equalizer(band=12, gain=0.250),
            filters.Equalizer(band=13, gain=0.350),
            filters.Equalizer(band=14, gain=0.400),
        ],
    ),
    Filter.ERRAPE: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.25),
            filters.Equalizer(band=1, gain=0.5),
            filters.Equalizer(band=2, gain=-0.5),
            filters.Equalizer(band=3, gain=-0.25),
            filters.Equalizer(band=4, gain=0),
            filters.Equalizer(band=6, gain=-0.025),
            filters.Equalizer(band=7, gain=-0.0175),
            filters.Equalizer(band=8, gain=0),
            filters.Equalizer(band=9, gain=0),
            filters.Equalizer(band=10, gain=0.0125),
            filters.Equalizer(band=11, gain=0.025),
            filters.Equalizer(band=12, gain=0.375),
            filters.Equalizer(band=13, gain=0.125),
            filters.Equalizer(band=14, gain=0.125),
        ],
    ),
    Filter.GAMING: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.350),
            filters.Equalizer(band=1, gain=0.300),
            filters.Equalizer(band=2, gain=0.250),
            filters.Equalizer(band=3, gain=0.200),
            filters.Equalizer(band=4, gain=0.150),
            filters.Equalizer(band=5, gain=0.100),
            filters.Equalizer(band=6, gain=0.050),
            filters.Equalizer(band=7, gain=-0.0),
            filters.Equalizer(band=8, gain=-0.050),
            filters.Equalizer(band=9, gain=-0.100),
            filters.Equalizer(band=10, gain=-0.150),
            filters.Equalizer(band=11, gain=-0.200),
            filters.Equalizer(band=12, gain=-0.250),
            filters.Equalizer(band=13, gain=-0.300),
            filters.Equalizer(band=14, gain=-0.350),
        ],
    ),
    Filter.HIGHFULL: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.25 + 0.375),
            filters.Equalizer(band=1, gain=0.25 + 0.025),
            filters.Equalizer(band=2, gain=0.25 + 0.0125),
            filters.Equalizer(band=3, gain=0.25),
            filters.Equalizer(band=4, gain=0.25),
            filters.Equalizer(band=5, gain=0.25 + -0.0125),
            filters.Equalizer(band=6, gain=0.25 + -0.025),
            filters.Equalizer(band=7, gain=0.25 + 0.0175),
            filters.Equalizer(band=8, gain=0.25),
            filters.Equalizer(band=9, gain=0.25),
            filters.Equalizer(band=10, gain=0.25 + 0.0125),
            filters.Equalizer(band=11, gain=0.25 + 0.025),
            filters.Equalizer(band=12, gain=0.25 + 0.375),
            filters.Equalizer(band=13, gain=0.25 + 0.125),
            filters.Equalizer(band=14, gain=0.25 + 0.125),
        ],
    ),
    Filter.HIGHVOICE: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=-2.0),
            filters.Equalizer(band=1, gain=-2.0),
            filters.Equalizer(band=2, gain=-5.0),
            filters.Equalizer(band=3, gain=4),
            filters.Equalizer(band=4, gain=3),
            filters.Equalizer(band=5, gain=1),
            filters.Equalizer(band=6, gain=0.1),
            filters.Equalizer(band=7, gain=2.2),
            filters.Equalizer(band=8, gain=0.5),
        ],
    ),
    Filter.PARTY: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=-1.16),
            filters.Equalizer(band=1, gain=0.28),
            filters.Equalizer(band=2, gain=0.42),
            filters.Equalizer(band=3, gain=0.5),
            filters.Equalizer(band=4, gain=0.36),
            filters.Equalizer(band=5, gain=0),
            filters.Equalizer(band=6, gain=-0.3),
            filters.Equalizer(band=7, gain=-0.21),
            filters.Equalizer(band=8, gain=-0.21),
        ],
    ),
    Filter.POP: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=-0.25),
            filters.Equalizer(band=1, gain=0.48),
            filters.Equalizer(band=2, gain=0.59),
            filters.Equalizer(band=3, gain=0.72),
            filters.Equalizer(band=4, gain=0.56),
            filters.Equalizer(band=5, gain=0.15),
            filters.Equalizer(band=6, gain=-0.24),
            filters.Equalizer(band=7, gain=-0.24),
            filters.Equalizer(band=8, gain=-0.16),
            filters.Equalizer(band=9, gain=-0.16),
            filters.Equalizer(band=10, gain=0),
            filters.Equalizer(band=11, gain=0),
            filters.Equalizer(band=12, gain=0),
            filters.Equalizer(band=13, gain=0),
            filters.Equalizer(band=14, gain=0),
        ],
    ),
    Filter.RADIO: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.65),
            filters.Equalizer(band=1, gain=0.45),
            filters.Equalizer(band=2, gain=-0.45),
            filters.Equalizer(band=3, gain=-0.65),
            filters.Equalizer(band=4, gain=-0.35),
            filters.Equalizer(band=5, gain=0.45),
            filters.Equalizer(band=6, gain=0.55),
            filters.Equalizer(band=7, gain=0.6),
            filters.Equalizer(band=8, gain=0.6),
            filters.Equalizer(band=9, gain=0.6),
            filters.Equalizer(band=10, gain=0),
            filters.Equalizer(band=11, gain=0),
            filters.Equalizer(band=12, gain=0),
            filters.Equalizer(band=13, gain=0),
            filters.Equalizer(band=14, gain=0),
        ],
    ),
    Filter.ROCK: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.300),
            filters.Equalizer(band=1, gain=0.250),
            filters.Equalizer(band=2, gain=0.200),
            filters.Equalizer(band=3, gain=0.100),
            filters.Equalizer(band=4, gain=0.050),
            filters.Equalizer(band=5, gain=-0.050),
            filters.Equalizer(band=6, gain=-0.150),
            filters.Equalizer(band=7, gain=-0.200),
            filters.Equalizer(band=8, gain=-0.100),
            filters.Equalizer(band=9, gain=-0.050),
            filters.Equalizer(band=10, gain=0.050),
            filters.Equalizer(band=11, gain=0.100),
            filters.Equalizer(band=12, gain=0.200),
            filters.Equalizer(band=13, gain=0.250),
            filters.Equalizer(band=14, gain=0.300),
        ],
    ),
    Filter.TREBLEBASS: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.6),
            filters.Equalizer(band=1, gain=0.67),
            filters.Equalizer(band=2, gain=0.67),
            filters.Equalizer(band=3, gain=0),
            filters.Equalizer(band=4, gain=-0.5),
            filters.Equalizer(band=5, gain=0.15),
            filters.Equalizer(band=6, gain=-0.45),
            filters.Equalizer(band=7, gain=0.23),
            filters.Equalizer(band=8, gain=0.35),
            filters.Equalizer(band=9, gain=0.45),
            filters.Equalizer(band=10, gain=0.55),
            filters.Equalizer(band=11, gain=0.6),
            filters.Equalizer(band=12, gain=0.55),
            filters.Equalizer(band=13, gain=0),
        ],
    ),
    # -----------------------------------------------------------
    # Timescale: speed, pitch, and/or rate independently.
    # All three values must be >= 0.0.
    # -----------------------------------------------------------
    Filter.DARTHVADOR: filters.Filters(
        timescale=filters.Timescale(speed=0.975, pitch=0.5, rate=0.8),
    ),
    Filter.NIGHTCORE: filters.Filters(
        timescale=filters.Timescale(speed=1.3, pitch=1.3, rate=1.0),
    ),
    Filter.LOVENIGHTCORE: filters.Filters(
        timescale=filters.Timescale(speed=1.1, pitch=1.2, rate=1.0),
    ),
    Filter.SUPERFAST: filters.Filters(
        timescale=filters.Timescale(speed=1.5010, pitch=1.2450, rate=1.9210),
    ),
    # Vaporwave combines an equalizer boost, a halved pitch, and a tremolo wobble.
    # This shows how multiple filter types can be composed into a single Filters payload.
    Filter.VAPOREWAVE: filters.Filters(
        equalizer=[
            filters.Equalizer(band=0, gain=0.3),
            filters.Equalizer(band=1, gain=0.3),
        ],
        timescale=filters.Timescale(pitch=0.5),
        tremolo=filters.Tremolo(depth=0.3, frequency=14),
    ),
    # ------------------------------------------------------------------
    # Rotation: pans audio between stereo channels at the given Hz rate,
    # creating the 8D audio effect.
    # ------------------------------------------------------------------
    Filter.EIGHTD: filters.Filters(
        rotation=filters.Rotation(rotation_hz=0.2),
    ),
    # --------------------------------------------------------------------
    # Karaoke: attenuates the vocal range around a center frequency.
    # level / mono_level: 0.0 (off) -> 1.0 (full effect).
    # filter_band: center frequency in Hz (220 Hz targets typical vocals).
    # filter_width: bandwidth in Hz around the center to suppress.
    # --------------------------------------------------------------------
    Filter.KARAOKE: filters.Filters(
        karaoke=filters.Karaoke(
            level=1.0,
            mono_level=1.0,
            filter_band=220.0,
            filter_width=100.0,
        ),
    ),
    # ------------------------------------------------------------------
    # LowPass: suppresses frequencies above the cutoff by smoothing the
    # signal. Higher smoothing = more high-end roll-off.
    # smoothing must be > 1.0.
    # ------------------------------------------------------------------
    Filter.SOFT: filters.Filters(
        low_pass=filters.LowPass(smoothing=20.0),
    ),
    # --------------------------------------------------
    # Tremolo: oscillates volume at the given frequency.
    # frequency: Hz, must be > 0.0.
    # depth: intensity, 0.0 < x <= 1.0.
    # --------------------------------------------------
    Filter.TREMOLO: filters.Filters(
        tremolo=filters.Tremolo(frequency=10, depth=0.5),
    ),
    # -------------------------------------------------
    # Vibrato: oscillates pitch at the given frequency.
    # frequency: Hz, 0.0 < x <= 14.0.
    # depth: intensity, 0.0 < x <= 1.0.
    # -------------------------------------------------
    Filter.VIBRATO: filters.Filters(
        vibrato=filters.Vibrato(frequency=10, depth=0.9),
    ),
}


def _get_player(interaction: discord.Interaction) -> sonolink.Player | None:
    vc = interaction.guild.voice_client if interaction.guild else None
    return vc if isinstance(vc, sonolink.Player) else None


async def filter_autocomplete(
    _: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=f.value, value=f.value)
        for f in Filter
        if current.lower() in f.value.lower()
    ][:25]


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


@bot.tree.command(
    name="apply-filter",
    description="Applies a filter preset to the current player.",
)
@app_commands.describe(
    filter="The filter preset to apply.",
    reset="Clear all existing filters before applying. Defaults to False (stacks on top).",
)
@app_commands.autocomplete(filter=filter_autocomplete)
async def apply_filter(
    interaction: discord.Interaction,
    filter: str,
    reset: bool = False,
) -> None:
    # Filters can be applied at any time while a track is playing and take effect immediately.
    # By default, the new preset is stacked on top of existing filters via Filters.combine(),
    # which returns a new Filters instance without mutating either input.
    # Passing reset=True replaces all active filters with only the chosen preset instead.
    await interaction.response.defer()

    vc = _get_player(interaction)
    if not vc or not vc.current:
        await interaction.followup.send("Nothing is currently playing!")
        return

    try:
        preset = Filter(filter)
    except ValueError:
        await interaction.followup.send(f"`{filter}` is not a valid filter preset.")
        return

    new_filters = (
        FILTERS[preset]
        if reset
        else (vc.filters or filters.Filters()).combine(FILTERS[preset])
    )
    await vc.set_filters(new_filters)
    await interaction.followup.send(
        f"{'Reset filters and applied' if reset else 'Applied'} `{preset.value}`!"
    )


@bot.tree.command(
    name="remove-filter",
    description="Removes a single active filter type.",
)
@app_commands.describe(filter="The filter preset whose filter types should be removed.")
@app_commands.autocomplete(filter=filter_autocomplete)
async def remove_filter(
    interaction: discord.Interaction,
    filter: str,
) -> None:
    # Rather than tracking which presets are active, we look at which filter types
    # the chosen preset uses and null those out on the current player state.
    # For example, removing 'nightcore' clears only the Timescale filter, leaving
    # any equalizer or rotation filters that may be active completely untouched.
    await interaction.response.defer()

    vc = _get_player(interaction)
    if not vc or not vc.current:
        await interaction.followup.send("Nothing is currently playing!")
        return

    try:
        preset = Filter(filter)
    except ValueError:
        await interaction.followup.send(f"`{filter}` is not a valid filter preset.")
        return

    current = vc.filters or filters.Filters()
    preset_filter = FILTERS[preset]
    attrs = (
        "timescale",
        "karaoke",
        "tremolo",
        "vibrato",
        "rotation",
        "distortion",
        "channel_mix",
        "low_pass",
    )

    for attr in attrs:
        if getattr(preset_filter, attr):
            setattr(current, attr, None)

    if preset_filter.equalizer:
        current.equalizer = []

    await vc.set_filters(current)
    await interaction.followup.send(f"Removed `{preset.value}` filter!")


@bot.tree.command(
    name="reset-filters", description="Clears all active filters from the player."
)
async def reset_filters(interaction: discord.Interaction) -> None:
    # Applying an empty Filters() instance tells Lavalink to remove all active filters.
    vc = _get_player(interaction)
    if not vc or not vc.current:
        await interaction.response.send_message("Nothing is currently playing!")
        return

    await vc.set_filters(filters.Filters())
    await interaction.response.send_message("All filters cleared!")


if __name__ == "__main__":
    bot.run("TOKEN")

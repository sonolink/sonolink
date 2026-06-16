.. currentmodule:: sonolink

Getting Started
===============

This guide shows the normal setup flow for a new SonoLink bot. It is not a migration guide:
it assumes you are starting from a Discord bot and want to connect it to Lavalink for the
first time.

The short version is:

1. Install SonoLink and one supported Discord library.
2. Run a Lavalink 4 server.
3. Create a :class:`sonolink.Client`.
4. Register at least one Lavalink node.
5. Start the SonoLink client.
6. Connect voice channels with :class:`sonolink.Player`.

Before you begin
----------------

SonoLink does not play audio by itself. It connects your bot to a separate Lavalink server,
and Lavalink performs the audio loading, decoding, and streaming work.

You need:

* Python 3.12 or newer.
* One supported Discord library: py-cord, discord.py, disnake, or nextcord.
* SonoLink installed with ``pip install sonolink``.
* A running Lavalink 4 server.

If you have not installed SonoLink yet, read :doc:`/installation`.
If you do not have Lavalink running yet, read :doc:`/guides/lavalink-setup`.

The three main objects
----------------------

Most SonoLink bots use these objects:

* :class:`sonolink.Client` belongs to your Discord client and owns the Lavalink connections.
* :class:`sonolink.Node` represents one Lavalink server.
* :class:`sonolink.Player` is the voice connection used in a Discord guild.

You normally create one :class:`sonolink.Client` when your bot starts, register one or more
nodes with :meth:`sonolink.Client.create_node`, then connect voice channels with
:class:`sonolink.Player` inside commands.

Connection lifecycle
--------------------

SonoLink uses the same general shape as most Lavalink wrappers: a long-lived client owns
your Lavalink nodes, and each Discord guild gets a player when the bot joins voice.

The important part is the order:

1. Create the Discord bot.
2. Create :class:`sonolink.Client` and attach it to the bot.
3. Register nodes with :meth:`sonolink.Client.create_node`.
4. Start the SonoLink client once the Discord client is ready.
5. Connect voice channels with :class:`sonolink.Player`.

For most bots, you do not need to manually choose a node when connecting a player. SonoLink
will use the client attached to your bot and select a connected node for you.

Creating the SonoLink client
----------------------------

Create the SonoLink client after creating your Discord bot. The client should live for as long
as your bot process lives.

This example uses Pycord, so the flow may differ for discord.py, Disnake, and
Nextcord (see more about that below).

.. code-block:: python

   from typing import Any

   import discord

   import sonolink

    class Bot(discord.Bot):
        def __init__(self) -> None:
            intents = discord.Intents(guilds=True, voice_states=True)
            super().__init__(intents=intents)

            # The SonoLink client owns your Lavalink nodes and is attached to this bot.
            self.sl_client: sonolink.Client[Any] = sonolink.Client(self)

        async def on_connect(self) -> None:
            await super().on_connect()

            # Start opens the registered Lavalink node connections.
            await self.sl_client.start()

   bot = Bot()

Registering a node
------------------

A node is SonoLink's connection information for a Lavalink server. You should register your
node before calling :meth:`sonolink.Client.start`.

.. code-block:: python

   bot.sl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       id="main",
   )

``uri`` is the address of your Lavalink server. For local development this is usually
``http://localhost:2333``.

If you prefer keeping the host and port separate, you may pass ``host`` and ``port`` instead
of ``uri``. This is available since SonoLink 1.1.0:

.. code-block:: python

   bot.sl_client.create_node(
       host="localhost",
       port=2333,
       password="youshallnotpass",
       id="main",
   )

``uri`` and ``host``/``port`` are mutually exclusive. Use whichever style fits your
configuration best.

``password`` must match the ``lavalink.server.password`` value in your Lavalink
``application.yml``.

``id`` is optional, but naming nodes is useful once you have more than one.

Calling :meth:`sonolink.Client.create_node` registers the node. Calling
:meth:`sonolink.Client.start` opens the connection to Lavalink. If you skip this step,
:class:`sonolink.Player` will not have a node to use.

Region-aware nodes
~~~~~~~~~~~~~~~~~~

Nodes do not need a region. If you omit ``regions``, SonoLink treats the node as a normal
candidate and selects by penalty:

.. code-block:: python

   bot.sl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       id="default",
   )

If you run multiple Lavalink nodes in different regions, assign each regional node the
Discord voice regions it should serve. SonoLink will prefer a node whose ``regions`` include
the connected voice channel's ``rtc_region``, then fall back to normal penalty-based selection
across all connected nodes if the channel uses automatic region detection or no matching node
is connected.

.. code-block:: python

   bot.sl_client.create_node(
       uri="http://us-east.example.com:2333",
       password="youshallnotpass",
       id="us-east",
       regions=[sonolink.NodeRegion.US_EAST, sonolink.NodeRegion.US_CENTRAL],
   )

   bot.sl_client.create_node(
       uri="http://rotterdam.example.com:2333",
       password="youshallnotpass",
       id="rotterdam",
       regions=[sonolink.NodeRegion.ROTTERDAM],
   )

   # Nodes without regions can still act as general fallback capacity.
   bot.sl_client.create_node(
       uri="http://fallback.example.com:2333",
       password="youshallnotpass",
       id="fallback",
   )

Automatic player selection uses the channel's ``rtc_region`` with the supported adapters for
discord.py, py-cord, disnake, and nextcord. You can also pass a raw Discord region string in
``regions`` if :class:`NodeRegion` does not include a newer Discord region yet.

For REST-style operations that happen before a player exists, pass ``region=`` yourself:

.. code-block:: python

   result = await bot.sl_client.search_track(
       "lofi beats",
       region=sonolink.NodeRegion.US_EAST,
   )

.. note::
   :meth:`sonolink.Client.start` should be called once your Discord client is ready,
   typically in :func:`pycord:discord.on_connect` (py-cord),
   :meth:`discord:discord.Client.setup_hook` (discord.py), :func:`disnake:disnake.on_connect`
   (disnake), or :func:`nextcord:nextcord.on_connect` (nextcord) rather than in
   ``on_ready``.

Connecting a player
-------------------

When a command needs audio, connect to the user's voice channel with :class:`sonolink.Player`.
The player will use the SonoLink client attached to your bot and choose a connected node.

.. code-block:: python

   @bot.slash_command(name="join", description="Connects the bot to your voice channel.")
   async def join(ctx: discord.ApplicationContext) -> None:
       if not isinstance(ctx.author, discord.Member):
           await ctx.respond("This command can only be used in a server.")
           return

       if not ctx.author.voice or not ctx.author.voice.channel:
           await ctx.respond("You must be in a voice channel.")
           return

       player = await ctx.author.voice.channel.connect(cls=sonolink.Player)
       assert isinstance(player, sonolink.Player)

       await ctx.respond("Connected.")

Searching and playing
---------------------

Use :meth:`sonolink.Client.search_track` to ask Lavalink for a track, then play it with the
guild's :class:`sonolink.Player`.

.. code-block:: python

   @bot.slash_command(name="play", description="Plays a song.")
   @discord.option("query", description="A search query or URL.")
   async def play(ctx: discord.ApplicationContext, query: str) -> None:
       await ctx.defer()

       if not isinstance(ctx.author, discord.Member):
           await ctx.respond("This command can only be used in a server.")
           return

       player = ctx.guild.voice_client if ctx.guild else None

       if player is None:
           if not ctx.author.voice or not ctx.author.voice.channel:
               await ctx.respond("You must be in a voice channel.")
               return

           player = await ctx.author.voice.channel.connect(cls=sonolink.Player)

       if not isinstance(player, sonolink.Player):
           await ctx.respond("The bot is already connected with another voice client.")
           return

       # Ask Lavalink to resolve the user's query through the SonoLink client.
       result = await bot.sl_client.search_track(query)

       if result.is_error() or result.is_empty() or result.result is None:
           await ctx.respond("No tracks found.")
           return

       # Search results can be a list of tracks, a playlist, or a single track.
       data = result.result

       if isinstance(data, list):
           track = data[0]
       elif isinstance(data, sonolink.models.Playlist):
           track = data.tracks[0]
       else:
           track = data

       # Queue the selected track on the guild's SonoLink player.
       player.queue.put(track)

       if not player.current:
           # If nothing is playing yet, pull the first queued track and start it.
           track = player.queue.get()
           await player.play(track)
           await ctx.respond(f"Now playing `{track.title}`.")
       else:
           await ctx.respond(f"Queued `{track.title}`.")

Repository examples
-------------------

The ``examples/`` directory in the GitHub repository contains complete bots for each
supported Discord library. These are useful when you want a working file to copy from instead
of building each command from the guide snippets.

The repository currently includes examples for:

* `py-cord <https://github.com/sonolink/sonolink/tree/main/examples/py-cord>`_
* `discord.py <https://github.com/sonolink/sonolink/tree/main/examples/discord.py>`_
* `disnake <https://github.com/sonolink/sonolink/tree/main/examples/disnake>`_
* `nextcord <https://github.com/sonolink/sonolink/tree/main/examples/nextcord>`_

Each framework folder includes a simple playback example, plus examples for settings,
filters, events, and more advanced usage.

Moving from another library
---------------------------

If you are moving from another Lavalink wrapper, start with the migration guide for that
library. Those pages map the old concepts to SonoLink's client, node, player, queue, search,
filter, and event APIs.

* :doc:`/guides/migrations/wavelink`
* :doc:`/guides/migrations/pomice`
* :doc:`/guides/migrations/mafic`
* :doc:`/guides/migrations/lavalink.py`
* :doc:`/guides/migrations/lavaplay.py`

Full minimal bot
----------------

Putting the pieces together:

.. code-block:: python

   from typing import Any

   import discord

   import sonolink
   import sonolink.models


   class Bot(discord.Bot):
       def __init__(self) -> None:
           intents = discord.Intents(guilds=True, voice_states=True)
           super().__init__(intents=intents)

           self.sl_client: sonolink.Client[Any] = sonolink.Client(self)

       async def on_connect(self) -> None:
           await super().on_connect()
           await self.sl_client.start()


   bot = Bot()

   bot.sl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       id="main",
   )


   @bot.slash_command(name="play", description="Plays a song.")
   @discord.option("query", description="A search query or URL.")
   async def play(ctx: discord.ApplicationContext, query: str) -> None:
       await ctx.defer()

       if not isinstance(ctx.author, discord.Member):
           await ctx.respond("This command can only be used in a server.")
           return

       player = ctx.guild.voice_client if ctx.guild else None

       if player is None:
           if not ctx.author.voice or not ctx.author.voice.channel:
               await ctx.respond("You must be in a voice channel.")
               return

           player = await ctx.author.voice.channel.connect(cls=sonolink.Player)

       if not isinstance(player, sonolink.Player):
           await ctx.respond("The bot is already connected with another voice client.")
           return

       result = await bot.sl_client.search_track(query)

       if result.is_error() or result.is_empty() or result.result is None:
           await ctx.respond("No tracks found.")
           return

       data = result.result

       if isinstance(data, list):
           track = data[0]
       elif isinstance(data, sonolink.models.Playlist):
           track = data.tracks[0]
       else:
           track = data

       player.queue.put(track)

       if not player.current:
           track = player.queue.get()
           await player.play(track)
           await ctx.respond(f"Now playing `{track.title}`.")
       else:
           await ctx.respond(f"Queued `{track.title}`.")


   bot.run("TOKEN")

Where to go next
----------------

After this guide:

* Read :doc:`/guides/players` for queue usage, skipping, pausing, filters, and clean disconnects.
* Read :doc:`/guides/lavalink-setup` if your node fails to connect or you need production setup.
* Read :doc:`/guides/filters` when you want to apply Lavalink audio filters.
* Read :doc:`/guides/migrations/index` if you are moving from another Lavalink wrapper.
* Check the `repository examples <https://github.com/sonolink/sonolink/tree/main/examples>`_
  for framework-specific complete bots.

Q&A / Troubleshooting
----------------------

Why does the bot join voice but not play anything?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Check that Lavalink is running and that the node ``uri`` or ``host``/``port`` values and
``password`` match your Lavalink configuration.

Why does connecting a player fail because no node is available?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make sure you called :meth:`sonolink.Client.create_node` before
:meth:`sonolink.Client.start`. Registering a node stores the Lavalink connection details;
starting the client opens the actual connection.

Why do track searches always return empty results?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Check your Lavalink source configuration. Source support depends on your Lavalink server and
installed plugins. For YouTube support, see the plugin notes in
:doc:`/guides/lavalink-setup`.

Check your Lavalink source configuration. Source support depends on your Lavalink server and
installed plugins. For YouTube support, see the plugin notes in
:doc:`/guides/lavalink-setup`.

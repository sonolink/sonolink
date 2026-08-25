.. currentmodule:: sonolink

Moving From Lavalink.py
=======================

This guide is for migrating from `Lavalink.py <https://github.com/Devoxin/Lavalink.py>`_ to SonoLink.

It walks through the main differences between SonoLink and Lavalink.py, so you can get a feel
for what changes and what stays familiar.

If you are not migrating an existing Lavalink.py bot, start with :doc:`/guides/getting-started`
instead.

What stays familiar
-------------------

* Lavalink remains the backend.
* SonoLink supports discord.py, py-cord, disnake, and nextcord — the same libraries
  Lavalink.py is most commonly paired with.
* The main runtime objects are still a client, nodes, players, tracks, and filters.

What changes
------------

Lavalink.py centres its API on a manually managed ``Client`` that owns a ``NodeManager`` and
a ``PlayerManager``, and exposes a lower-level ``DefaultPlayer`` with a basic list-based queue
that requires manual management. SonoLink replaces these with a higher-level coordinator, a structured
settings system, an automated queue, and automatic node selection and built-in autoplay/history.

Concept mapping
---------------

.. list-table::
   :header-rows: 1

   * - Lavalink.py
     - SonoLink
   * - ``lavalink.Client``
     - :class:`sonolink.Client`
   * - ``lavalink.Client.node_manager`` / ``NodeManager``
     - Managed internally; access via :meth:`sonolink.Client.get_node`
   * - ``lavalink.Client.player_manager`` / ``PlayerManager``
     - Not exposed; players are created via :meth:`sonolink.Node.create_player` or ``voice_channel.connect``
   * - ``lavalink.DefaultPlayer``
     - :class:`sonolink.Player`
   * - ``lavalink.BasePlayer``
     - :class:`sonolink.Player` (subclass if needed)
   * - ``lavalink.AudioTrack``
     - :class:`sonolink.models.Playable`
   * - ``lavalink.LoadResult``
     - :class:`sonolink.models.SearchResult`
   * - ``lavalink.LoadType``
     - Implicit in :class:`sonolink.models.SearchResult` result type
   * - ``lavalink.Filter``
     - :class:`sonolink.models.Filters` (and individual filter classes)
   * - ``lavalink.listener``
     - Discord client ``on_sonolink_*`` event handlers

Connection lifecycle
--------------------

SonoLink's coordinator is constructed with no manual
voice payload forwarding need, because it registers its own internal listeners:

.. code-block:: python

   # SonoLink
   import sonolink

   sl_client = sonolink.Client(bot)

   sl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       id="main",
   )

   async def setup_hook() -> None:
       await sl_client.start()

.. note::
   :meth:`sonolink.Client.start` should be called in :meth:`discord:discord.Client.setup_hook`
   (discord.py), :func:`pycord:discord.on_connect` (py-cord),
   :func:`disnake:disnake.on_connect` (disnake), or :func:`nextcord:nextcord.on_connect`
   (nextcord) — not in ``on_ready``.

Node management
---------------

In Lavalink.py, nodes are registered via ``Client.add_node`` and accessed through the
``NodeManager``. Region-based selection and penalty-based load balancing are handled
internally by ``NodeManager``, and you can target a specific node by name via
``NodeManager.find_ideal_node``.

SonoLink does not expose a ``NodeManager`` at all — node selection for new players is
automatic. If you need a specific node, retrieve it by ID:

.. code-block:: python

   node = sl_client.get_node("main")
   player = node.create_player(...)

For most bots the automatic selection is sufficient and you will not need to call this
directly.

Players and voice connection
----------------------------

Lavalink.py does not integrate with ``discord.VoiceProtocol``. Instead, you call
``PlayerManager.create_player`` yourself and then manually send voice state updates:

.. code-block:: python

   # Lavalink.py
   player = bot.lavalink.player_manager.create(
       guild_id=ctx.guild.id,
       endpoint=str(ctx.guild.region),
   )
   await ctx.author.voice.channel.guild.change_voice_state(
       channel=ctx.author.voice.channel,
   )

In SonoLink, players are created through the standard Discord ``VoiceProtocol`` interface:

.. code-block:: python

   # SonoLink
   player = await voice_channel.connect(cls=sonolink.Player)

If you need to pre-configure a player before connecting:

.. code-block:: python

   player = sonolink.Player(
       node=node,
       volume=100,
   )

   await voice_channel.connect(cls=player)

See :doc:`/guides/players` for the full player reference.

Searching and loading tracks
-----------------------------

In Lavalink.py, searching is done through ``Client.get_tracks`` (or the equivalent on the
node), which returns a ``LoadResult`` containing a ``LoadType`` and a list of
``AudioTrack`` objects:

.. code-block:: python

   # Lavalink.py
   result = await bot.lavalink.get_tracks(query)

   if not result or not result.tracks:
       return

   if result.load_type == lavalink.LoadType.PLAYLIST:
       track = result.tracks[0]
   else:
       track = result.tracks[0]

In SonoLink, searching returns a :class:`sonolink.models.SearchResult` wrapper that makes
the result type explicit without requiring you to branch on a ``LoadType`` enum:

.. code-block:: python

   # SonoLink
   result = await sl_client.search_track(query)
   if result.is_error() or result.is_empty() or result.result is None:
       return

   data = result.result

   if isinstance(data, list):
       track = data[0]
   elif isinstance(data, sonolink.models.Playlist):
       track = data.tracks[0]
   else:
       track = data

:class:`sonolink.models.SearchResult` covers all possible outcomes — a single track, a
playlist, a search result list, an empty result, or an error — so you no longer need to
check ``LoadType`` manually.

Tracks
------

Lavalink.py uses ``lavalink.AudioTrack`` for individual tracks. The SonoLink equivalent is
:class:`sonolink.models.Playable`. SonoLink tracks additionally carry
:class:`sonolink.models.Album` and :class:`sonolink.models.Artist` metadata when the source
provides it.

Playback
--------

:class:`sonolink.Player` exposes the same playback controls as Lavalink.py's
``DefaultPlayer``. The main difference is the queue: rather than a plain list,
:attr:`~sonolink.Player.queue` is a :class:`sonolink.Queue` object with history-backed
navigation, autoplay integration, and additional configuration via
:class:`~sonolink.models.AutoPlaySettings` and :class:`~sonolink.models.HistorySettings`.
Tracks are added via :meth:`~sonolink.Queue.put` rather than ``player.queue.append``.

Pausing is split into explicit :meth:`~sonolink.Player.pause` and
:meth:`~sonolink.Player.resume` methods rather than ``set_pause(True/False)``.

See :doc:`/guides/players` for the full playback reference.

Filters
-------

Lavalink.py defines filter classes (``Equalizer``, ``Karaoke``, ``Timescale``, ``Tremolo``,
``Vibrato``, ``Rotation``, ``LowPass``, ``ChannelMix``, ``Distortion``) that all derive from
``lavalink.Filter``, and applies them via ``DefaultPlayer.set_filter``:

.. code-block:: python

   # Lavalink.py
   karaoke = lavalink.Karaoke(level=0.5)
   await player.set_filter(karaoke)

SonoLink groups all filter configuration into a single :class:`sonolink.models.Filters`
object applied with :meth:`sonolink.Player.set_filters`. The individual filter types are the
same, just passed as constructor arguments to ``Filters``. The ``seek`` parameter optionally
restarts the current track position after applying:

.. code-block:: python

   # SonoLink
   from sonolink.models import Filters, Karaoke

   filters = Filters(karaoke=Karaoke(level=0.5))
   await player.set_filters(filters, seek=True)

.. note::
   Lavalink.py's ``lavalink.Volume`` filter class has no equivalent in SonoLink.
   Volume is controlled directly on the player via :attr:`sonolink.Player.volume`
   rather than through the :class:`~sonolink.models.Filters` system.

See :doc:`/guides/filters` for the full filter reference.

Events
------

Lavalink.py uses a ``@lavalink.listener`` decorator on cog methods, registered with
``Client.add_event_hooks``. Event objects are passed directly to the handler:

.. code-block:: python

   # Lavalink.py
   class MusicCog(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
           bot.lavalink.add_event_hooks(self)

       @lavalink.listener(lavalink.TrackStartEvent)
       async def on_track_start(self, event: lavalink.TrackStartEvent):
           ...

       @lavalink.listener(lavalink.TrackEndEvent)
       async def on_track_end(self, event: lavalink.TrackEndEvent):
           ...

SonoLink dispatches events through the Discord client with the ``sonolink_`` prefix, passing
a typed payload object alongside the player. You register handlers as standard Discord
event listeners:

.. code-block:: python

   # SonoLink
   @bot.event
   async def on_sonolink_track_start(player: sonolink.Player, payload):
       ...

   @bot.event
   async def on_sonolink_track_end(player: sonolink.Player, payload):
       ...

The event name mapping is:

.. list-table::
   :header-rows: 1

   * - Lavalink.py event class
     - SonoLink event
   * - ``TrackStartEvent``
     - :func:`on_sonolink_track_start(player, payload) <on_sonolink_track_start>`
   * - ``TrackEndEvent``
     - :func:`on_sonolink_track_end(player, payload) <on_sonolink_track_end>`
   * - ``TrackExceptionEvent``
     - :func:`on_sonolink_track_exception(player, payload) <on_sonolink_track_exception>`
   * - ``TrackStuckEvent``
     - :func:`on_sonolink_track_stuck(player, payload) <on_sonolink_track_stuck>`
   * - ``NodeConnectedEvent`` / ``NodeReadyEvent``
     - :func:`on_sonolink_node_ready(payload) <on_sonolink_node_ready>`
   * - ``NodeDisconnectedEvent``
     - :func:`on_sonolink_node_close(node) <on_sonolink_node_close>`
   * - ``PlayerUpdateEvent``
     - :func:`on_sonolink_player_update(player, payload) <on_sonolink_player_update>`
   * - ``WebSocketClosedEvent``
     - :func:`on_sonolink_websocket_closed(player, payload) <on_sonolink_websocket_closed>`
   * - ``TrackLoadFailedEvent``
     - *(no direct SonoLink equivalent)*
   * - ``IncomingWebSocketMessage``
     - *(no direct SonoLink equivalent)*
   * - ``PlayerErrorEvent``
     - *(no direct SonoLink equivalent)*
   * - ``QueueEndEvent``
     - *(handled internally; configure autoplay instead — see below)*
   * - ``NodeChangedEvent``
     - *(handled internally; SonoLink manages node failover automatically)*
   * - *(no equivalent)*
     - :func:`on_sonolink_player_disconnect(player, payload) <on_sonolink_player_disconnect>`

See :doc:`/api/events` for the full event reference and payload types.

Settings
--------

SonoLink introduces a settings system with no Lavalink.py equivalent. Settings are
dataclass-like objects passed at node or player creation time, giving you structured control
over behaviour that Lavalink.py left to manual implementation in event handlers:

* :class:`sonolink.models.InactivitySettings` — controls how long a player waits before
  disconnecting when the channel is inactive, and what counts as inactive.
* :class:`sonolink.models.CacheSettings` — configures the node-level LFU search result cache.
* :class:`sonolink.models.AutoPlaySettings` — configures autoplay mode, search provider,
  discovery count, and seed limits.
* :class:`sonolink.models.HistorySettings` — enables or limits the track history that
  ``previous`` and autoplay depend on.

.. code-block:: python

   from sonolink.models.settings import AutoPlaySettings, CacheSettings, HistorySettings, InactivitySettings
   from sonolink.gateway.enums import AutoPlayMode, InactivityMode

   sl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       inactivity_settings=InactivitySettings(
           timeout=300,
           mode=InactivityMode.ALL_BOTS,
       ),
       cache_settings=CacheSettings(
           enabled=True,
           max_items=1000,
       ),
   )

Autoplay and track history
--------------------------

Lavalink.py has no autoplay or track history system — bots that want either must build them
manually inside a ``QueueEndEvent`` or ``TrackEndEvent`` handler. SonoLink introduces both.

Autoplay is configured through :class:`sonolink.models.AutoPlaySettings` at player creation
time and toggled via :attr:`sonolink.Player.autoplay`, which accepts an
:class:`sonolink.AutoPlayMode` value:

* :attr:`sonolink.AutoPlayMode.DISABLED` — the player stops when the queue empties.
* :attr:`sonolink.AutoPlayMode.PARTIAL` — SonoLink manages queue progression autonomously
  but does not fill the queue with recommended tracks.
* :attr:`sonolink.AutoPlayMode.ENABLED` — when the queue empties, SonoLink discovers related
  tracks and fills the queue automatically.

Track history is enabled via :class:`sonolink.models.HistorySettings` and exposed through
:attr:`sonolink.Player.queue` as a :class:`sonolink.History` object. Autoplay uses history
as its seed, so the two features work together.

.. warning::
   Autoplay requires history to be enabled. If history is disabled through
   :class:`sonolink.models.HistorySettings` (``enabled=False``), autoplay will have no
   reference track to discover from.

Errors and exceptions
---------------------

Lavalink.py organises its errors under a ``ClientError`` base, with ``AuthenticationError``,
``InvalidTrack``, ``LoadError``, and ``RequestError`` as subclasses. SonoLink has a separate
exception hierarchy:

.. list-table::
   :header-rows: 1

   * - Lavalink.py
     - SonoLink
   * - ``AuthenticationError``
     - :exc:`sonolink.InvalidNodePassword`
   * - ``RequestError`` (HTTP failures)
     - :exc:`sonolink.HTTPException`
   * - ``InvalidTrack``
     - *(validated via* :class:`sonolink.models.SearchResult` *— check* ``is_error()`` *)*
   * - ``LoadError``
     - *(surface via* ``result.is_error()`` *on* :class:`sonolink.models.SearchResult` *)*
   * - *(no equivalent)*
     - :exc:`sonolink.QueueEmpty`
   * - *(no equivalent)*
     - :exc:`sonolink.HistoryEmpty`
   * - *(no equivalent)*
     - :exc:`sonolink.WebSocketError`
   * - *(no equivalent)*
     - :exc:`sonolink.NodeURINotFound`

See :doc:`/api/exceptions` for the full exception reference.

Useful references
-----------------

* `Lavalink.py repository <https://github.com/Devoxin/Lavalink.py>`_
* `Lavalink.py API reference <https://lavalink.readthedocs.io/en/development/>`_

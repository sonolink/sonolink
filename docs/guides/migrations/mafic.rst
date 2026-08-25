.. currentmodule:: sonolink

Moving From Mafic
=================

This guide is for migrating from `Mafic <https://github.com/ooliver1/mafic>`_ to SonoLink.

It walks through the main differences between SonoLink and Mafic, so you can get a feel for
what changes and what stays familiar.

If you are not migrating an existing Mafic bot, start with :doc:`/guides/getting-started`
instead.

What stays familiar
-------------------

* Lavalink remains the backend.
* SonoLink supports discord.py, py-cord, disnake, and nextcord via a custom
  ``discord.VoiceProtocol`` for voice integration — the same libraries Mafic supports.
* The main runtime objects are still a coordinator, nodes, players, tracks, playlists, and filters.

What changes
------------

Mafic centers its API around a ``NodePool`` bound to your Discord client and a
``Player.fetch_tracks`` search flow. SonoLink replaces both with instance-based equivalents,
introduces a structured settings system, and adds features like autoplay, track history, and a
node-level search cache that have no equivalent in Mafic.

Concept mapping
---------------

.. list-table::
   :header-rows: 1

   * - Mafic
     - SonoLink
   * - ``mafic.NodePool``
     - :class:`sonolink.Client`
   * - ``mafic.Node``
     - :class:`sonolink.Node`
   * - ``mafic.Player``
     - :class:`sonolink.Player`
   * - ``player.fetch_tracks(query, type=SearchType.YOUTUBE)``
     - :meth:`sonolink.Client.search_track` / :meth:`sonolink.Node.search_track`
   * - ``mafic.Track``
     - :class:`sonolink.models.Playable`
   * - ``mafic.Playlist``
     - :class:`sonolink.models.Playlist`
   * - ``mafic.SearchType``
     - :class:`sonolink.TrackSourceType`
   * - ``mafic.Filter``
     - :class:`sonolink.models.Filters`
   * - ``player.add_filter(filter)``
     - :meth:`sonolink.Player.set_filters`
   * - ``mafic.Strategy`` / ``mafic.NodePool`` selection
     - Automatic (see `Node selection`_ below)

Connection lifecycle
--------------------

In Mafic, you instantiate a ``NodePool`` with your bot and call ``create_node`` on it:

.. code-block:: python

   # Mafic
   pool = mafic.NodePool(bot)

   async def on_ready(self):
       await pool.create_node(
           host="127.0.0.1",
           port=2333,
           password="youshallnotpass",
           label="MAIN",
       )

In SonoLink, the coordinator is an explicit instance you create and own. Nodes are
registered on it, and you call :meth:`sonolink.Client.start` once your Discord client is
ready:

.. code-block:: python

   # SonoLink
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

Node selection
--------------

Mafic exposes ``NodePool.get_node`` with a pluggable ``Strategy`` system (``VoiceRegion``,
``Region``, ``Group``, and custom ``StrategyCallable`` types) for controlling which node a
player is assigned to.

SonoLink does not expose a strategy API at this level. Node selection for a new player is
handled automatically. If you need to target a specific node, you can do so explicitly via
:meth:`sonolink.Client.get_node`:

.. code-block:: python

   node = sl_client.get_node("main")
   player = node.create_player(...)

For most bots the automatic selection is sufficient and you will not need to call this directly.

Settings
--------

SonoLink introduces a settings system with no Mafic equivalent. Settings are dataclass-like
objects passed at node or player creation time, giving you structured control over behaviour
that Mafic either did not support or left to manual implementation:

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

Searching
---------

In Mafic, searching is done on the player instance and returns a list of tracks directly:

.. code-block:: python

   # Mafic
   tracks = await player.fetch_tracks(query, type=SearchType.YOUTUBE)
   if not tracks:
       return
   track = tracks[0]

In SonoLink, searching is done on the client or node and returns a
:class:`sonolink.models.SearchResult` wrapper that makes the result type explicit. The search
source is passed as a :class:`sonolink.TrackSourceType` value rather than a ``SearchType``:

.. code-block:: python

   # SonoLink
   result = await sl_client.search_track(query, source=sonolink.TrackSourceType.YOUTUBE)
   if result.is_error() or result.is_empty() or result.result is None:
       return

   data = result.result

   if isinstance(data, list):
       track = data[0]
   elif isinstance(data, sonolink.models.Playlist):
       track = data.tracks[0]
   else:
       track = data

:class:`sonolink.models.SearchResult` covers all possible outcomes: a single track, a
playlist, a search result list, an empty result, or an error — so you no longer need to
branch on the return type yourself.

.. note::
    Some ``mafic.SearchType`` members (e.g. ``APPLE_MUSIC``, ``TTS``, ``VK_MUSIC``,
    ``YANDEX_MUSIC``, ``DEEZER_ISRC``, ``SPOTIFY_RECOMMENDATIONS``) have no dedicated
    :class:`sonolink.TrackSourceType` member. Pass their raw prefix string (e.g.
    ``"amsearch"``) instead — source support still depends on your Lavalink server and
    installed plugins.

Tracks and playlists
--------------------

Mafic uses ``mafic.Track`` and ``mafic.Playlist``. In SonoLink the individual track type is
:class:`sonolink.models.Playable`, and :class:`sonolink.models.Playlist` is the playlist
equivalent. SonoLink tracks additionally carry :class:`sonolink.models.Album` and
:class:`sonolink.models.Artist` metadata when the source provides it.

Players and voice connection
----------------------------

Connecting to a voice channel works the same way:

.. code-block:: python

   player = await voice_channel.connect(cls=sonolink.Player)

The ``cls`` argument accepts a :class:`sonolink.Player` class or a pre-configured instance.
SonoLink automatically selects the correct internal adapter for your Discord library at
runtime via the ``SONOLINK_FRAMEWORK`` environment variable — you do not need to import
library-specific player classes yourself.

If you need to pre-configure a player before connecting:

.. code-block:: python

   player = sonolink.Player(
       node=node,
       volume=100,
   )

   await voice_channel.connect(cls=player)

Filters
-------

Mafic uses individual filter classes (``Karaoke``, ``Timescale``, etc.) applied one at a
time via ``player.add_filter``:

.. code-block:: python

   # Mafic
   await player.add_filter(mafic.Karaoke(level=0.5), label="karaoke")

SonoLink groups all filter configuration into a single :class:`sonolink.models.Filters`
object applied with :meth:`sonolink.Player.set_filters`. The individual filter types
(``Karaoke``, ``Timescale``, etc.) are the same, just passed as arguments to ``Filters``:

.. code-block:: python

   # SonoLink
   from sonolink.models import Filters, Karaoke

   filters = Filters(karaoke=Karaoke(level=0.5))
   await player.set_filters(filters, seek=True)

See :doc:`/guides/filters` for the full filter reference.

Errors and exceptions
---------------------

Mafic organises its errors under a ``MaficException`` base with subclasses for HTTP errors,
player errors, and library compatibility issues. SonoLink has a separate exception hierarchy:

.. list-table::
   :header-rows: 1

   * - Mafic
     - SonoLink
   * - ``NoNodesAvailable``
     - *(node selection is automatic; no direct equivalent)*
   * - ``PlayerNotConnected``
     - :exc:`RuntimeError`, raised when calling playback methods while disconnected
   * - ``HTTPException``
     - :exc:`sonolink.HTTPException`
   * - ``HTTPBadRequest``
     - :exc:`sonolink.HTTPException` (check ``status``)
   * - ``HTTPUnauthorized``
     - :exc:`sonolink.InvalidNodePassword`
   * - ``HTTPNotFound``
     - :exc:`sonolink.NodeURINotFound`
   * - *(no equivalent)*
     - :exc:`sonolink.QueueEmpty`
   * - *(no equivalent)*
     - :exc:`sonolink.HistoryEmpty`

See :doc:`/api/exceptions` for the full exception reference.

Events
------

Mafic dispatches events through the Discord client with unprefixed names such as
``on_track_start`` and ``on_node_ready``. SonoLink uses the ``sonolink_`` prefix and passes
a typed payload object alongside the player, making it easier to distinguish SonoLink events
from your bot's own events:

.. list-table::
   :header-rows: 1

   * - Mafic
     - SonoLink
   * - ``on_track_start(event)``
     - :func:`on_sonolink_track_start(player, payload) <on_sonolink_track_start>`
   * - ``on_track_end(event)``
     - :func:`on_sonolink_track_end(player, payload) <on_sonolink_track_end>`
   * - ``on_track_exception(event)``
     - :func:`on_sonolink_track_exception(player, payload) <on_sonolink_track_exception>`
   * - ``on_track_stuck(event)``
     - :func:`on_sonolink_track_stuck(player, payload) <on_sonolink_track_stuck>`
   * - ``on_node_ready(node)``
     - :func:`on_sonolink_node_ready(payload) <on_sonolink_node_ready>`
   * - ``on_node_unavailable(node)``
     - :func:`on_sonolink_node_close(node) <on_sonolink_node_close>`
   * - ``on_websocket_closed(event)``
     - :func:`on_sonolink_websocket_closed(player, payload) <on_sonolink_websocket_closed>`
   * - ``on_node_stats(node)``
     - :func:`on_sonolink_stats_receive(node, payload) <on_sonolink_stats_receive>`
   * - *(no equivalent)*
     - :func:`on_sonolink_player_disconnect(player, payload) <on_sonolink_player_disconnect>`

See :doc:`/api/events` for the full event reference and payload types.

Autoplay and track history
--------------------------

Mafic has no autoplay or track history system. SonoLink introduces both.

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

Useful references
-----------------

* `Mafic repository <https://github.com/ooliver1/mafic>`_
* `Mafic API reference <https://mafic.readthedocs.io/en/latest/>`_

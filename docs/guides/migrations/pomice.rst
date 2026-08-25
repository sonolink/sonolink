.. currentmodule:: sonolink

Moving From Pomice
==================

This guide is for migrating from `Pomice <https://github.com/cloudwithax/pomice>`_ to SonoLink.

It walks through the main differences between SonoLink and Pomice 2.x, so you can get a feel
for what changes and what stays familiar.

If you are not migrating an existing Pomice bot, start with :doc:`/guides/getting-started`
instead.

What stays familiar
-------------------

* Lavalink remains the backend.
* Pomice is built specifically around discord.py. SonoLink supports discord.py, py-cord,
  disnake, and nextcord, each using a custom ``discord.VoiceProtocol`` for voice integration.
* The main runtime objects are still a coordinator, nodes, players, queues,
  tracks, playlists, and filters.

What changes
------------

Pomice is built specifically around discord.py, a ``NodePool`` object, and player-driven
searching through ``Player.get_tracks``. SonoLink replaces that with an explicit
:class:`sonolink.Client`, a multi-framework voice adapter layer, and structured search
results instead of returning either a list, a playlist, or ``None`` directly.

Concept mapping
---------------

.. list-table::
   :header-rows: 1

   * - Pomice
     - SonoLink
   * - ``pomice.NodePool``
     - :class:`sonolink.Client`
   * - ``pomice.Node``
     - :class:`sonolink.Node`
   * - ``pomice.Player``
     - :class:`sonolink.Player`
   * - ``player.get_tracks(...)`` / ``node.get_tracks(...)``
     - :meth:`sonolink.Client.search_track` / :meth:`sonolink.Node.search_track`
   * - ``pomice.Track``
     - :class:`sonolink.models.Playable`
   * - ``pomice.Playlist``
     - :class:`sonolink.models.Playlist`
   * - ``pomice.SearchType``
     - :class:`sonolink.TrackSourceType`
   * - ``pomice.Filter`` / ``player.filters``
     - :class:`sonolink.models.Filters`
   * - ``player.add_filter(...)`` / ``player.remove_filter(...)`` / ``player.reset_filters(...)``
     - :meth:`sonolink.Player.set_filters`

Connection lifecycle
--------------------

Both libraries use a long-lived object that owns your Lavalink nodes, and both should be
started once your Discord client is ready. In Pomice, that object is ``pomice.NodePool``:

.. code-block:: python

   # Pomice
   pomice_pool = pomice.NodePool()

   async def setup_hook() -> None:
       await pomice_pool.create_node(
           bot=bot,
           host="127.0.0.1",
           port=2333,
           password="youshallnotpass",
           identifier="MAIN",
       )

In SonoLink, the equivalent object is :class:`sonolink.Client`. Nodes are registered on that
client, and :meth:`sonolink.Client.start` opens the Lavalink connections:

.. code-block:: python

   # SonoLink
   import sonolink

   sl_client = sonolink.Client(bot)

   sl_client.create_node(
       uri="http://127.0.0.1:2333",
       password="youshallnotpass",
       id="MAIN",
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

Pomice exposes ``NodePool.get_node`` and ``NodePool.get_best_node``. ``get_best_node`` uses
``NodeAlgorithm`` values such as ``by_ping`` and ``by_players`` when you want to pick from a
multi-node setup.

SonoLink handles the usual node choice automatically. If you need a specific node, fetch it
explicitly:

.. code-block:: python

   node = sl_client.get_node("MAIN")
   player = node.create_player(...)

For most bots, using :meth:`sonolink.Client.search_track` and connecting with
:class:`sonolink.Player` is enough and you do not need to select nodes manually.

Settings
--------

SonoLink keeps node and player behaviour in structured settings objects:

* :class:`sonolink.models.InactivitySettings` — controls how long a player waits before
  disconnecting when the channel is inactive, and what counts as inactive.
* :class:`sonolink.models.CacheSettings` — configures the node-level LFU search result cache.
* :class:`sonolink.models.AutoPlaySettings` — configures autoplay mode, search provider,
  discovery count, and seed limits.
* :class:`sonolink.models.HistorySettings` — enables or limits the track history that
  ``previous`` and autoplay depend on.

.. code-block:: python

   from sonolink.gateway.enums import AutoPlayMode, InactivityMode
   from sonolink.models.settings import AutoPlaySettings, CacheSettings, HistorySettings, InactivitySettings

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

   async def setup_hook() -> None:
       await sl_client.start()

       # get_best_node requires a connected node, so create players
       # only after Client.start() has finished.
       player = sl_client.get_best_node().create_player(
           autoplay_settings=AutoPlaySettings(
               mode=AutoPlayMode.ENABLED,
               discovery_count=10,
           ),
           history_settings=HistorySettings(
               enabled=True,
               max_items=100,
           ),
       )

Searching
---------

Pomice searches through ``Player.get_tracks`` or ``Node.get_tracks`` and returns a list of
tracks, a playlist, or ``None``:

.. code-block:: python

   # Pomice
   results = await player.get_tracks(query=search, search_type=pomice.SearchType.ytsearch)
   if not results:
       return

   if isinstance(results, pomice.Playlist):
       play_track = results.tracks[0]
       rest = results.tracks[1:]
   else:
       play_track = results[0]
       rest = results[1:]

In SonoLink, searching is done on the client or node and returns a
:class:`sonolink.models.SearchResult` wrapper:

.. code-block:: python

   # SonoLink
   result = await sl_client.search_track(search, source=sonolink.TrackSourceType.YOUTUBE)
   if result.is_error() or result.is_empty() or result.result is None:
       return

   data = result.result
   rest = []

   if isinstance(data, list):
       play_track = data[0]
       rest = data[1:]
   elif isinstance(data, sonolink.models.Playlist):
       play_track = data.tracks[0]
       rest = data.tracks[1:]
   else:
       play_track = data

:class:`sonolink.models.SearchResult` covers all possible outcomes: a single track, a
playlist, a search result list, an empty result, or an error result. This keeps the success
and failure branches explicit.

.. note::
   Pomice can parse Spotify and Apple Music URLs client-side when those options are enabled
   on the node. In SonoLink, normal search sources are selected with
   :class:`sonolink.TrackSourceType`, and source support still depends on your Lavalink
   server and installed plugins.

Tracks and playlists
--------------------

Pomice uses ``pomice.Track`` for individual tracks and ``pomice.Playlist`` for playlists.
In SonoLink the individual track type is :class:`sonolink.models.Playable`, and
:class:`sonolink.models.Playlist` is the playlist equivalent. SonoLink tracks also carry
:class:`sonolink.models.Album` and :class:`sonolink.models.Artist` metadata when the source
provides it.

Players and voice connection
----------------------------

Connecting still goes through Discord's ``VoiceChannel.connect`` API:

.. code-block:: python

   player = await voice_channel.connect(cls=sonolink.Player)

The ``cls`` argument accepts a :class:`sonolink.Player` class or a pre-configured instance.
SonoLink automatically selects the correct internal adapter for your Discord library at
runtime via the ``SONOLINK_FRAMEWORK`` environment variable — you do not need to import
library-specific player classes yourself.

If you need to configure a player before connecting, instantiate it directly or use
:meth:`sonolink.Node.create_player`:

.. code-block:: python

   player = node.create_player(volume=100)
   await voice_channel.connect(cls=player)

Playback flow
-------------

Pomice exposes ``Player.is_playing`` and lets ``Player.play`` replace the current track when
``ignore_if_playing`` is used. SonoLink exposes the equivalent
:attr:`sonolink.Player.is_playing` property, or you can check :attr:`sonolink.Player.current`
directly. Queue progression after a track ends is handled automatically:

.. code-block:: python

   # play_track and rest come from the search result — see Searching above
   if vc.current is None:
       await vc.play(play_track)
   else:
       rest = [play_track, *rest]

   for track in rest:
       await vc.queue.put_wait(track)

When a track ends, SonoLink automatically calls :meth:`sonolink.Player.skip` internally,
which pulls the next track from the queue, falls back to autoplay if the queue is empty, and
stops the player if neither applies. You do not need to drive this manually from a track-end
listener.

Filters
-------

Pomice uses filter stacking through methods on the player:

.. code-block:: python

   # Pomice
   await player.add_filter(pomice.Karaoke(level=0.5), fast_apply=True)
   await player.remove_filter("karaoke", fast_apply=True)
   await player.reset_filters(fast_apply=True)

SonoLink applies a single :class:`sonolink.models.Filters` object with
:meth:`sonolink.Player.set_filters`. The individual filter types are passed as constructor
arguments to ``Filters``:

.. code-block:: python

   # SonoLink
   from sonolink.models import Filters, Karaoke

   filters = Filters(karaoke=Karaoke(level=0.5))
   await player.set_filters(filters, seek=True)

To remove a filter, apply a new ``Filters`` object without that filter. To clear all filters,
apply an empty ``Filters`` object:

.. code-block:: python

   await player.set_filters(Filters(), seek=True)

See :doc:`/guides/filters` for the full filter reference.

Events
------

Pomice dispatches events through the Discord client with the ``pomice_`` prefix. SonoLink
uses the ``sonolink_`` prefix and passes typed payload objects alongside the player where
appropriate:

.. list-table::
   :header-rows: 1

   * - Pomice
     - SonoLink
   * - ``on_pomice_track_start(player, track)``
     - :func:`on_sonolink_track_start(player, payload) <on_sonolink_track_start>`
   * - ``on_pomice_track_end(player, track, reason)``
     - :func:`on_sonolink_track_end(player, payload) <on_sonolink_track_end>`
   * - ``on_pomice_track_exception(player, track, exception)``
     - :func:`on_sonolink_track_exception(player, payload) <on_sonolink_track_exception>`
   * - ``on_pomice_track_stuck(player, track, threshold)``
     - :func:`on_sonolink_track_stuck(player, payload) <on_sonolink_track_stuck>`
   * - ``on_pomice_websocket_closed(payload)``
     - :func:`on_sonolink_websocket_closed(player, payload) <on_sonolink_websocket_closed>`
   * - ``on_pomice_websocket_open(target, ssrc)``
     - *No direct SonoLink event*
   * - *(no equivalent)*
     - :func:`on_sonolink_player_disconnect(player, payload) <on_sonolink_player_disconnect>`

See :doc:`/api/events` for the full event reference and payload types.

Autoplay and track history
--------------------------

Pomice exposes recommendations through ``Player.get_recommendations`` and
``Node.get_recommendations``. SonoLink builds recommendation-style playback into its autoplay
and history systems.

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

State helpers
-------------

Pomice exposes ``Player.is_playing`` and ``Player.is_paused``. SonoLink provides the direct
equivalents :attr:`sonolink.Player.is_playing` and :attr:`sonolink.Player.paused`:

.. code-block:: python

   # Pomice
   if player.is_playing:
       ...

   if player.is_paused:
       ...

   # SonoLink
   if player.is_playing:
       ...

   if player.paused:
       ...

The common public player state in SonoLink is:

* :attr:`sonolink.Player.current` — the track currently playing, or ``None``.
* :attr:`sonolink.Player.is_playing` — whether a track is loaded **and** the player is not paused.
* :attr:`sonolink.Player.paused` — whether the player is paused.
* :attr:`sonolink.Player.position` — the current playback position in milliseconds.
* :attr:`sonolink.Player.volume` — the current volume, between 0 and 1000.
* :attr:`sonolink.Player.queue` — the :class:`sonolink.Queue` holding upcoming and historical tracks.
* :attr:`sonolink.Player.autoplay` — the current :class:`sonolink.AutoPlayMode` for this player.

Useful references
-----------------

* `Pomice repository <https://github.com/cloudwithax/pomice>`_
* `Pomice documentation <https://pomice.readthedocs.io/en/latest/>`_
* `Pomice API reference <https://pomice.readthedocs.io/en/latest/api/index.html>`_

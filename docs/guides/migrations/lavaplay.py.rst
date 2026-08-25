.. currentmodule:: sonolink

Moving From Lavaplay.py
=======================

This guide is for migrating from `Lavaplay.py <https://github.com/HazemMeqdad/lavaplay.py>`_ to SonoLink.

It walks through the main differences between SonoLink and Lavaplay, so you can get a feel for what
changes and what stays familiar.

If you are not migrating an existing Lavaplay bot, start with :doc:`/guides/getting-started`
instead.

What stays familiar
-------------------

* Lavalink remains the backend.
* SonoLink supports discord.py, py-cord, disnake, and nextcord via a custom
  ``discord.VoiceProtocol`` for voice integration.
* The main runtime objects are still a coordinator, nodes, players, tracks, playlists, and filters.

What changes
------------

Lavaplay is library-independent, which means it does not integrate with ``discord.py``'s voice
connection cache — utilities such as ``Context.voice_client`` return ``None`` even when connected,
and voice state updates must be forwarded manually. SonoLink is library-dependent and handles all
of this automatically through ``discord.VoiceProtocol``. It also adds a structured settings system,
an automated queue with history and autoplay, and automatic node selection.

Concept mapping
---------------

.. list-table::
    :header-rows: 1

    * - Lavaplay
      - SonoLink
    * - ``lavaplay.Lavalink``
      - :class:`sonolink.Client`
    * - ``lavaplay.Node``
      - :class:`sonolink.Node`
    * - ``lavaplay.Player``
      - :class:`sonolink.Player`
    * - ``lavaplay.Node.search_youtube`` / ``lavaplay.Node.search_soundcloud`` / ``lavaplay.Node.search_youtube_music`` / ``lavaplay.Node.get_track`` / ``lavaplay.Node.auto_search_tracks``
      - :meth:`sonolink.Client.search_track` / :meth:`sonolink.Node.search_track`
    * - ``lavaplay.Track``
      - :class:`sonolink.models.Playable`
    * - ``lavaplay.Playlist``
      - :class:`sonolink.models.Playlist`
    * - ``lavaplay.TrackLoadFailed``
      - :attr:`sonolink.models.SearchResult.exception`
    * - ``lavaplay.Filters``
      - :class:`sonolink.models.Filters`
    * - ``lavaplay.Player.filters``
      - :meth:`sonolink.Player.set_filters`

Connection lifecycle
--------------------

In Lavaplay, you create a ``Lavalink`` instance, and then create a ``Node`` with ``Lavalink.create_node``:

.. code-block:: python

    # Lavaplay.py
    lavalink = Lavalink()
    node = lavalink.create_node(
        host="127.0.0.1",
        port=2333,
        password="youshallnotpass",
        user_id=0,
    )

    # in any function, either a library's on_ready or just a set up:
    node.connect()

In SonoLink, this is essentially the same, but with some changes:

.. code-block:: python

    # SonoLink
    sl_client = sonolink.Client(bot)

    sl_client.create_node(
        uri="http://127.0.0.1:2333",
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

Lavaplay keeps its node management in a single ``Node`` class, which the players are bound to,
and offers no built-in selection between nodes.

SonoLink handles all nodes internally, but still allows for node selection per player, exposing
:meth:`sonolink.Node.create_player`, similar to Lavaplay's ``Node.create_player``.

.. code-block:: python

   node = sl_client.get_node("main")
   player = node.create_player(...)

For most bots, the automatic node selection SonoLink offers is sufficient and you will not need to call this
directly.

Players and voice connection
----------------------------

Lavaplay does not directly expose a ``discord.VoiceProtocol``, but instead relies on you providing the required data to
connect and update the player, either via a custom ``discord.VoiceProtocol`` subclass, or receiving raw events.

.. code-block:: python

    # Lavaplay.py
   player = node.create_player(ctx.guild.id)
    await ctx.guild.change_voice_state(
        channel=ctx.author.voice.channel,
    )

    async def on_voice_server_update(data):
        await player.raw_voice_server_update(data)

    # other methods required, such as voice_state_update

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
----------------------------

In Lavaplay.py, searching is done through any ``Node.search_X`` method, or ``Node.get_tracks``,
which returns a list of ``Track``\s, a ``Playlist``, or a ``TrackLoadFailed``.

.. code-block:: python

    # Lavaplay.py
    result = await node.get_tracks(query)

    if not result or isinstance(result, TrackLoadFailed):
        return

    if isinstance(result, PlayList):
        track = result.tracks[0]
    else:
        track = result[0]

In SonoLink, searching is done through :meth:`sonolink.Client.search_track` (or its equivalent on
the node: :meth:`sonolink.Node.search_track`). This method returns a :class:`sonolink.models.SearchResult`
wrapper. If you want to specify a source, you can either pass a prefix in ``query``, or pass
a :class:`sonolink.TrackSourceType` enum member or string.

.. code-block:: python

    # SonoLink
    result = await sl_client.search_track(query, source=sonolink.TrackSourceType.SOUNDCLOUD)
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
playlist, a search result list, an empty result, or an error.

Tracks
------

Lavaplay.py provides the ``lavaplay.Track`` model for individual tracks. The SonoLink equivalent is
:class:`sonolink.models.Playable`. SonoLink tracks additionally carry :class:`sonolink.models.Album`
and :class:`sonolink.models.Artist` metadata when the source provides it.

Playback
--------

:class:`sonolink.Player` exposes almost the same methods as Lavaplay.py's ``Player`` class,
with the following main differences:

* Unlike Lavaplay.py, :attr:`sonolink.Player.queue` is a :class:`sonolink.Queue` object, which also provides
  history-backed navigation, autoplay integration, and additional configuration via :class:`~sonolink.models.AutoPlaySettings`
  and :class:`~sonolink.models.HistorySettings`. Tracks are added via :meth:`~sonolink.Queue.put` rather than
  ``player.queue.append``, and all queue-related methods live under :attr:`sonolink.Player.queue`.
* Lavaplay.py offers ``player.play`` and ``player.play_playlist``. The former has a direct SonoLink equivalent,
  :meth:`~sonolink.Player.play`, while the latter does not and requires manual iteration through the playlist tracks
  calling ``play`` on each.
* In SonoLink, pausing and resuming are split into two separate methods: :meth:`~sonolink.Player.pause` and
  :meth:`~sonolink.Player.resume`, unlike Lavaplay.py where you called ``player.pause(True/False)``.

See :doc:`/guides/players` for the full playback reference.

Filters
-------

In Lavaplay.py, filters are all encapsulated in the ``Filters`` class, offering methods such as ``Filters.equalizer``
or ``Filters.karaoke`` to update or set a filter, applied via ``player.filters(filters)``.

.. code-block:: python

    # Lavaplay.py
    filters = lavaplay.Filters()
    filters.equalizer([(0, 0.5)])  # set band 0 gain to 0.5

    await player.filters(filters)

In SonoLink, the :class:`~sonolink.models.Filters` class takes all filters you want to update as constructor
arguments, then you call :meth:`~sonolink.Player.set_filters` to apply them. The ``seek`` parameter optionally
restarts the current track position after applying:

.. code-block:: python

    # SonoLink
    filters = sonolink.models.Filters(
        equalizer=[
            sonolink.models.Equalizer(
                band=0,
                gain=0.5,
            ),
        ],
    )

    await player.set_filters(filters)

See :doc:`/guides/filters` for the full filter reference.

Events
------

Lavaplay.py uses a ``@node.listen`` decorator on each ``Node`` instance to attach and handle events, passing
the event model or event name:

.. code-block:: python

    # Lavaplay.py
    @node.listen(lavaplay.TrackStartEvent)
    async def on_track_start(event: lavaplay.TrackStartEvent) -> None:
        print("New track started playing:", event.track.title)

    @node.listen("TrackEndEvent")
    async def on_track_end(event: lavaplay.TrackEndEvent) -> None:
        print("Track finished playing:", event.track.title)

SonoLink instead dispatches events through your library's client with the ``sonolink_`` prefix, passing a typed
payload object alongside the player. You register handlers as standard Discord event listeners:

.. code-block:: python

    # SonoLink
    @bot.event
    async def on_sonolink_track_start(player: sonolink.Player, payload: sonolink.gateway.TrackStartEvent) -> None:
        print("New track started playing:", payload.track.title)

    @bot.event
    async def on_sonolink_track_end(player: sonolink.Player, payload: sonolink.gateway.TrackEndEvent) -> None:
        print("Track finished playing:", payload.track.title)

The event name mapping is:

.. list-table::
    :header-rows: 1

    * - Lavaplay.py event class or name
      - SonoLink event
    * - ``ReadyEvent``
      - :func:`on_sonolink_node_ready(payload) <on_sonolink_node_ready>`
    * - ``TrackStartEvent``
      - :func:`on_sonolink_track_start(player, payload) <on_sonolink_track_start>`
    * - ``TrackEndEvent``
      - :func:`on_sonolink_track_end(player, payload) <on_sonolink_track_end>`
    * - ``StatsUpdateEvent``
      - *(handled internally; you may access the updated data via* :attr:`~sonolink.Node.stats` *)*
    * - ``TrackExceptionEvent``
      - :func:`on_sonolink_track_exception(player, payload) <on_sonolink_track_exception>`
    * - ``TrackStuckEvent``
      - :func:`on_sonolink_track_stuck(player, payload) <on_sonolink_track_stuck>`
    * - ``WebSocketClosedEvent``
      - :func:`on_sonolink_websocket_closed(player, payload) <on_sonolink_websocket_closed>`
    * - ``ErrorEvent``
      - *(no direct SonoLink equivalent)*
    * - ``PlayerUpdateEvent``
      - :func:`on_sonolink_player_update(player, payload) <on_sonolink_player_update>`
    * - *(no equivalent)*
      - :func:`on_sonolink_player_disconnect(player, payload) <on_sonolink_player_disconnect>`

See :doc:`/api/events` for the full event reference and payload types.

Settings
--------

SonoLink introduces a settings system with no Lavaplay.py equivalent. Settings are dataclass-like
objects passed at node or player creation time, giving you structured control over behaviour that
Lavaplay.py left to manual implementation in event handlers:

* :class:`sonolink.models.InactivitySettings` — controls how long a player waits before disconnecting
  when the channel is inactive, and what counts as inactive.
* :class:`sonolink.models.CacheSettings` — configures the node-level LFU search result cache.
* :class:`sonolink.models.AutoPlaySettings` — configures autoplay mode, search provider,
  discovery count, and seed limits.
* :class:`sonolink.models.HistorySettings` — enables or limits the track history that ``previous``
  and autoplay depend on.

.. code-block:: python

    from sonolink.models import AutoPlaySettings, CacheSettings, HistorySettings, InactivitySettings
    from sonolink.gateway import AutoPlayMode, InactivityMode

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

Lavaplay.py has no history or autoplay system — bots that want either must build them manually, although
it provides helpful methods such as ``Node.auto_search_tracks``. SonoLink introduces both features by default.

Autoplay is configured through :class:`sonolink.models.AutoPlaySettings` at player creation time, and toggled
via :attr:`sonolink.Player.autoplay`, which accepts an :class:`sonolink.AutoPlayMode` value:

* :attr:`sonolink.AutoPlayMode.DISABLED` — the player stops when the queue empties.
* :attr:`sonolink.AutoPlayMode.PARTIAL` — SonoLink manages queue progression autonomously but does not fill the
  queue automatically.
* :attr:`sonolink.AutoPlayMode.ENABLED` — when the queue empties, SonoLink discovers related tracks and fills
  the queue automatically.

Track history is enabled via :class:`sonolink.models.HistorySettings` and exposed through :attr:`sonolink.Player.queue`
as a :class:`sonolink.History` object. Autoplay uses history as its seed, so the two features work together.

.. warning::
    Autoplay requires history to be enabled. If history is disabled through
    :class:`sonolink.models.HistorySettings` (``enabled=False``), autoplay will have no
    reference track to discover from.

Errors and exceptions
---------------------

Lavaplay.py exposes different errors as ``Exception`` subclasses. SonoLink provides a subclass-based hierarchy
for them:

.. list-table::
    :header-rows: 1

    * - Lavaplay.py
      - SonoLink
    * - ``FiltersError`` and ``VolumeError``
      - *(no direct SonoLink equivalent)*
    * - ``NotConnectedError`` and ``ConnectedError``
      - :exc:`RuntimeError`, raised for their corresponding methods (e.g. ``RuntimeError`` when calling :meth:`Node.connect`
        means the node is already connected)
    * - ``TrackLoadFailed``
      - *(surface via* ``result.is_error()`` *on* :class:`sonolink.models.SearchResult` *)*
    * - ``requestFailed`` (HTTP failures)
      - :exc:`sonolink.HTTPException`
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

* `Lavaplay.py repository <https://github.com/HazemMeqdad/lavaplay.py>`_
* `Lavaplay.py API reference <https://lavaplay.readthedocs.io/en/latest>`_

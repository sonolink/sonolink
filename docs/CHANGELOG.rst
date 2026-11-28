.. currentmodule:: sonolink
.. _whats_new:

Changelog
=========

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

`Unreleased`_
-------------

**Added**
~~~~~~~~~

**Changed**
~~~~~~~~~~~

**Fixed**
~~~~~~~~~

**Removed**
~~~~~~~~~~~

**Deprecated**
~~~~~~~~~~~~~~

**Miscellaneous**
~~~~~~~~~~~~~~~~~

- Added ``:gh-commit:`` and ``:gh-issue:`` roles for linking to GitHub commits and issues, respectively, on changelog
  entries. (:gh-issue:`145`)

.. _unreleased: https://github.com/sonolink/sonolink/compare/v1.4.1..HEAD

.. _vp1p4p1:

v1.4.1 - 2026-11-07
-------------------

**Fixed**
~~~~~~~~~

- Fixed missing exports in ``__all__`` for ``sonolink.*`` and ``sonolink.gateway``. (:gh-issue:`134`)
- Fixed a ``SyntaxWarning`` on Python 3.14+ caused by a ``return`` inside the
  ``finally`` block of the player disconnect lifecycle. (:gh-issue:`137`)

**Miscellaneous**
~~~~~~~~~~~~~~~~~
- Mentioned support for new Python 3.15 in related files. (:gh-issue:`127`)
- Re-licensed sonolink from MIT to Apache 2.0. (:gh-issue:`128`)
- Added a new way to contact maintainers in case of a security issue (email). (:gh-issue:`135`)

.. _vp1p4p0:

v1.4.0 - 2026-09-16
-------------------

**Added**
~~~~~~~~~

- Added a ``no_replace`` parameter to :meth:`Player.play` that maps to
  Lavalink's ``noReplace`` query parameter. (:gh-issue:`76`)
- Added :meth:`Queue.total_duration` to compute the total duration of all
  tracks in the queue, including the current track and AutoPlay-discovered
  tracks. AutoPlay tracks can be excluded via ``with_autoplay=False``. (:gh-issue:`78`)
- Added :meth:`Queue.duration_until` to compute the cumulative duration of all
  queued tracks before a given index, supporting negative indices. (:gh-issue:`78`)
- Added :attr:`Player.is_playing` to check whether the player is currently
  playing a track (a track is loaded and the player is not paused). (:gh-issue:`82`)
- Added :attr:`Player.remaining` to check the estimated playback time
  remaining for the current track, calculated as ``track.length - player.position``. (:gh-issue:`82`)
- Added :attr:`Player.history` as a convenience alias for :attr:`Queue.history`,
  returning ``None`` when history tracking is disabled. (:gh-issue:`82`)
- Added a ``secure`` parameter to :meth:`Client.create_node` that builds an
  ``https://``/``wss://`` URI when using ``host`` and ``port``, so TLS nodes no
  longer require passing a full ``uri``. (:gh-issue:`97`)
- Added ``Queue.__setitem__`` to replace the track(s) at an index or slice,
  mirroring ``list`` assignment semantics. (:gh-issue:`101`)
- Added :meth:`History.clear` to remove all tracks from the history.
  Previously only reachable indirectly through :meth:`Queue.clear_history`. (:gh-issue:`100`)
- Added a ``paused`` parameter to :meth:`Player.update` for pausing or
  resuming playback. (:gh-issue:`99`)

**Fixed**
~~~~~~~~~

- Fixed :meth:`Filters.combine` mutating the second operand. ``other`` is now
  deep-copied before merging, so neither input is aliased or reordered. (:gh-issue:`118`)
- Fixed :attr:`sonolink.Playable.playlist` being ``None`` on tracks loaded from playlists. (:gh-issue:`117`)
- Fixed :attr:`~sonolink.HTTPException.timestamp` creating Lavalink's millisecond
  error timestamps as seconds, which raised ``OSError``/``OverflowError`` when accessed. (:gh-issue:`116`)
- Fixed :meth:`RESTClient.version` requesting ``/v4/version`` instead of ``/version``. (:gh-issue:`115`)
- Fixed :attr:`Player.paused` being cleared by :attr:`~sonolink.gateway.TrackStartEvent`
  even when a track was started / replaced with ``paused=True``. (:gh-issue:`114`)
- Fixed :meth:`Player.play` with `no_replace=True` corrupting state when track gets rejected. (:gh-issue:`113`)
- Fix pause/resume corrupting estimated playback position. :meth:`Player.pause` now saves
  the current interpolated position before freezing, preventing stale values on resume. (:gh-issue:`112`)
- Fixed :attr:`~sonolink.gateway.TrackStartEvent.original` being ``None`` after a track ended
  and the next started via ``skip()``. (:gh-issue:`89`)
- Fixed AutoPlay re-discovering and re-queueing tracks that were already
  recommended in a previous round, because only the seed reference was tracked. (:gh-issue:`87`)
- Fixed duplicated history entries on track transitions in :meth:`Player.play`.
- Fixed :meth:`Queue.move` placing tracks one position before the requested
  target index when moving them forward. (:gh-issue:`84`)
- Fixed :meth:`Client.create_node` building a scheme-less URI (e.g.
  ``host:port``) when given ``host`` and ``port``, which caused all REST
  requests to fail client-side. (:gh-issue:`97`)

**Changed**
~~~~~~~~~~~

**Deprecated**
~~~~~~~~~~~~~~

- Deprecated :meth:`Queue.clear_history` in favor of :meth:`History.clear`. (:gh-issue:`100`)

**Miscellaneous**
~~~~~~~~~~~~~~~~~

- Removed the internal, never-read ``_ready`` attribute from the player.
- Exposed ``SonoLinkException`` exception class to prevent docs building warnings.
- Moved ``ruff`` and `basedpyright` into dependency-groups so CI workflows can install them
  individually via ``pip install --group <name>``.
- Added a unit test suite, run via a new ``tests`` workflow on every PR.
- Added automatic version bumping after each release, so the development version
  and changelog are committed and pushed by the release workflow.
- Corrected API inaccuracies in the library migration guides
  (:doc:`/guides/migrations/index`).
- Bumped the minimum ``nextcord`` version to 3.2 (adds DAVE support).
- Added a `CONTRIBUTING <https://github.com/sonolink/sonolink/blob/main/.github/CONTRIBUTING.md>`_
  guide with instructions for opening contributions.
- Corrected typos and clarified player volume and filter combination behavior in
  the API documentation.

.. _vp1p3p0:

v1.3.0 - 2026-07-20
-------------------

**Added**
~~~~~~~~~

- Added various helper methods to :class:`Queue`: (:gh-issue:`57`)

  - :meth:`Queue.sort` to sort the queue by a given key function. Similar to Python's built-in :meth:`list.sort` method.

    - Example: ``queue.sort(key=lambda track: track.title)`` to sort by track title.
  - :meth:`Queue.reverse` to reverse the order of the queue.
  - :meth:`Queue.dedupe` to remove duplicate tracks from the queue.
  - ``Queue.__reversed__`` to allow the built-in :func:`reversed` function on the queue.

- Added :attr:`History.enabled` property for checking whether history recording is active. (:gh-issue:`66`)
- Added :meth:`Player.skip_to` to skip directly to a track at a specific
  queue index. (:gh-issue:`64`)
- Added :meth:`Queue.move` to move a track from one index to another, shifting
  other tracks accordingly. (:gh-issue:`63`)
- Added :meth:`Queue.remove_at` to remove and return a track by index without
  side effects on the current track. (:gh-issue:`63`)
- Added a ``key`` parameter to :meth:`Queue.remove` and :meth:`Queue.remove_wait` for removing
  tracks by an arbitrary derived value instead of equality, without needing to hold the original
  :class:`Playable` instance. (:gh-issue:`59`)

  - Example: ``queue.remove([track.identifier], key=lambda t: t.identifier)`` to remove a track
    by its identifier.

- Added :class:`ShuffleMode` and :attr:`Queue.shuffle_mode` for persistent shuffle support. (:gh-issue:`58`)

  - Independent of :class:`QueueMode`.
  - While :attr:`ShuffleMode.PERSISTENT` is active, :meth:`Queue.get` pops a random track instead of
    the next one in order, without reordering the underlying queue. Switching back to
    :attr:`ShuffleMode.DEFAULT` resumes playback in the original order.
  - :meth:`Queue.shuffle` is unaffected and still performs its usual one-time in-place reorder.

- Added a ``key`` parameter to :meth:`Queue.get` and :meth:`Queue.get_wait` to avoid picking a
  track that collides with the current track on an arbitrary derived value, e.g. to avoid
  repeats. (:gh-issue:`69`)

  - Example: ``queue.get(key=lambda track: track.author)`` to avoid picking a track by the
    currently playing artist.
  - If every remaining candidate collides, the collision is allowed rather than raising.

- Added a ``key`` parameter to :meth:`Player.skip`, forwarded straight through to
  :meth:`Queue.get`, so the same repeat-avoidance behaves consistently whether tracks are
  pulled from the queue directly or via the player. (:gh-issue:`69`)

  - Example: ``await player.skip(key=lambda track: track.author)``.

**Fixed**
~~~~~~~~~

- Fixed :meth:`Queue.get_wait` not registering the waiter before attempting to
  retrieve a track, causing a race condition where a concurrent ``put()`` could
  be missed and the waiter would hang indefinitely. (:gh-commit:`b81977b`)
- Fixed :attr:`Queue.history` returning a :class:`History` instance when history
  is disabled; now correctly returns ``None``. (:gh-commit:`629135b`)
- Fixed :meth:`Player.play` not pushing the previously playing track to history
  before starting a new track, matching the documented behavior. (:gh-commit:`b9dadde`)
- Fixed :meth:`Player.stop` with ``clear_queue=True`` not clearing
  AutoPlay-discovered tracks from the queue. (:gh-commit:`66de09e`)
- Fixed :meth:`Player.stop` silently resetting :attr:`Queue.mode` to
  :attr:`QueueMode.NORMAL` when ``clear_queue=True``; this is now documented
  behavior. (:gh-commit:`e7e34e5`)
- Fixed :meth:`Queue.copy` creating a new :class:`History` that shared a
  mutable reference to the original settings object, causing mutations to
  ``enabled`` or ``max_items`` to leak between copies. (:gh-commit:`27492b6`)
- Fixed :meth:`Queue.remove` with a ``key`` parameter ignoring duplicate lookup
  values and crashing on unhashable types; both the ``remove_all=True`` and
  ``remove_all=False`` paths now consistently respect user-provided values. (:gh-commit:`1780602`)
- Added missing exports for :exc:`AutoPlaySeedMissing`,
  :exc:`FrameworkClientMismatch`, and :exc:`FrameworkImportError` to the
  top-level ``__all__``. (:gh-commit:`f16c1a5`)
- Fixed ``Player.on_track_end`` dispatching :class:`TrackEndEvent` with the
  wrong ``original`` track when ``skip()`` was triggered, because
  ``_original_track`` was overwritten by ``play()`` before the event was
  emitted. (:gh-commit:`4583c4c`)
- Fixed :meth:`Player.previous` pushing the previous track back into history
  after ``play()`` was called, creating a duplicate history entry. (:gh-commit:`8cc562d`)
- Fixed :class:`Filters` constructor not calling ``super().__init__()``, leaving
  ``_client`` and ``_data`` uninitialised on direct construction. (:gh-commit:`db1144a`)

**Miscellaneous**
~~~~~~~~~~~~~~~~~

- Consolidated the separate ``pr-checks`` and ``pr-template`` workflows into a
  single ``pr-governance`` workflow. (:gh-issue:`68`)
- Scoped all CI job permissions to read-only and disabled credential persistence
  on checkout for improved security. (:gh-issue:`68`)
- Added a 15-minute timeout to every CI job. (:gh-issue:`68`)
- Enabled ``pip`` caching across CI workflows. (:gh-issue:`68`)
- Added concurrency control to the lint workflow to cancel redundant runs. (:gh-issue:`68`)
- Added ``twine check`` and build provenance attestation to the release workflow. (:gh-issue:`68`)
- Hardened the template-check validation and excluded draft PRs from template
  enforcement, triggering checks only on ``ready_for_review``. (:gh-issue:`68`)
- Added sticky ``h2``/``h3`` headers, a hover-highlights toggle persisted in
  ``localStorage``, and alphabetical "On this page" TOC sorting to the docs. (:gh-issue:`60`)
- Enabled ``nitpicky`` Sphinx mode and ``sphinx-autodoc-typehints``; replaced
  raw ``:class:`` references with proper cross-references throughout. (:gh-issue:`60`)
- Exposed missing exception classes (``SonoLinkException``, ``NodeError``,
  ``NetworkError``) and ``Version``/``GitInfo`` models in the API docs. (:gh-commit:`83559b3`)

.. _vp1p2p1:

v1.2.1 - 2026-07-04
-------------------

**Added**
~~~~~~~~~

- Added the missing ``NetworkError`` export to the public API. (:gh-commit:`2aba636`)

**Fixed**
~~~~~~~~~

- Fixed a typo in ``__repr_attrs__`` of :class:`~sonolink.gateway.WebSocketClosedEvent`. (:gh-commit:`6f534b4`)
- Fixed an incorrect datetime timestamp in :attr:`~sonolink.gateway.schemas.PlayerState.time` caused by differing time
  units. (:gh-commit:`7fd208a`)
- Fixed an issue where the node status would remain stuck on :attr:`NodeStatus.CONNECTING` after
  an ``attempt_connect`` failure. (:gh-commit:`f43aa91`)
- Fixed :class:`Filters` not populating data on the instance. (:gh-commit:`253a6a4`)
- Fixed a race condition in the node reconnection flow that caused an intermittent
  "Timed out waiting for node READY payload" error after prolonged uptime. (:gh-issue:`56`)

.. _vp1p2p0:

v1.2.0 - 2026-06-23
-------------------

**Added**
~~~~~~~~~

- Added :attr:`Node.is_connecting` property for checking whether a node is currently establishing a connection. (:gh-commit:`5feaca0`)
- Added the missing `auto_reconnect` parameter to :meth:`Client.create_node` for controlling whether the client should
  automatically attempt to reconnect to the node on disconnection. This defaults to ``True``. (:gh-issue:`45`)
- Added :meth:`Node.reconnect` for manually triggering a reconnection to the node. (:gh-issue:`45`)
- Added :attr:`~sonolink.gateway.TrackStartEvent.original` and :attr:`~sonolink.gateway.TrackEndEvent.original` to access
  the original track passed to :meth:`Player.play`. (:gh-issue:`47`)
- Serializable extras are now forwarded to Lavalink as ``user_data`` and accessible via
  :attr:`~sonolink.models.Playable.extras` on reconstructed tracks. Non-serializable values are warned and
  accessible via ``.original.extras``. (:gh-issue:`47`)
- Added support for region-aware node selection (:gh-issue:`49`):

  - Added :class:`NodeRegion` enum representing the available Discord voice channel regions a node can serve.
  - Added ``regions`` parameter to :meth:`Client.create_node` and :class:`Node` to associate a node with one or more
    :class:`NodeRegion` values (or raw strings).
  - Added ``region`` parameter to :meth:`Client.get_best_node`, :meth:`Client.search_track`, :meth:`Client.decode_track`,
    and :meth:`Client.decode_tracks` to drive region-aware node selection.
  - :class:`~sonolink.gateway.player._base.BasePlayer` now automatically passes its voice region to
    :meth:`Client.get_best_node` when selecting a node on connect.

**Fixed**
~~~~~~~~~

- Fixed an issue where the client would not attempt to reconnect to a node after a disconnection, even if ``auto_reconnect``
  was enabled. (:gh-issue:`45`)
- Fixed an issue with using the `speed` extra, or the ``curl-cffi`` package where it would raise a `CurlError` and
  the library would fail to handle it properly, causing the node to be left in a broken state. (:gh-issue:`45`)
- Fixed an internal race condition where :meth:`Node.connect` could be called on an already-connected node, causing a
  :exc:`RuntimeError` to be silently raised in the background after extended uptime. (:gh-commit:`30534b7`)

.. _vp1p1p1:

v1.1.1 - 2026-05-15
-------------------

**Fixed**
~~~~~~~~~

- Recursion issue in :class:`sonolink.Player` custom subclass and instance checks that raised a
  :exc:`RecursionError` during ``issubclass`` or ``isinstance`` checks. (:gh-commit:`3c94285`)
- :class:`sonolink.Player` not properly disconnecting after Discord 4014 and 4022 voice close
  events, which could leave players stuck in an invalid voice session state. (:gh-commit:`88c3996`)
- :class:`sonolink.Player` not disconnecting on stale LavaLink session. (:gh-commit:`2a08185`)
- Missing typings for :attr:`sonolink.gateway.PlayerDisconnectEvent.extra_data` on
  :class:`sonolink.gateway.PlayerDisconnectEvent`. (:gh-issue:`37`)

.. _vp1p1p0:

v1.1.0 - 2026-05-14
-------------------

**Added**
~~~~~~~~~

- Added support for `Nextcord <https://github.com/nextcord/nextcord>`_ via :class:`NextcordPlayer <.adapters._nextcord.NextcordPlayer>`.
  (:gh-issue:`25`)

  See the `Nextcord examples <https://github.com/sonolink/sonolink/tree/main/examples/nextcord>`_ for usage.
- Added :func:`sonolink.get_client <sonolink._registry.get_client>` for retrieving the active client instance.
  (:gh-commit:`5b9b7ee`)
- Added :meth:`Client.get_node` to retrieve a specific node from the client. (:gh-commit:`72143b8`)
- Added three new events:

  - :func:`on_sonolink_websocket_closed` (:class:`WebSocketClosedEvent`) (:gh-commit:`f05be5f`)
  - :func:`on_sonolink_stats_receive` (:class:`StatsEvent`) (:gh-commit:`585f8e6`)
  - :func:`on_sonolink_player_disconnect` (:class:`PlayerDisconnectEvent`) (:gh-issue:`32`)

- Added :meth:`Player.update` to quickly update multiple player settings at once. (:gh-commit:`5068893`)
  :attr:`Player.autoplay_settings`, :attr:`Player.history_settings`, and :attr:`Player.queue_mode`
  are now exposed and can be set directly. (:gh-commit:`d1f18f6`)
- Added :attr:`TrackSourceType.DEEZER` as a supported track source. (:gh-commit:`8067304`)
- Added :attr:`Queue.count` and :attr:`History.count` properties. (:gh-commit:`1a81a57`)
- Added :attr:`Queue.autoplay_tracks` and :meth:`Queue.put_autoplay` to fix autoplay queue priority
  via a dedicated stream. :attr:`~sonolink.models.Playable.autoplay` is also now exposed. (:gh-commit:`4f6a1f9`)
- Added :exc:`AutoPlaySeedMissing`, a specific error raised when autoplay has no seed tracks to
  generate from. (:gh-commit:`48c67f4`)
- Added framework-specific import and mismatch exceptions (:gh-issue:`28`):

  - :exc:`FrameworkClientMismatch`
  - :exc:`FrameworkImportError`

- Added a :doc:`Getting Started </guides/getting-started>` guide. (:gh-issue:`36`)
- Added four new migration guides (:gh-issue:`29`):

  - `Mafic <https://sonolink.readthedocs.io/en/latest/guides/migrations/mafic.html>`_
  - `Lavalink.py <https://sonolink.readthedocs.io/en/latest/guides/migrations/lavalink.py.html>`_
  - `Lavaplay.py <https://sonolink.readthedocs.io/en/latest/guides/migrations/lavaplay.py.html>`_
  - `Pomice <https://sonolink.readthedocs.io/en/latest/guides/migrations/pomice.html>`_

  The existing `WaveLink <https://sonolink.readthedocs.io/en/latest/guides/migrations/wavelink.html>`_ guide has also been updated.

- Added a `py.typed <https://typing.python.org/en/latest/spec/distributing.html#packaging-typed-libraries>`_ marker file
  for improved typing compatibility with type checkers. (:gh-commit:`f058e94`)
- Added two new keyword arguments to :meth:`Client.create_node`: ``host`` and ``port`` for
  specifying the node URI in parts as an alternative to the single ``uri`` string; ``uri``
  is now optional to allow for this. (:gh-issue:`34`)
- Added a `Code of Conduct <https://github.com/sonolink/sonolink/blob/main/.github/CODE_OF_CONDUCT.md>`_ for project
  community guidelines. (:gh-commit:`9893e41`)

**Changed**
~~~~~~~~~~~

- ``WSCloseEvent`` has been renamed to :class:`~sonolink.gateway.WebSocketClosedEvent`. (:gh-commit:`037dedb`)
- :meth:`get_best_node` now prefers nodes with known stats over nodes with no reported stats. (:gh-commit:`b93f8bc`)
- Swapped :exc:`asyncio.TimeoutError` with the built-in :exc:`TimeoutError` throughout. (:gh-commit:`68f3502`)
- Cleaned up documentation for all enums.

**Removed**
~~~~~~~~~~~

- Removed the fallback to ``discord.py`` as the default framework. (:gh-commit:`85c2b37`)
- Removed the unused ``value`` argument from :meth:`Player.pause`. (:gh-commit:`33f62d0`)
  :meth:`Player.resume` is no longer an alias for unpausing — it must be called explicitly to
  resume playback.

**Fixed**
~~~~~~~~~

- Fixed incorrect generics on the :class:`PycordPlayer <.adapters._pycord.PycordPlayer>`. (:gh-commit:`684bdc9`)
- Fixed ``force`` parameter handling in :meth:`Player.disconnect <._base.BasePlayer.disconnect>`. (:gh-commit:`ca44cad`)
- Fixed the library raising :class:`QueueEmpty <sonolink.QueueEmpty>` when skipping tracks for the user internally.
  (:gh-commit:`5e4dbed`)

**Miscellaneous**
~~~~~~~~~~~~~~~~~

- :class:`sonolink.gateway.Node <sonolink.gateway.node.Node>` has been split into multiple components internally for
  better separation of concerns and maintainability. This is not a breaking change as the
  public API remains the same, but it should improve code readability and future extensibility. (:gh-issue:`33`)
- Formatted the project with `Ruff <https://docs.astral.sh/ruff/>`_ for consistent code style and linting. (:gh-issue:`35`)

.. _vp1p0p1:

v1.0.1 - 2026-04-12
-------------------

**Fixed**
~~~~~~~~~
- Inconsistent environment variable usage across code and documentation. (:gh-issue:`22`)
- Fixed performance and memory issue in PlayerFactory caused by repeated metadata scans (:gh-issue:`22`):

  - Reduced connection time (~11x faster)
  - Reduced memory peak (~12x lower)
  - Eliminated repeated expensive ``importlib.metadata.packages_distributions()`` calls

.. _vp1p0p0:

v1.0.0 - 2026-04-11
-------------------

Initial release. For more information on what this added, consider referring to the API Reference or the examples.

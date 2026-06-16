.. currentmodule:: sonolink

Gateway API
===========

The gateway layer contains the queue, enum, error, and event-related runtime types.
The top-level :class:`sonolink.Client`, :class:`sonolink.Node`, and :class:`sonolink.Player`
classes are documented on :doc:`/api/core`.

Region-aware node selection
---------------------------

You can create nodes without any region metadata. Those nodes use the normal penalty-based
selection path:

.. code-block:: python

   client = sonolink.Client(bot)

   client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       id="default",
   )

Pass ``regions`` to :meth:`~sonolink.Client.create_node` when you want new players to prefer
Lavalink nodes near the Discord voice channel's region. The built-in discord.py, py-cord,
disnake, and nextcord players read ``channel.rtc_region`` during connection. If the channel
has no explicit region, or no connected node matches that region, SonoLink falls back to
penalty-based node selection across all connected nodes.

``regions`` accepts :class:`NodeRegion` values or raw Discord region strings. Raw strings are
useful when Discord introduces a region before SonoLink adds a matching enum member.

.. code-block:: python

   client = sonolink.Client(bot)

   client.create_node(
       uri="http://us-east.example.com:2333",
       password="youshallnotpass",
       id="us-east",
       regions=[sonolink.NodeRegion.US_EAST, sonolink.NodeRegion.US_CENTRAL],
   )

   client.create_node(
       uri="http://rotterdam.example.com:2333",
       password="youshallnotpass",
       id="rotterdam",
       regions=[sonolink.NodeRegion.ROTTERDAM],
   )

   client.create_node(
       uri="http://fallback.example.com:2333",
       password="youshallnotpass",
       id="fallback",
   )

   client.create_node(
       uri="http://custom.example.com:2333",
       password="youshallnotpass",
       id="custom",
       regions=[sonolink.NodeRegion.US_EAST, "custom-region"],
   )

For operations that choose a node without a connected player, pass an explicit ``region`` to
:meth:`~sonolink.Client.get_best_node`, :meth:`~sonolink.Client.search_track`,
:meth:`~sonolink.Client.decode_track`, or :meth:`~sonolink.Client.decode_tracks`.

Voice state
-----------

.. autoclass:: sonolink.PlayerConnectionState
   :members:   


Websocket payloads
------------------

.. autoclass:: sonolink.gateway.schemas.PlayerState
   :members:

.. autoclass:: sonolink.gateway.schemas.MemoryStats
   :members:

.. autoclass:: sonolink.gateway.schemas.CPUStats
   :members:
   
.. autoclass:: sonolink.gateway.schemas.FrameStats
   :members:

.. autoclass:: sonolink.gateway.schemas.StatsEvent
   :members:

.. autoclass:: sonolink.gateway.schemas.WebSocketClosedEvent
   :members:   

Library adapters
----------------

These classes are the concrete :class:`~sonolink.Player` implementations for each
supported Discord library. You will not normally instantiate them directly —
:class:`~sonolink.Player` resolves the correct adapter automatically at runtime via
the ``SONOLINK_FRAMEWORK`` environment variable. They are documented here for
completeness and for users who need to type-annotate their voice channel references
precisely.

All three classes inherit the full public API of :class:`~sonolink.player.BasePlayer`
(playback, queue, filters, volume, etc.) in addition to the members listed below.

.. autoclass:: sonolink.gateway.player._base.BasePlayer
   :members:

.. autoclass:: sonolink.gateway.player.adapters._dpy.DpyPlayer
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: sonolink.gateway.player.adapters._pycord.PycordPlayer
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: sonolink.gateway.player.adapters._disnake.DisnakePlayer
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: sonolink.gateway.player.adapters._nextcord.NextcordPlayer
   :members:
   :inherited-members:
   :show-inheritance:

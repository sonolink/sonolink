.. currentmodule:: sonolink

SonoLink Documentation
======================

SonoLink is a high-performance Lavalink v4 wrapper for Python, inspired by WaveLink.
It provides a high-level voice player API while still exposing the underlying node,
model, REST, and gateway primitives when you need them.

It is designed for bot authors who want a practical, queue-first player interface out of
the box, without losing access to the runtime types and protocol details needed for
debugging, customisation, or more advanced workflows.

.. _framework-compatibility:

Framework Compatibility
-----------------------

SonoLink is compatible with **discord.py 2.7+**, **py-cord 2.8+**, **disnake 2.12+** and **nextcord 3.1.1+**,
and requires no additional Discord library dependency — it automatically detects whichever
you have installed. If multiple are found and none has already been imported, one is selected 
automatically and a warning is logged.

.. important::
   SonoLink targets **Lavalink 4.x**. See :doc:`/guides/lavalink-setup` for instructions on
   setting up and self-hosting a Lavalink server.

Getting Started
---------------

.. toctree::
   :maxdepth: 1
   :caption: Main

   installation
   guides/index
   api/index

.. toctree::
   :maxdepth: 1
   :caption: Meta

   changelog
   version_guarantees

Who should read what
--------------------

* **New users** — start with :doc:`installation`, then read :doc:`guides/getting-started`.
* **Advanced users** — jump straight to :doc:`api/index` and refer to the guides as needed.

Typical flow
------------

1. Create a :class:`sonolink.Client` attached to your Discord client.

   Pass ``framework`` explicitly if multiple Discord libraries are installed in the same environment.
2. Register one or more Lavalink nodes with :meth:`sonolink.Client.create_node`.
3. Start the SonoLink client once your Discord client is ready.
4. Connect to a voice channel using :class:`sonolink.Player`.
5. Search for tracks, populate the queue, and begin playback.

Core pieces
-----------

The public API is easiest to understand from the outside in:

* :class:`sonolink.Client` — attached to your Discord client; owns all nodes and
  acts as the main entry point.
* :class:`sonolink.Node` — represents a single Lavalink server connection.
* :class:`sonolink.Player` — the Discord voice protocol implementation used per guild.
* :doc:`sonolink.models <api/models>` — user-facing objects including tracks, playlists,
  search results, and settings.

License
-------

SonoLink is released under the `Apache License 2.0 <https://github.com/sonolink/sonolink/blob/main/LICENSE>`_.

Resources
---------

* `GitHub repository <https://github.com/sonolink/sonolink>`_
* `PyPI package <https://pypi.org/project/sonolink/>`_
* `Discord community <https://discord.gg/tPHVWBPedt>`_

Credits
-------

* `Paillat-dev <https://github.com/Paillat-dev>`_ for the
  `content width selector <https://github.com/Pycord-Development/pycord/pull/3040>`_.
* `Rapptz <https://github.com/Rapptz>`_ for the original
  `attributetable Sphinx extension <https://github.com/Rapptz/discord.py/blob/master/docs/extensions/attributetable.py>`_.

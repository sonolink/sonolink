<div align="center">

![SonoLink](https://raw.githubusercontent.com/sonolink/sonolink/main/docs/_static/images/banner.png)

A high-performance Lavalink v4 wrapper for Python, inspired by [WaveLink](https://github.com/PythonistaGuild/Wavelink).

[Documentation](https://sonolink.readthedocs.io/en/latest) · [Discord Server](https://discord.gg/tPHVWBPedt)

[![PyPI](https://img.shields.io/pypi/v/sonolink)](https://pypi.org/project/sonolink)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org)
[![Lavalink](https://img.shields.io/badge/lavalink-4.x-orange)](https://lavalink.dev)
[![License](https://img.shields.io/github/license/sonolink/sonolink)](LICENSE)
[![Discord](https://img.shields.io/discord/1471146455002775624?label=discord)](https://discord.gg/tPHVWBPedt)

</div>

---

## Features

- Full Lavalink v4+ REST API support
- Built on [msgspec](https://github.com/jcrist/msgspec) for rapid serialization and strict type validation
- Optional [curl_cffi](https://github.com/lexiforest/curl_cffi) for faster networking
- Async-first and [Basedpyright](https://docs.basedpyright.com/latest/) strict-compliant
- Multi-library native support for [discord.py](https://github.com/Rapptz/discord.py), [py-cord](https://github.com/Pycord-Development/pycord), [disnake](https://github.com/DisnakeDev/disnake), and [nextcord](https://github.com/nextcord/nextcord)

## Documentation

The full documentation is available at https://sonolink.readthedocs.io/en/latest. It includes guides on getting started, Lavalink setup and moving from other libraries, as well as a comprehensive API reference.

Examples may be found in the [examples](https://github.com/sonolink/sonolink/tree/main/examples) directory.

## Installation

> [!NOTE]
> A [virtual environment](https://docs.python.org/3/library/venv.html) is recommended, especially on Linux where the system Python may restrict package installations.
> 
### Requirements:
- Python 3.12 or higher
- A running Lavalink 4.x server ([guide on setup](https://sonolink.readthedocs.io/en/latest/guides/lavalink-setup.html))
- One of the following discord libraries with the `[voice]` extra:
  - [discord.py](https://pypi.org/project/discord.py) 2.7+
  - [py-cord](https://pypi.org/project/py-cord) 2.8+
  - [disnake](https://pypi.org/project/disnake) 2.12+
  - [nextcord](https://pypi.org/project/nextcord) 3.2+
  
### Install

**Stable** (recommended):
```sh
pip install -U sonolink # basic
pip install -U "sonolink[speed]" # optional speed improvements
```

**Development** (latest from GitHub):
```sh
pip install -U "sonolink @ git+https://github.com/sonolink/sonolink" # basic
pip install -U "sonolink[speed] @ git+https://github.com/sonolink/sonolink" # optional speed improvements
```

> [!TIP]
> On Linux/macOS use `python3 -m pip`, on Windows use `py -3 -m pip` if `pip` isn't on your PATH.

## Contributors
This project wouldn't be possible without the dedication and support of our contributors.  
<br>
![Contributors](https://contributors-table.vercel.app/image?repo=sonolink/sonolink&width=50&columns=15)

<br>

<p align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/footers/gray0_ctp_on_line.svg?sanitize=true" />
</p>

<p align="center">
        <i><code>&copy 2026 <a href="https://github.com/sonolink">SonoLink Development Team</a></code></i>
</p>

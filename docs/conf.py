import datetime
import sys
from pathlib import Path

from sonolink import __version__

ROOT = Path(__file__).resolve().parents[1]
DOCS_PATH = ROOT / "docs"
sys.path.insert(0, str(ROOT))
sys.path.append(str(DOCS_PATH / "extensions"))


# -- Project information --
project = "sonolink"
author = "vmphase, Soheab, DA-344"
copyright = f"{datetime.date.today().year}, {author}"
release = __version__

# -- General configuration --
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx.ext.viewcode",
    "attributetable",
    "navigationhome",
    "pythonref",
]

# Intersphinx link to standard Python docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "discord": ("https://discordpy.readthedocs.io/en/stable/", None),
    "pycord": ("https://docs.pycord.dev/en/master/", None),
    "disnake": ("https://docs.disnake.dev/en/stable/", None),
    "nextcord": ("https://docs.nextcord.dev/en/stable/", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "curl_cffi": ("https://curl-cffi.readthedocs.io/en/stable/", None),
    "msgspec": ("https://msgspec.dev/", None),
}

exclude_patterns = [
    "_build",
]
nitpick_ignore_regex = [
    ("py:class", r"(N|D|P|T|T_co|~P|SessionType|WSErrorType|type\[N\])"),
    ("py:class", r"dict\[str"),
    ("py:class", r"sonolink\.errors\.SonoLinkException"),
    ("py:class", r"sonolink\.gateway\.errors\.NodeError"),
    ("py:class", r"sonolink\.models\.base\.(BaseModel|BaseSettings)"),
    ("py:class", r"sonolink\.network\.base\.(BaseHTTPManager|BaseWebsocketManager)"),
    ("py:class", r"sonolink\.rest\.http\..+"),
    ("py:class", r"sonolink\.gateway\.queue\.base\..+"),
    ("py:class", r"sonolink\.gateway\.events\..+"),
    ("py:class", r"sonolink\.utils\.properties\.(T|T_co|_cached_property)"),
]

# -- Options for autodoc --
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "inherited-members": True,
}
autodoc_mock_imports = ["discord", "py-cord", "disnake", "nextcord"]
autodoc_typehints = "both"
autodoc_class_signature = "mixed"
napoleon_preprocess_types = True
autodoc_member_order = "groupwise"
autodoc_typehints_description_target = "documented"

# -- Options for HTML output --
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = [
    f"css/{path.name}" for path in sorted((DOCS_PATH / "_static" / "css").iterdir())
]
html_js_files = [
    f"js/{path.name}" for path in sorted((DOCS_PATH / "_static" / "js").iterdir())
]
html_title = f"{project} {release} documentation"
html_favicon = "_static/images/logo.svg"
templates_path = ["_templates"]

html_theme_options = {
    "light_logo": "images/logo.svg",
    "dark_logo": "images/logo.svg",
    "sidebar_hide_name": True,
    "light_css_variables": {
        "color-brand-primary": "#d8ad37",
        "color-brand-content": "#2f6c95",
        "color-brand-visited": "#7f5ba6",
        "color-api-name": "#2f6c95",
        "color-api-pre-name": "#2f6c95",
        "color-topic-title": "#d8ad37",
        "color-topic-title-background": "rgba(216, 173, 55, 0.16)",
        "color-admonition-title": "#d8ad37",
        "color-admonition-title-background": "rgba(216, 173, 55, 0.14)",
        "color-sidebar-background": "#f4f7fb",
        "color-sidebar-background-border": "#d9e1ec",
        "color-sidebar-brand-text": "#102131",
        "color-sidebar-link-text": "#40576c",
        "color-sidebar-link-text--top-level": "#2f6c95",
        "color-sidebar-item-background--current": "rgba(47, 108, 149, 0.10)",
        "color-sidebar-item-expander-background--hover": "rgba(47, 108, 149, 0.10)",
        "color-sidebar-search-background": "#edf2f8",
        "color-sidebar-search-background--focus": "#ffffff",
        "color-sidebar-search-border": "#d0dae6",
        "color-link": "#2f6c95",
        "color-link--hover": "#255577",
        "color-link--visited": "#7f5ba6",
        "color-toc-item-text--active": "#2f6c95",
        "color-foreground-primary": "#162432",
        "color-foreground-secondary": "#4f6273",
        "color-foreground-muted": "#69798a",
        "color-background-primary": "#fcfcfa",
        "color-background-secondary": "#f6f8fb",
        "color-background-hover": "#e8eef5",
        "color-background-border": "#dde4ec",
        "color-card-border": "#e1e7ef",
        "color-card-background": "rgba(255, 255, 255, 0.86)",
        "color-admonition-background": "rgba(255, 255, 255, 0.84)",
    },
    "dark_css_variables": {
        "color-brand-primary": "#d8ad37",
        "color-brand-content": "#69a7d1",
        "color-brand-visited": "#c29df2",
        "color-api-name": "#8ec5ea",
        "color-api-pre-name": "#8ec5ea",
        "color-topic-title": "#d8ad37",
        "color-topic-title-background": "rgba(216, 173, 55, 0.18)",
        "color-admonition-title": "#d8ad37",
        "color-admonition-title-background": "rgba(216, 173, 55, 0.16)",
        "color-sidebar-background": "#0f1720",
        "color-sidebar-background-border": "#1f2e3d",
        "color-sidebar-brand-text": "#f1f4f7",
        "color-sidebar-caption-text": "#7b92a6",
        "color-sidebar-link-text": "#afbcc8",
        "color-sidebar-link-text--top-level": "#8ec5ea",
        "color-sidebar-item-background--current": "rgba(105, 167, 209, 0.14)",
        "color-sidebar-item-expander-background--hover": "rgba(105, 167, 209, 0.12)",
        "color-sidebar-search-background": "#13202c",
        "color-sidebar-search-background--focus": "#1a2a38",
        "color-sidebar-search-border": "#24384a",
        "color-link": "#7fb8dd",
        "color-link--hover": "#a4d0ec",
        "color-link--visited": "#c29df2",
        "color-toc-item-text--active": "#8ec5ea",
        "color-foreground-primary": "#dbe4eb",
        "color-foreground-secondary": "#a8b5c0",
        "color-foreground-muted": "#7f8d99",
        "color-foreground-border": "#566675",
        "color-background-primary": "#13181f",
        "color-background-secondary": "#192028",
        "color-background-hover": "#1d2731",
        "color-background-border": "#273342",
        "color-card-border": "#202a33",
        "color-card-background": "rgba(22, 27, 34, 0.88)",
        "color-admonition-background": "rgba(20, 25, 31, 0.90)",
        "color-problematic": "#f07c6b",
        "color-highlighted-background": "#14314a",
    },
}

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/width-selector.html",
        "sidebar/scroll-end.html",
        "sidebar/variant-selector.html",
    ]
}

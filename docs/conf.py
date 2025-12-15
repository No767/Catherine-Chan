from pathlib import Path

from matplotlib import font_manager
from matplotlib.font_manager import FontProperties


def determine_font() -> str:
    fonts_path = Path("_static/fonts/Outfit-SemiBold.ttf")

    if not fonts_path.exists():
        fonts_path = Path("docs/_static/fonts/Outfit-SemiBold.ttf")

    font_manager.fontManager.addfont(fonts_path)
    properties = FontProperties(family="sans-serif", fname=fonts_path)
    return properties.get_name()


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Catherine-Chan"
copyright = "2024-Present, No767"
author = "No767"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx_design", "sphinxext.opengraph"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_title = "Catherine-Chan"

# -- Open Graph (OGP) options ------------------------------------------------
# https://sphinxext-opengraph.readthedocs.io/en/latest/

ogp_site_name = "Catherine-Chan Documentation"
ogp_description_length = 130
ogp_type = "website"

ogp_custom_meta_tags = [
    '<link rel="icon" type="image/png" href="/_static/public/favicon-96x96.png" sizes="96x96" />'
    '<link rel="icon" type="image/svg+xml" href="/_static/public/favicon.svg" />',
    '<link rel="shortcut icon" href="/_static/public/favicon.ico" />',
    '<link rel="apple-touch-icon" sizes="180x180" href="/_static/public/apple-touch-icon.png" />',
    '<meta name="apple-mobile-web-app-title" content="Catherine-Chan Documentation" />',
    '<link rel="manifest" href="/_static/public/site.webmanifest" />',
]


ogp_social_cards = {
    "enable": True,
    "image": "./_images/pride.png",
    "line_color": "#FFABE1",
    "font": determine_font(),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "dark_css_variables": {
        "color-brand-primary": "#ffbdea",
        "color-brand-content": "#a9edfe",
    },
    "light_css_variables": {
        "color-brand-primary": "#ff38c0",
        "color-brand-content": "#2cd3fd",
    },
}

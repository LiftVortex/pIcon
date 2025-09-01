import sys
from typing import Dict

# Radii, spacing, elevation
RADIUS = 10  # px
SPACING = 8  # 8/12 grid
ELEVATION_SHADOW = "0 4 16 #00000020"  # not native in Tk; used for reference

TYPOGRAPHY = {
    "font_main": "Segoe UI Variable 10",
    "font_fallback": "Segoe UI 10",
    "font_mono": "Consolas 10",
}

# Color palettes for light/dark
LIGHT_COLORS: Dict[str, str] = {
    "bg": "#f6f6f6",
    "bg_mica_top": "#f6f6f6",
    "bg_mica_bottom": "#eaeaea",
    "card": "#ffffff",
    "text": "#1c1c1c",
    "muted": "#6b6b6b",
    "outline": "#dedede",
    "checker_dark": "#e6e6e6",
    "checker_light": "#ffffff",
    "banner_info": "#e8f2ff",
    "banner_warn": "#fff4db",
    "banner_error": "#ffebeb",
}

DARK_COLORS: Dict[str, str] = {
    "bg": "#1b1b1b",
    "bg_mica_top": "#1b1b1b",
    "bg_mica_bottom": "#202020",
    "card": "#262626",
    "text": "#f2f2f2",
    "muted": "#a0a0a0",
    "outline": "#363636",
    "checker_dark": "#1f1f1f",
    "checker_light": "#2a2a2a",
    "banner_info": "#0d2744",
    "banner_warn": "#3d2f10",
    "banner_error": "#3a0f0f",
}

def get_colors(is_light: bool) -> Dict[str, str]:
    return LIGHT_COLORS if is_light else DARK_COLORS

"""Core scaffolding for AccessiClock wxPython app."""

from .settings import AppSettings, load_settings, save_settings
from .shortcuts import Shortcut, build_shortcut_help, default_shortcuts

__all__ = [
    "AppSettings",
    "Shortcut",
    "build_shortcut_help",
    "default_shortcuts",
    "load_settings",
    "save_settings",
]

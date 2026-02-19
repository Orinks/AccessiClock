"""Keyboard shortcut map for AccessiClock UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Shortcut:
    keys: str
    action: str


def default_shortcuts() -> list[Shortcut]:
    """Return current keyboard shortcut map."""
    return [
        Shortcut("F5", "Test chime"),
        Shortcut("Space", "Announce current time"),
        Shortcut("Ctrl+,", "Open settings"),
        Shortcut("Alt+F4", "Exit application"),
        Shortcut("Tab / Shift+Tab", "Move focus between controls"),
    ]


def build_shortcut_help() -> str:
    """Create readable help text for the status line / docs."""
    return " | ".join(f"{s.keys}: {s.action}" for s in default_shortcuts())

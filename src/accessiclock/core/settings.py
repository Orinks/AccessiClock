"""Settings I/O and simple validation for AccessiClock."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class AppSettings:
    """Persistent user settings used by the app."""

    volume: int = 50
    clock: str = "default"
    chime_hourly: bool = True
    chime_half_hour: bool = False
    chime_quarter_hour: bool = False
    quiet_hours_enabled: bool = False
    quiet_start: str = "22:00"
    quiet_end: str = "07:00"

    @classmethod
    def from_dict(cls, raw: dict) -> AppSettings:
        """Build settings from plain dict with safe defaults."""
        settings = cls(
            volume=_clamp_volume(raw.get("volume", 50)),
            clock=str(raw.get("clock", "default") or "default"),
            chime_hourly=bool(raw.get("chime_hourly", True)),
            chime_half_hour=bool(raw.get("chime_half_hour", False)),
            chime_quarter_hour=bool(raw.get("chime_quarter_hour", False)),
            quiet_hours_enabled=bool(raw.get("quiet_hours_enabled", False)),
            quiet_start=str(raw.get("quiet_start", "22:00")),
            quiet_end=str(raw.get("quiet_end", "07:00")),
        )
        return settings

    def to_dict(self) -> dict:
        """Serialize settings to plain dict."""
        return asdict(self)


def _clamp_volume(value: object) -> int:
    try:
        return max(0, min(100, int(value)))
    except (TypeError, ValueError):
        return 50


def load_settings(config_file: Path) -> AppSettings:
    """Load settings from config file. Returns defaults on errors."""
    if not config_file.exists():
        return AppSettings()

    try:
        with open(config_file, encoding="utf-8") as handle:
            return AppSettings.from_dict(json.load(handle))
    except (OSError, json.JSONDecodeError, TypeError):
        return AppSettings()


def save_settings(config_file: Path, settings: AppSettings) -> None:
    """Save settings to disk, creating parent directories as needed."""
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as handle:
        json.dump(settings.to_dict(), handle, indent=2)

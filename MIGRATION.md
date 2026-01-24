# AccessiClock: Toga → wxPython Migration

## Overview

Migrating from Toga/BeeWare to wxPython for consistency with AccessiWeather and better accessibility support.

## Current State (Toga)
- `accessibletalkingclock/` - Briefcase app structure
- `src/accessibletalkingclock/app.py` - Main Toga application
- `src/accessibletalkingclock/audio/player.py` - AudioPlayer with sound_lib

## Target State (wxPython)
Following AccessiWeather's architecture exactly.

## New Project Structure

```
AccessiClock/
├── src/
│   └── accessiclock/
│       ├── __init__.py
│       ├── __main__.py
│       ├── main.py                    # Entry point
│       ├── app.py                     # wx.App subclass
│       ├── paths.py                   # Path management
│       ├── constants.py               # App constants
│       ├── config.py                  # Configuration management
│       │
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py         # Main clock window
│       │   ├── system_tray.py         # System tray icon
│       │   └── dialogs/
│       │       ├── __init__.py
│       │       ├── settings_dialog.py
│       │       ├── clock_manager_dialog.py    # Like soundpack_manager
│       │       ├── community_clocks_dialog.py
│       │       └── alarm_dialog.py
│       │
│       ├── clocks/                    # Clock packs (like soundpacks/)
│       │   ├── default/
│       │   │   ├── clock.json
│       │   │   └── *.wav
│       │   ├── westminster/
│       │   └── digital/
│       │
│       ├── audio/
│       │   ├── __init__.py
│       │   ├── player.py              # Keep sound_lib player
│       │   ├── clock_player.py        # Clock-specific playback logic
│       │   └── tts_engine.py          # Text-to-speech (SAPI + AI)
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── clock_service.py       # Time tracking, chime scheduling
│       │   ├── alarm_service.py       # Alarms and timers
│       │   └── community_clock_service.py
│       │
│       └── notifications/
│           ├── __init__.py
│           ├── clock_installer.py     # Install clock packs
│           └── toast_notifier.py
│
├── installer/                         # PyInstaller config
├── tests/
├── pyproject.toml
├── README.md
└── MIGRATION.md
```

## Migration Phases

### Phase M1: Project Scaffolding ✅
- [x] Create new directory structure
- [x] Set up pyproject.toml with wxPython deps
- [x] Create basic app.py and main_window.py
- [x] Port AudioPlayer (mostly unchanged)

### Phase M2: Core Clock UI
- [ ] Main window with clock display
- [ ] Time update loop (wx.Timer instead of asyncio)
- [ ] Basic controls (volume, test chime)
- [ ] Screen reader accessibility testing

### Phase M3: Clock Pack System
- [ ] Create clock.json schema
- [ ] Clock pack loader
- [ ] Clock selection dropdown
- [ ] Preview functionality

### Phase M4: Settings & Persistence
- [ ] Settings dialog with tabs
- [ ] JSON config file
- [ ] Remember window position

### Phase M5: TTS Integration
- [ ] SAPI5 wrapper for Windows TTS
- [ ] Time announcement formats
- [ ] Voice selection

### Phase M6: System Tray
- [ ] Tray icon with menu
- [ ] Click to announce time
- [ ] Minimize to tray option

## Key Differences: Toga vs wxPython

| Toga | wxPython |
|------|----------|
| `toga.App` | `wx.App` |
| `toga.MainWindow` | `wx.Frame` / `SizedFrame` |
| `toga.Button` | `wx.Button` |
| `toga.Selection` | `wx.ComboBox` |
| `toga.Switch` | `wx.CheckBox` |
| `toga.TextInput` | `wx.TextCtrl` |
| `add_background_task()` | `wx.Timer` or `threading` |
| `Pack` styles | `wx.BoxSizer` |

## Dependencies

```toml
dependencies = [
    "wxPython>=4.2.0",
    "playsound3",           # Simple audio playback
    "pyttsx3",              # SAPI5 TTS wrapper
    "httpx>=0.20.0",        # For community clocks
    "attrs>=22.2.0",        # Data classes
]
```

## What to Keep

- **AudioPlayer** (`audio/player.py`) - Works fine, just import path changes
- **Roadmap** - Still valid
- **Test audio file** - Reuse

## What to Remove

- `accessibletalkingclock/` (entire Briefcase structure)
- Briefcase configs
- Toga-specific code

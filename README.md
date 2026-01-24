# AccessiClock

An accessible talking clock application designed for visually impaired users, featuring customizable clock packs, TTS announcements, and AI voice support.

Built with wxPython for native Windows accessibility and screen reader compatibility.

## Features

### ✅ Implemented
- **Large Digital Clock Display**: Easy-to-read time display with automatic updates
- **Full Keyboard Navigation**: Tab through all controls with logical focus order
- **Screen Reader Accessible**: Works with NVDA, JAWS, and Windows Narrator
- **Volume Control**: Adjustable audio volume
- **Chime Configuration**: Enable/disable hourly, half-hour, and quarter-hour chimes
- **Test Functionality**: Preview clock sounds

### 🔄 Planned
- **Clock Packs**: Customizable sound themes (Westminster, Nature, Digital, etc.)
- **TTS Announcements**: Speak the time using Windows SAPI or AI voices
- **AI Voices**: ElevenLabs and OpenAI TTS integration
- **Community Clocks**: Browse and install clock packs from GitHub
- **Alarms & Timers**: Set reminders and countdown timers
- **System Tray**: Minimize to tray with quick access

## Installation

### Requirements
- Windows 10 or later
- Python 3.10 or higher

### From Source

```bash
# Clone the repository
git clone https://github.com/orinks/AccessiClock.git
cd AccessiClock

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Run the application
python -m accessiclock
```

### Quick Start (Windows)
```powershell
.\start.ps1
```

## Usage

### Keyboard Shortcuts
- **Tab**: Navigate between controls
- **Space**: Announce current time
- **F5**: Test current chime
- **Alt+V**: Change volume
- **Ctrl+,**: Open settings

### Clock Packs

Clock packs are located in the `clocks/` directory. Each pack contains:
- `clock.json` - Manifest with metadata
- Audio files for different chimes (hour, half-hour, etc.)

## Project Structure

```
AccessiClock/
├── src/accessiclock/
│   ├── app.py              # Main wxPython application
│   ├── main.py             # Entry point
│   ├── constants.py        # App constants
│   ├── paths.py            # Path management
│   ├── ui/
│   │   ├── main_window.py  # Main clock window
│   │   └── dialogs/        # Settings, clock manager, etc.
│   ├── audio/
│   │   └── player.py       # Audio playback (sound_lib)
│   ├── clocks/             # Clock pack resources
│   └── services/           # Background services
├── tests/
├── pyproject.toml
└── README.md
```

## Accessibility

This application prioritizes accessibility:

- ✅ **Screen Reader Compatible**: Native Windows widgets for NVDA/JAWS/Narrator
- ✅ **Keyboard Navigation**: All features accessible via keyboard
- ✅ **Logical Tab Order**: Intuitive focus flow
- ✅ **Status Announcements**: Changes announced to assistive technology

## Technology Stack

- **Framework**: [wxPython](https://wxpython.org/) 4.2+
- **Audio**: [sound_lib](https://github.com/accessibleapps/sound_lib) (BASS wrapper)
- **TTS**: pyttsx3 (SAPI5) + optional AI voices
- **Packaging**: PyInstaller

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Style
```bash
ruff check src/
ruff format src/
```

## Roadmap

See [MIGRATION.md](MIGRATION.md) for detailed migration status and future plans.

### Phases
1. ✅ Core UI with accessibility (wxPython)
2. 🔄 Clock pack system
3. ⏳ TTS integration
4. ⏳ Settings persistence
5. ⏳ Community clocks
6. ⏳ AI voice support
7. ⏳ Installer & distribution

## Contributing

Contributions welcome! Please ensure:
- All UI elements maintain accessibility compliance
- Screen reader compatibility is tested with NVDA
- Code follows ruff formatting

## License

MIT License - See LICENSE file for details.

## Credits

Inspired by Steve's Talking Clock and built for the accessibility community.

---

*Part of the Accessi* suite of accessible applications.*

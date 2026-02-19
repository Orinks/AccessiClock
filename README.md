# AccessiClock 🕐

An accessible talking clock application designed for visually impaired users, built with wxPython for native Windows accessibility support.

## Features

- **Screen Reader Accessible**: Fully compatible with NVDA, JAWS, and Windows Narrator
- **Customizable Chimes**: Hourly, half-hour, and quarter-hour chime options
- **Clock Packs**: Switchable clock sound themes (Default, Digital, Westminster)
- **Text-to-Speech**: Announces time on demand with customizable voice settings
- **Quiet Hours**: Automatically silence chimes during specified times
- **Portable Mode**: Run from USB drive without installation

## Screenshot

```
┌─────────────────────────────────────────┐
│ AccessiClock                        _ □ X│
├─────────────────────────────────────────┤
│ Current Time:                           │
│ ┌─────────────────────────────────────┐ │
│ │           3:45:30 PM                │ │
│ └─────────────────────────────────────┘ │
│ Ready. Use Tab to navigate controls.    │
│                                         │
│ Clock: [Default        ▼]               │
│ Volume: 50%        [Change Volume]      │
│                                         │
│ Chime Intervals:                        │
│ [✓] Hourly chimes                       │
│ [ ] Half-hour chimes                    │
│ [ ] Quarter-hour chimes                 │
│                                         │
│ [Test Chime] [Announce Time] [Settings] │
└─────────────────────────────────────────┘
```

## Installation

### Requirements

- Python 3.10 or higher
- Windows 10/11 (primary), Linux/macOS (limited support)

### From Source

```bash
# Clone the repository
git clone https://github.com/orinks/AccessiClock.git
cd AccessiClock

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -e .

# Run the application
python -m accessiclock
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space | Announce current time |
| F5 | Test chime sound |
| Tab | Navigate between controls |
| Ctrl+, | Open settings |
| Alt+F4 | Exit application |

### Clock Packs

AccessiClock includes three built-in clock packs:

- **Default**: Pleasant melodic chimes
- **Digital**: Simple electronic beeps
- **Westminster**: Classic Westminster-style chimes

You can also import custom clock packs or create your own.

### Creating Custom Clock Packs

A clock pack is a folder containing:

```
my_clock_pack/
├── clock.json      # Manifest file (required)
├── hour.wav        # Hourly chime sound
├── half_hour.wav   # Half-hour chime sound
├── quarter_hour.wav # Quarter-hour chime sound
├── preview.wav     # Preview/test sound
└── startup.wav     # Startup sound (optional)
```

Example `clock.json`:

```json
{
  "name": "My Custom Clock",
  "author": "Your Name",
  "description": "A custom clock pack.",
  "version": "1.0.0",
  "sounds": {
    "hour": "hour.wav",
    "half_hour": "half_hour.wav",
    "quarter_hour": "quarter_hour.wav",
    "preview": "preview.wav"
  }
}
```

## Configuration

Settings are stored in:
- Windows: `%APPDATA%\AccessiClock\config.json`
- Linux: `~/.config/AccessiClock/config.json`
- Portable mode: `./data/config.json`

## Migration Notes

- Current migration parity checklist: `docs/wxpython-migration-parity-checklist.md`

## Development

### Running Tests

```bash
# Run all tests
PYTHONPATH=src pytest tests/ -v

# Run with coverage
PYTHONPATH=src pytest tests/ --cov=accessiclock
```

### Project Structure

```
AccessiClock/
├── src/accessiclock/
│   ├── __init__.py
│   ├── app.py              # Main application class
│   ├── main.py             # Entry point
│   ├── constants.py        # Application constants
│   ├── paths.py            # Path management
│   ├── audio/
│   │   ├── player.py       # Audio playback
│   │   └── tts_engine.py   # Text-to-speech
│   ├── services/
│   │   ├── clock_service.py     # Chime scheduling
│   │   └── clock_pack_loader.py # Clock pack management
│   ├── clocks/             # Built-in clock packs
│   │   ├── default/
│   │   ├── digital/
│   │   └── westminster/
│   └── ui/
│       ├── main_window.py  # Main window
│       └── dialogs/        # Settings & clock manager
├── tests/                  # Unit tests
├── scripts/                # Utility scripts
└── pyproject.toml         # Project configuration
```

### Generate Placeholder Sounds

```bash
python scripts/generate_sounds.py
```

## Accessibility

AccessiClock is designed with accessibility as a primary goal:

- All controls are keyboard accessible
- Logical tab order for screen reader navigation
- Status messages announced via accessible labels
- High contrast support (uses system colors)
- Large, readable clock display
- Native Windows widgets for automatic accessibility support

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Credits

- Built with [wxPython](https://wxpython.org/)
- TTS powered by [pyttsx3](https://pyttsx3.readthedocs.io/)
- Accessibility testing with [NVDA](https://www.nvaccess.org/)

## Support

- Report issues on [GitHub Issues](https://github.com/orinks/AccessiClock/issues)
- For accessibility feedback, please mention your screen reader and version

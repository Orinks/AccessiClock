# Accessible Talking Clock

A desktop clock application designed specifically for visually impaired users, featuring native Windows accessibility support and customizable soundpacks.

## Overview

This application provides an accessible, screen-reader-friendly clock with hourly chimes and customizable sound themes. Built with Toga (BeeWare), it uses native Windows widgets that work seamlessly with NVDA, JAWS, and Windows Narrator.

## Features

### ✅ Phase 1 - Complete
- **Large Digital Clock Display**: Easy-to-read time display with automatic updates
- **Full Keyboard Navigation**: Tab through all controls with logical focus order
- **Screen Reader Accessible**: Time display and all controls are accessible via Tab navigation
- **Native Windows Controls**: All UI elements use native widgets for maximum accessibility
- **Soundpack Selection**: Choose from Classic (Westminster), Nature, or Digital themes
- **Volume Control**: Cycle through volume levels (0-100%)
- **Interval Configuration**: Configure hourly, half-hour, and quarter-hour chimes
- **Status Feedback**: Real-time updates announced to screen readers
- **Test Functionality**: Preview soundpack before enabling

### 🔄 Planned Features
- **Phase 2**: Background audio system with sound_lib (accessible audio library) and threading
- **Phase 3**: Built-in soundpack audio files (Westminster chimes, nature sounds, digital beeps)
- **Phase 4**: Settings persistence and configuration dialog
- **Phase 5**: Digital/analog display toggle, advanced volume controls
- **Phase 6**: Windows executable packaging with Briefcase

## Project Structure

```
accessible_talking_clock/
├── .venv/                          # Python virtual environment
├── accessibletalkingclock/         # Briefcase application
│   ├── src/
│   │   └── accessibletalkingclock/
│   │       ├── app.py              # Main application code
│   │       ├── __init__.py
│   │       ├── __main__.py
│   │       └── resources/          # App resources
│   ├── tests/                      # Unit tests
│   ├── pyproject.toml              # Briefcase configuration
│   ├── start.ps1                   # Windows startup script
│   ├── start.sh                    # Unix/Linux startup script
│   └── README.md                   # Application-specific docs
├── plans/                          # Project planning documents
│   └── 2025-01-12_15-30-45_accessible-desktop-clock/
│       ├── plan.md                 # Full project specification
│       └── tasks.md                # Implementation tasks
└── README.md                       # This file
```

## Getting Started

### Prerequisites
- Windows 10 or later (primary platform)
- Python 3.8 or higher
- Screen reader (NVDA recommended for testing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd accessible_talking_clock
   ```

2. **Install uv (Python package manager)**
   ```powershell
   powershell -Command "Set-ExecutionPolicy RemoteSigned -scope CurrentUser -Force; iwr https://astral.sh/uv/install.ps1 -useb | iex"
   ```

3. **Set up virtual environment**
   ```bash
   uv venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

4. **Install dependencies**
   ```bash
   uv pip install briefcase toga sound_lib ipykernel matplotlib
   ```

### Running the Application

#### Using Startup Scripts (Recommended)
```powershell
cd accessibletalkingclock
.\start.ps1  # Windows
# or
./start.sh   # Linux/Mac
```

#### Manual Launch
```bash
cd accessibletalkingclock
python -m briefcase dev
```

## Accessibility

This application prioritizes accessibility:

- ✅ **Screen Reader Compatible**: Works with NVDA, JAWS, and Windows Narrator
- ✅ **Keyboard Navigation**: All features accessible via keyboard
- ✅ **Tab Order**: Logical focus flow through all controls
- ✅ **Native Widgets**: Uses platform-native controls for maximum compatibility
- ✅ **Status Announcements**: Changes are announced to assistive technology
- ✅ **Focus Indicators**: Clear visual and programmatic focus management

### Testing with NVDA

1. Download and install [NVDA](https://www.nvaccess.org/download/)
2. Start NVDA
3. Launch the Accessible Talking Clock
4. Use Tab key to navigate between controls
5. Verify all elements are announced properly
6. Test all buttons with Enter or Space keys

## Development

### Building from Source
```bash
cd accessibletalkingclock
python -m briefcase build
```

### Running Tests
```bash
cd accessibletalkingclock
pytest
```

### Code Structure
- `app.py`: Main application logic, UI layout, event handlers
- `pyproject.toml`: Briefcase configuration and dependencies
- `resources/`: Application icons and resources (audio files in Phase 3+)

## Technology Stack

- **Framework**: [Toga](https://beeware.org/project/projects/libraries/toga/) (BeeWare)
- **Packaging**: [Briefcase](https://beeware.org/project/projects/tools/briefcase/)
- **Audio**: [sound_lib](https://github.com/accessibleapps/sound_lib) - High-level wrapper around BASS audio library, specifically designed for accessible applications (Phase 2+)
- **Platform**: Native Windows widgets via WinForms
- **Accessibility**: Windows Accessibility APIs (automatic via native widgets)

## Roadmap

- [x] **Phase 1**: Core UI with accessibility (Complete)
- [ ] **Phase 2**: Audio playback system
- [ ] **Phase 3**: Soundpack implementation
- [ ] **Phase 4**: Settings persistence
- [ ] **Phase 5**: Advanced features and polish
- [ ] **Phase 6**: Distribution and packaging

## Contributing

Contributions are welcome! Please ensure:
- All UI elements maintain accessibility compliance
- Screen reader compatibility is tested with NVDA
- Code follows existing patterns and style
- New features include appropriate logging

## License

MIT License - See LICENSE file for details

## Credits

Built with [Memex](https://memex.tech)

Co-Authored-By: Memex <noreply@memex.tech>

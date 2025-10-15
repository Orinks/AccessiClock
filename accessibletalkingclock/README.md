# Accessible Talking Clock

A desktop clock application designed specifically for visually impaired users, built with native Windows accessibility support.

## Features

### Phase 1 - Complete ✅
- **Large Digital Clock Display**: Easy-to-read time display that updates every second
- **Screen Reader Compatible**: All controls work with NVDA, JAWS, and Windows Narrator
- **Keyboard Navigation**: Full Tab navigation support through all controls
- **Accessible Time Display**: Clock display is focusable and readable by screen readers
- **Soundpack Selection**: Choose from Classic (Westminster), Nature (Birds & Water), or Digital (Beeps) sound themes
- **Volume Control**: Cycle through volume levels (0%, 25%, 50%, 75%, 100%)
- **Interval Configuration**: Toggle chimes for hourly, half-hour, and quarter-hour intervals
- **Test Functionality**: Test button to preview current soundpack
- **Status Feedback**: Real-time status updates announced to screen readers

### Planned Features
- **Phase 2**: Background audio playback system with pygame
- **Phase 3**: Built-in soundpack audio files and playback
- **Phase 4**: Settings persistence and configuration dialog
- **Phase 5**: Digital/analog display modes and advanced accessibility features
- **Phase 6**: Packaged Windows executable with bundled resources

## Accessibility

This application was designed with accessibility as a primary concern:

- **Native Windows Controls**: Uses Toga/WinForms widgets that inherit Windows accessibility APIs
- **Tab Navigation**: Logical tab order through all interface elements
- **Screen Reader Support**: Compatible with NVDA, JAWS, and Windows Narrator
- **Keyboard Access**: All functionality available via keyboard
- **Status Announcements**: Changes and actions are announced to assistive technology
- **Focus Management**: Clear focus indicators and proper focus flow

## Getting Started

### Prerequisites
- Windows 10 or later
- Python 3.8 or later
- Screen reader (NVDA recommended for testing)

### Installation
1. Clone this repository
2. Set up virtual environment: `uv venv`
3. Activate environment: `.venv\Scripts\activate`
4. Install dependencies: `uv pip install briefcase toga pygame`

### Running the Application
Use the provided startup scripts:
- **Windows**: `.\start.ps1`
- **Cross-platform**: `.\start.sh`

Or run manually:
```bash
python -m briefcase dev
```

### Accessibility Testing
1. Start NVDA screen reader
2. Launch the application
3. Use Tab key to navigate between controls
4. Verify all elements are announced properly
5. Test all buttons and controls with Enter/Space keys

## Technical Details

- **Framework**: Toga (BeeWare) for cross-platform native GUI
- **Packaging**: Briefcase for distributable executables
- **Accessibility**: Native Windows accessibility APIs via WinForms
- **Threading**: Designed for background audio and timer threads (Phase 2+)

## Development Status

✅ **Phase 1 Complete**: Core UI with full accessibility support
🔄 **Phase 2 Next**: Audio system implementation
📋 **Phases 3-6**: Planned features and packaging

## Contributing

This project prioritizes accessibility compliance and follows WCAG guidelines. All contributions should maintain or improve accessibility features.

Generated with [Memex](https://memex.tech)
Co-Authored-By: Memex <noreply@memex.tech>
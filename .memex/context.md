# Accessible Talking Clock - Project Rules

## Project Overview
Desktop clock application designed specifically for visually impaired users using Toga (BeeWare) framework with native Windows accessibility support. The application prioritizes screen reader compatibility (NVDA, JAWS, Windows Narrator) and keyboard navigation.

## Technology Stack

### Core Framework
- **Toga (BeeWare)**: Cross-platform GUI framework using native widgets
- **Briefcase**: Application packaging and distribution tool
- **WinForms**: Native Windows widgets backend (toga-winforms)
- **Python 3.8+**: Programming language

### Package Management
- **uv**: Primary package manager (preferred over pip/poetry/conda)
- Virtual environment location: `.venv/` at project root
- Key dependencies: `briefcase`, `toga`, `sound_lib` (Phase 2+)

### Development Commands
```bash
# Running the application
cd accessibletalkingclock
python -m briefcase dev

# Using startup scripts
.\start.ps1  # Windows
./start.sh   # Unix/Linux
```

## Project Structure

### Directory Layout
```
accessible_talking_clock/           # Project root (Git repository here)
├── .venv/                         # Virtual environment
├── accessibletalkingclock/        # Briefcase application (created by briefcase new)
│   ├── src/accessibletalkingclock/
│   │   ├── app.py                # Main application logic
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── resources/            # Icons, sounds (Phase 3+)
│   ├── tests/
│   ├── pyproject.toml            # Briefcase configuration
│   ├── start.ps1                 # Windows startup script
│   └── start.sh                  # Unix startup script
└── plans/                         # Project planning documents
```

**CRITICAL**: Git repository is at `accessible_talking_clock/` root level, NOT inside the `accessibletalkingclock/` subdirectory.

## Accessibility Requirements (NON-NEGOTIABLE)

### UI Element Rules
1. **All UI elements MUST be keyboard accessible via Tab navigation**
2. **All controls MUST use native Windows widgets** (no custom rendered controls)
3. **Time display MUST be in Tab order** - use `toga.TextInput(readonly=True)` NOT `toga.Label`
4. **Status feedback MUST be provided** via status labels that screen readers announce
5. **Focus order MUST be logical** - top to bottom, left to right

### Known Patterns
- **Clock Display**: Use `TextInput(readonly=True)` for accessibility, not `Label`
  - Update with `.value` property, not `.text`
  - Makes time display focusable via Tab key
- **Volume Control**: Use Button cycling through levels (not Slider)
  - Toga Slider API has issues with `range` parameter
  - Button provides better screen reader feedback
- **Switches**: Use `toga.Switch` for binary options (on/off toggles)
- **Dropdowns**: Use `toga.Selection` for multiple choices

### Testing Requirements
- **MUST test with NVDA screen reader** before considering any UI feature complete
- Verify Tab navigation reaches all controls
- Verify all controls announce their purpose
- Test button activation with Enter/Space keys

## Code Conventions

### Logging
- Use comprehensive logging for all user interactions
- Log level: INFO for user actions, ERROR for failures
- Pattern: `logger.info(f"Action performed: {details}")`
- All event handlers should log the action

### Event Handlers
```python
def _on_control_change(self, widget):
    """Handle control change with logging and status update."""
    logger.info(f"Control changed to: {widget.value}")
    self.status_label.text = f"Status update for screen readers"
    # Audio/timer integration in Phase 2+
```

### Async Operations
- Clock updates use async background tasks
- Pattern: `async def update_clock(*args):` (accepts interface parameter)
- Use `self.add_background_task(coroutine)` (deprecated but functional)
- Alternative: `asyncio.create_task()` or `App.on_running()` handler

### Status Feedback
- Always update `self.status_label.text` for screen reader announcements
- Provide immediate feedback for all user actions
- Example: "Volume set to 50%", "Soundpack changed to Classic"

## Development Workflow

### Phase-Based Development
Current: **Phase 1 Complete** ✅
- Phase 1: Core UI with accessibility
- Phase 2: Audio playback system (sound_lib, threading)
- Phase 3: Soundpack implementation with audio files
- Phase 4: Settings persistence
- Phase 5: Polish and advanced features
- Phase 6: Distribution packaging

### Git Practices
- Repository at project root (`accessible_talking_clock/`)
- Commit early and often
- Use descriptive commit messages
- Include "Co-Authored-By: Memex <noreply@memex.tech>" for AI assistance
- Feature branches for new development

### Package Installation
```bash
# Setup
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/Linux
uv pip install briefcase toga sound_lib ipykernel matplotlib
```

## Known Issues & Workarounds

### Toga Slider Widget
**Issue**: `toga.Slider(range=(0,100), ...)` throws `NameError: Unknown property 'range'`
**Workaround**: Use Button with cycling volume levels instead
**Status**: Simplified for Phase 1, may revisit in Phase 5

### Clock Update Async
**Issue**: Background task handler receives unexpected interface parameter
**Solution**: Define coroutine as `async def update_clock(*args):` to accept parameters
**Status**: Working with deprecation warning

### Briefcase Project Structure
**Important**: `briefcase new` creates nested directory with app name
- Project root: `accessible_talking_clock/`
- Briefcase app: `accessible_talking_clock/accessibletalkingclock/`
- Always cd into the briefcase app directory before running `briefcase dev`

## Application Design Principles

### User Experience
- Large, readable fonts (32px for clock)
- Clear status messages
- Simple, uncluttered interface
- Logical control grouping

### Code Organization
- Main application logic in `app.py`
- Single class: `AccessibleTalkingClock(toga.App)`
- Event handlers prefixed with `_on_` or `_` (private methods)
- Helper methods for time formatting, UI updates

### Error Handling
- Try/except blocks in async operations
- Log errors comprehensively
- Graceful degradation (continue operation when possible)

## Documentation Standards

### Code Comments
- Docstrings for all public methods
- Inline comments for complex logic
- TODO comments for future phases with phase number

### README Files
- Project root README: Overall project documentation
- Application README: App-specific usage instructions
- Include accessibility testing procedures

## Testing Checklist (Phase 1)
- [x] Application launches without errors
- [x] Clock display updates every second
- [x] Clock display is accessible via Tab key
- [x] All controls accessible via keyboard
- [x] Soundpack selection changes logged
- [x] Volume control cycles through levels
- [x] Interval switches toggle properly
- [x] Status label updates on all actions
- [x] NVDA announces all elements correctly
- [x] Tab order is logical
- [x] All buttons activate with Enter/Space

## Resources & References
- Toga documentation: https://toga.readthedocs.io/
- Briefcase documentation: https://briefcase.readthedocs.io/
- NVDA download: https://www.nvaccess.org/download/
- Design guidelines: https://raw.githubusercontent.com/memextech/templates/refs/heads/main/design/minimalist-b2b-professional.md

## Phase 2+ Preparation Notes

### Audio System (sound_lib)
- **Library**: sound_lib (high-level wrapper around BASS audio library)
- **Advantages**: 
  - Specifically designed for accessible applications
  - Wide format support (MP3, WAV, OGG, FLAC, and many more)
  - Thread-safe audio playback
  - Simple API for basic playback needs
  - Cross-platform (Windows, macOS, Linux)
- **Installation**: `pip install sound_lib` or `uv pip install sound_lib`
- **Documentation**: https://sound-lib.readthedocs.io/
- **Basic Usage Pattern**:
  ```python
  from sound_lib import stream
  
  # Create and play a sound
  s = stream.FileStream(file="chime.wav")
  s.volume = 0.5  # Set volume (0.0 to 1.0)
  s.play()
  
  # Check if playing
  if s.is_playing:
      # Handle playback state
  
  # Stop and cleanup
  s.stop()
  s.free()
  ```

### Audio File Organization
- Audio files will go in `src/accessibletalkingclock/resources/sounds/`
- Structure:
  ```
  resources/sounds/
  ├── classic/
  │   ├── hour.wav
  │   ├── quarter.wav
  │   └── half.wav
  ├── nature/
  │   ├── hour.wav
  │   ├── quarter.wav
  │   └── half.wav
  └── digital/
      ├── hour.wav
      ├── quarter.wav
      └── half.wav
  ```
- Threading required for background chimes (don't block UI)
- Settings will persist to JSON file in user directory
- Consider .gitkeep for empty sounds directory initially
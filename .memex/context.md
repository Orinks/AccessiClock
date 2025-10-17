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

# If briefcase dev fails with template out of date error:
python -m briefcase create  # Reset configuration, overwrite when prompted

# Using startup scripts
.\start.ps1  # Windows
./start.sh   # Unix/Linux

# Running tests
pytest tests/
```

### Briefcase Troubleshooting
- **Template out of date error**: Run `briefcase create` and choose to overwrite to reset the configuration pyproject file
- **App won't start**: Check logs in `logs/` directory for detailed error messages

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
│   │   ├── audio/                # Phase 2: Audio playback system
│   │   │   ├── __init__.py
│   │   │   ├── player.py         # AudioPlayer class
│   │   │   └── test_sound.wav    # Test audio file
│   │   └── resources/            # Icons, sounds (Phase 3+)
│   │       └── sounds/           # Soundpack audio files
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_app.py           # Main application tests
│   │   └── test_audio_player.py  # AudioPlayer tests (Phase 2)
│   ├── pyproject.toml            # Briefcase configuration
│   ├── start.ps1                 # Windows startup script
│   └── start.sh                  # Unix startup script
└── plans/                         # Project planning documents
```

**CRITICAL**: Git repository is at `accessible_talking_clock/` root level, NOT inside the `accessibletalkingclock/` subdirectory.

## Testing Methodology

### Test-Driven Development (TDD)
**Required approach for all new features:**
1. **Write test first**: Define expected behavior before implementation
2. **Run test**: Verify it fails (red)
3. **Implement minimum code**: Make the test pass (green)
4. **Refactor**: Improve code while keeping tests passing
5. **Repeat**: Continue cycle for next behavior

### Behavior-Driven Development (BDD)
**Focus on user-facing behavior:**
- Tests should describe WHAT the feature does, not HOW it does it
- Use descriptive test names: `test_clock_updates_every_second()`
- Assert expected outcomes from user perspective
- Example:
  ```python
  def test_volume_button_cycles_through_levels():
      """When user clicks volume button, volume cycles through 25%, 50%, 75%, 100%, then back to 25%."""
      app = create_test_app()
      initial_volume = app.volume_level
      
      app._on_volume_toggle(None)
      assert app.volume_level == 50
      assert app.status_label.text == "Volume set to 50%"
      
      app._on_volume_toggle(None)
      assert app.volume_level == 75
      
      app._on_volume_toggle(None)
      assert app.volume_level == 100
      
      app._on_volume_toggle(None)
      assert app.volume_level == 25  # Cycles back
  ```

### Test Organization
- **Unit Tests**: Individual component behavior (methods, functions)
- **Integration Tests**: Component interactions (UI + logic)
- **Accessibility Tests**: Screen reader compatibility, keyboard navigation
- All tests in `accessibletalkingclock/tests/` directory
- Use pytest framework
- Mock external dependencies (file I/O, audio playback)

### Test Assertions
**Always assert expected behavior:**
- ✅ `assert clock.display.value.startswith("12:")` - Tests behavior
- ✅ `assert status_label.text == "Volume set to 50%"` - Tests user feedback
- ✅ `assert sound.is_playing == True` - Tests state
- ❌ `assert type(widget) == toga.TextInput` - Tests implementation detail

### Accessibility Testing
**Manual verification required (cannot be fully automated):**
- Run NVDA and verify announcements
- Test Tab navigation sequence
- Verify keyboard shortcuts work
- Document test procedures in test docstrings
- Create automated tests for keyboard event handling where possible

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
- Write automated tests for keyboard event handling

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

### Feature Implementation Process
1. **Plan**: Define user-facing behavior
2. **Test**: Write test(s) asserting expected behavior
3. **Implement**: Write minimum code to pass tests
4. **Verify**: Run tests and manual accessibility checks
5. **Refactor**: Improve code quality
6. **Commit**: Save progress with descriptive message

### Phase-Based Development
Current: **Phase 2 Complete** ✅

#### Completed Phases
- **Phase 1: Core UI with accessibility** ✅
  - Clock display with TextInput for screen reader access
  - Soundpack selection dropdown
  - Volume control button (cycling through levels)
  - Interval switches (hourly, half-hour, quarter-hour)
  - Test Chime button
  - Settings button placeholder
  - All controls keyboard accessible
  - Tab navigation working
  - Status label for screen reader feedback

- **Phase 2: Audio playback system** ✅
  - sound_lib library integration
  - AudioPlayer class with thread-safe playback
  - Volume control (0-100%)
  - Test sound file (440Hz beep)
  - 15 comprehensive unit tests (all passing)
  - UI integration (volume button, Test Chime button)
  - Error handling and status feedback
  - Non-blocking audio playback

#### Upcoming Phases
- Phase 3: Soundpack implementation with audio files
- Phase 4: Settings persistence
- Phase 5: Polish and advanced features
- Phase 6: Distribution packaging

### Git Practices

#### Branch Strategy
- **Repository location**: `accessible_talking_clock/` (project root)
- **For new features**: ALWAYS create a new branch
  - Base branch: current branch (usually `main` or `dev`)
  - Naming convention: `feature/feature-name` or `phase-N/feature-name`
  - Example: `git checkout -b feature/audio-playback`
- **Never work directly on main/dev branches** for new features

#### Commit & Push Workflow
- **Commit in phases**: Save work incrementally as you progress
  - After writing tests
  - After implementing feature
  - After refactoring
  - After manual testing
- **Push regularly**: Push commits to remote branch to ensure work is backed up
  - Push after each meaningful commit
  - Push at end of work session
  - Push before switching tasks
- **Commit message format**:
  ```
  Brief description of change
  
  - Detailed point 1
  - Detailed point 2
  
  Co-Authored-By: Memex <noreply@memex.tech>
  ```

#### Example Workflow
```bash
# Starting new feature
git checkout main  # or dev
git pull origin main
git checkout -b feature/audio-playback

# Work cycle
# ... write tests ...
git add tests/test_audio.py
git commit -m "Add tests for audio playback system"
git push origin feature/audio-playback

# ... implement feature ...
git add src/accessibletalkingclock/app.py
git commit -m "Implement audio playback with sound_lib"
git push origin feature/audio-playback

# ... refactor ...
git add src/accessibletalkingclock/app.py
git commit -m "Refactor audio code into separate methods"
git push origin feature/audio-playback

# When feature complete
# Create pull request or merge to main/dev
```

#### Commit Best Practices
- Commit early and often
- Each commit should be a logical unit of work
- Include "Co-Authored-By: Memex <noreply@memex.tech>" for AI-assisted work
- Write descriptive commit messages
- Push after each commit to prevent data loss

### Package Installation
```bash
# Setup
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/Linux
uv pip install briefcase toga sound_lib pytest ipykernel matplotlib
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

## Testing Checklist

### Phase 1 ✅
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

### Phase 2 ✅
- [x] sound_lib installed successfully
- [x] AudioPlayer class implemented
- [x] Volume control (0-100%) working
- [x] Test sound file created (440Hz beep)
- [x] 15 unit tests written and passing
- [x] AudioPlayer integrated with UI
- [x] Volume button updates AudioPlayer
- [x] Test Chime button plays audio
- [x] Error handling for audio failures
- [x] Status label announces audio events
- [ ] Manual NVDA testing (requires user interaction)

## Resources & References
- Toga documentation: https://toga.readthedocs.io/
- Briefcase documentation: https://briefcase.readthedocs.io/
- NVDA download: https://www.nvaccess.org/download/
- pytest documentation: https://docs.pytest.org/
- Design guidelines: https://raw.githubusercontent.com/memextech/templates/refs/heads/main/design/minimalist-b2b-professional.md

## Audio System (Phase 2 - Complete)

### Implementation Details
- **Library**: sound_lib 0.83 (high-level wrapper around BASS audio library)
- **Status**: ✅ Installed and integrated
- **Location**: `src/accessibletalkingclock/audio/player.py`
- **Features Implemented**:
  - AudioPlayer class with thread-safe playback
  - Volume control (0-100% with clamping)
  - Wide format support (WAV, MP3, OGG, FLAC)
  - Playback status checking
  - Error handling for missing/invalid files
  - Automatic BASS initialization
  - UI integration (volume button, Test Chime button)
- **Testing**: 15 unit tests, all passing
- **Documentation**: https://sound-lib.readthedocs.io/

### Usage in Application
```python
from accessibletalkingclock.audio import AudioPlayer

# Initialize (done in app.startup())
self.audio_player = AudioPlayer(volume_percent=50)

# Play sound
self.audio_player.play_sound("path/to/sound.wav")

# Change volume
self.audio_player.set_volume(75)

# Check status
if self.audio_player.is_playing():
    # Handle playback state

# Stop playback
self.audio_player.stop()
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
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
- Virtual environment location: `.venv/` at project root (NOT in briefcase app subdirectory)
- Key dependencies: `briefcase`, `toga`, `sound_lib` (Phase 2+)

### Development Commands
```bash
# CRITICAL: Virtual environment activation and briefcase dev execution
# The .venv is at PROJECT ROOT (accessible_talking_clock/)
# BUT briefcase dev MUST be run from the briefcase app directory (accessibletalkingclock/)

# Correct workflow:
cd C:\Users\joshu\Workspace\accessible_talking_clock  # Project root
.venv\Scripts\Activate.ps1  # PowerShell (NOT activate.bat)
cd accessibletalkingclock   # Briefcase app directory - MUST cd here before briefcase dev
python -m briefcase dev     # Run the app (from accessibletalkingclock/ directory)

# WRONG: Running briefcase dev from project root will fail
# cd C:\Users\joshu\Workspace\accessible_talking_clock
# python -m briefcase dev  # ❌ This won't work - no pyproject.toml here

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
- **ModuleNotFoundError**: Ensure dependencies are in `pyproject.toml` `requires` list AND installed in venv
- **CRITICAL: briefcase dev location**: MUST be run from `accessibletalkingclock/` directory (where pyproject.toml is), NOT from project root

## Project Structure

### Directory Layout
```
accessible_talking_clock/           # Project root (Git repository here, .venv here)
├── .venv/                         # Virtual environment (PROJECT ROOT LEVEL)
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
│   ├── pyproject.toml            # Briefcase configuration (MUST include all runtime deps)
│   ├── start.ps1                 # Windows startup script
│   └── start.sh                  # Unix startup script
└── plans/                         # Project planning documents
```

**CRITICAL**: 
- Git repository is at `accessible_talking_clock/` root level
- Virtual environment (`.venv/`) is at `accessible_talking_clock/` root level
- Briefcase app is at `accessible_talking_clock/accessibletalkingclock/`

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

### Application Lifecycle Management
**CRITICAL**: Proper cleanup is required to prevent resource leaks and threading issues

#### Initialization Pattern
```python
class AccessibleTalkingClock(toga.App):
    def __init__(self, *args, **kwargs):
        """Initialize application."""
        super().__init__(*args, **kwargs)
        self._clock_task = None
        self._shutdown_flag = False
        # Initialize other state variables
```

#### Cleanup Pattern (REQUIRED)
```python
async def on_exit(self):
    """Clean up resources before application exits."""
    logger.info("Application exit handler called")
    
    # Signal background tasks to stop
    self._shutdown_flag = True
    
    # Give async tasks time to stop gracefully
    try:
        await asyncio.sleep(0.5)
        logger.info("Background tasks stopped")
    except Exception as e:
        logger.warning(f"Error waiting for tasks: {e}")
    
    # Clean up external resources (audio, files, etc.)
    if self.audio_player:
        try:
            self.audio_player.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up audio player: {e}")
    
    logger.info("Application cleanup completed")
    return True  # Allow exit
```

#### Background Task Pattern
```python
async def update_task(*args):
    """Background task that checks shutdown flag."""
    while not self._shutdown_flag:
        try:
            # Do work
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in task: {e}")
            await asyncio.sleep(1)
    logger.info("Task stopped")
```

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
- **ALWAYS** make background tasks stoppable with shutdown flag

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
  - **Proper cleanup with BASS_Free()**

#### Upcoming Phases
- Phase 3: Soundpack implementation with audio files
- Phase 4: Settings persistence
- Phase 5: Polish and advanced features
- Phase 6: Distribution packaging

### Git Practices

#### Branch Strategy
- **Repository location**: `accessible_talking_clock/` (project root)
- **main**: Production-ready code only
- **dev**: Development integration branch (all feature branches merge here first)
- **For new features**: ALWAYS create a new branch from `dev`
  - Naming convention: `phase-N/feature-name` or `feature/feature-name`
  - Example: `git checkout dev && git checkout -b phase-3/soundpack-implementation`
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
git checkout dev
git pull origin dev
git checkout -b phase-3/soundpack-implementation

# Work cycle
# ... write tests ...
git add tests/test_soundpack.py
git commit -m "Add tests for soundpack loading system"
git push origin phase-3/soundpack-implementation

# ... implement feature ...
git add src/accessibletalkingclock/soundpack.py
git commit -m "Implement soundpack loading from directory structure"
git push origin phase-3/soundpack-implementation

# ... refactor ...
git add src/accessibletalkingclock/soundpack.py
git commit -m "Refactor soundpack code into separate methods"
git push origin phase-3/soundpack-implementation

# When feature complete - merge to dev first
git checkout dev
git pull origin dev
git merge phase-3/soundpack-implementation
git push origin dev

# Later - merge dev to main for release
git checkout main
git merge dev
git push origin main
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
.venv\Scripts\Activate.ps1  # Windows PowerShell
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

### Threading Issues on Shutdown (KNOWN LIMITATION)
**Issue**: When closing the application, threading errors appear:
- `Windows fatal exception: code 0x80010108` (RPC_E_DISCONNECTED)
- Errors in `toga_winforms\libs\proactor.py` and `pythonnet\__init__.py`

**Root Cause**: This is a **known framework-level issue** with pythonnet and toga-winforms on Windows. The error occurs when:
1. The WinForms event loop (proactor) is shutting down
2. Pythonnet is trying to unload .NET assemblies
3. COM threading conflicts occur between these two shutdown processes

**Impact**:
- Error appears AFTER the application window closes
- Error appears AFTER cleanup code completes
- Does NOT affect application functionality
- Does NOT lose user data
- Does NOT prevent clean shutdown
- Users never see this error (console only, not in packaged apps)

**Mitigation**:
- We implement proper cleanup with `on_exit()` handler
- All user-level resources are freed (audio, tasks, etc.)
- This is the best we can do at the application level
- See `THREADING_FIXES.md` for detailed documentation

**References**:
- pythonnet issue #1701: PythonEngine.Shutdown() threading issues
- COM error 0x80010108: RPC_E_DISCONNECTED
- Documented in `accessibletalkingclock/THREADING_FIXES.md`

**DO NOT** attempt to "fix" this by:
- Removing cleanup code
- Adding sleeps before exit
- Trying to manually control pythonnet shutdown
- The error is unavoidable at the framework level

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
- External systems (audio) in separate modules

### Error Handling
- Try/except blocks in async operations
- Log errors comprehensively
- Graceful degradation (continue operation when possible)
- Always clean up resources in finally blocks or cleanup handlers

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
- [x] Cleanup handler implemented with BASS_Free()
- [x] Background tasks stoppable with shutdown flag
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
  - **Proper cleanup with BASS_Free() call**
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

# CRITICAL: Clean up (done in app.on_exit())
self.audio_player.cleanup()  # Frees BASS resources
```

### AudioPlayer Cleanup Pattern (REQUIRED)
**MUST** be called in application `on_exit()` handler:
```python
def cleanup(self):
    """Clean up audio resources including BASS library."""
    global _bass_initialized
    
    logger.info("Cleaning up AudioPlayer resources")
    
    # Stop and free current stream
    if self._current_stream:
        try:
            self._current_stream.stop()
            self._current_stream.free()
            self._current_stream = None
        except Exception as e:
            logger.warning(f"Error during stream cleanup: {e}")
    
    # Free BASS library resources
    if _bass_initialized:
        try:
            BASS_Free()
            _bass_initialized = False
            logger.info("BASS audio system freed")
        except Exception as e:
            logger.warning(f"Error freeing BASS: {e}")
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

### Dependencies Management
**CRITICAL**: All runtime dependencies MUST be in `pyproject.toml`:
```toml
[tool.briefcase.app.accessibletalkingclock]
requires = [
    "sound_lib",  # REQUIRED for audio playback
    # Add other runtime dependencies here
]
```

**Common mistake**: Installing package in venv but forgetting to add to `pyproject.toml` causes `ModuleNotFoundError` when running `briefcase dev`.
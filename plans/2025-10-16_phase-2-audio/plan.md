# Phase 2: Audio Playback System

## Created
2025-10-16

## Overview
Implement audio playback system using sound_lib library with thread-safe background playback. This phase establishes the foundation for playing chime sounds at configured intervals without blocking the UI thread.

## Goals
1. Install and configure sound_lib library
2. Create basic audio playback abstraction layer
3. Implement thread-safe audio player
4. Add audio testing capabilities
5. Integrate with existing clock UI (volume control)
6. Prepare directory structure for Phase 3 soundpacks

## Non-Goals
- Actual chime scheduling (Phase 3)
- Complete soundpack implementation (Phase 3)
- Settings persistence (Phase 4)
- Multiple interval configuration (Phase 4)

## Technical Approach

### Audio Library: sound_lib
- Wrapper around BASS audio library
- Thread-safe by design
- Wide format support (WAV, MP3, OGG, FLAC)
- Simple API for accessible applications
- Cross-platform compatible

### Architecture
```
src/accessibletalkingclock/
├── app.py                    # Existing main app (integrate volume control)
├── audio/
│   ├── __init__.py
│   ├── player.py            # AudioPlayer class (sound_lib wrapper)
│   └── test_sound.wav       # Simple test sound file
└── resources/
    └── sounds/
        └── .gitkeep         # Prepare for Phase 3 soundpacks
```

### Threading Strategy
- UI thread: Main Toga event loop (never blocks)
- Audio playback: sound_lib handles threading internally
- No explicit threading needed (sound_lib is designed for this)

## Implementation Steps

### Step 1: Setup Audio Infrastructure
- Install sound_lib dependency
- Create `audio/` package structure
- Add simple test sound file
- Create resource directory structure

### Step 2: AudioPlayer Implementation
- Create `AudioPlayer` class in `audio/player.py`
- Methods:
  - `__init__(volume_percent=50)`
  - `play_sound(file_path: str)` - Play audio file
  - `stop()` - Stop current playback
  - `set_volume(volume_percent: int)` - Set volume (0-100)
  - `is_playing() -> bool` - Check playback status
- Error handling for missing files, invalid formats

### Step 3: Testing
- Unit tests for AudioPlayer class
- Test volume control
- Test multiple sequential sounds
- Test error conditions (missing files, invalid formats)
- Manual testing with NVDA active

### Step 4: UI Integration
- Connect existing volume button to AudioPlayer.set_volume()
- Add "Test Audio" button to UI
- Status label feedback for audio events
- Verify audio doesn't block UI updates

## Acceptance Criteria
- [ ] sound_lib installed and working
- [ ] AudioPlayer class plays WAV files without blocking UI
- [ ] Volume control affects audio playback
- [ ] Test button plays sound on demand
- [ ] All tests pass
- [ ] Clock continues updating during audio playback
- [ ] NVDA compatibility maintained

## Testing Strategy
**TDD Approach:**
1. Write test for each AudioPlayer method before implementation
2. Run test (should fail)
3. Implement method
4. Run test (should pass)
5. Refactor as needed

**Manual Testing:**
1. Start NVDA
2. Launch app
3. Click "Test Audio" button
4. Verify sound plays
5. Verify clock continues updating
6. Change volume and test again
7. Verify status label announces actions

## Dependencies
- sound_lib (install via uv)
- pytest (already installed)
- Test audio file (create simple WAV)

## Risks & Mitigations
- **Risk**: sound_lib installation issues on Windows
  - Mitigation: Fallback to simpler library if needed (winsound)
- **Risk**: Audio blocks UI thread
  - Mitigation: sound_lib is async by design; verify in tests
- **Risk**: BASS library not available
  - Mitigation: sound_lib bundles BASS; no separate install needed

## Next Phase Preview
Phase 3 will use this AudioPlayer to:
- Implement 3 soundpacks (classic, nature, digital)
- Schedule chimes at configured intervals
- Add soundpack selection UI
- Manage audio file resources

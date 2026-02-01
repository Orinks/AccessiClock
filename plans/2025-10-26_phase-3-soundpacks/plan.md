# Phase 3: Soundpack Implementation

## Overview
Implement the soundpack system with real audio files for three themes: Classic, Nature, and Digital. Each soundpack contains three chime sounds: hourly, half-hour, and quarter-hour.

## Goals
1. Create soundpack directory structure and audio file organization
2. Implement Soundpack class to manage loading and accessing audio files
3. Find or create free-to-use audio files for three soundpack themes
4. Integrate soundpack system with existing UI and AudioPlayer
5. Implement automatic chiming based on interval switches
6. Test all functionality with TDD/BDD approach

## Requirements

### Functional Requirements
- **FR1**: System loads soundpack audio files from organized directory structure
- **FR2**: Users can switch between Classic, Nature, and Digital soundpacks via dropdown
- **FR3**: System plays appropriate chime (hour/half/quarter) based on current time and enabled intervals
- **FR4**: Test Chime button plays the hourly chime of selected soundpack
- **FR5**: All audio files are properly attributed if required by license
- **FR6**: System gracefully handles missing or invalid audio files

### Non-Functional Requirements
- **NFR1**: Audio files are high quality (16-bit, 44.1kHz WAV or OGG)
- **NFR2**: Audio files are royalty-free or Creative Commons licensed
- **NFR3**: Soundpack loading is performant (< 500ms on startup)
- **NFR4**: All functionality maintains existing accessibility standards

## Technical Design

### Directory Structure
```
accessibletalkingclock/src/accessibletalkingclock/
├── resources/
│   └── sounds/
│       ├── classic/
│       │   ├── hour.wav
│       │   ├── half.wav
│       │   └── quarter.wav
│       ├── nature/
│       │   ├── hour.wav
│       │   ├── half.wav
│       │   └── quarter.wav
│       ├── digital/
│       │   ├── hour.wav
│       │   ├── half.wav
│       │   └── quarter.wav
│       └── ATTRIBUTIONS.md  # Credit for audio sources
```

### Soundpack Class Design
```python
class Soundpack:
    """Manages loading and accessing soundpack audio files."""
    
    def __init__(self, name: str, base_path: Path):
        """Initialize soundpack with name and base directory."""
        
    def load(self) -> bool:
        """Load and validate all sound files. Returns True if successful."""
        
    def get_sound_path(self, chime_type: str) -> Path:
        """Get path to specific chime sound (hour/half/quarter)."""
        
    @property
    def is_loaded(self) -> bool:
        """Check if soundpack is fully loaded."""
        
    @property
    def available_chimes(self) -> List[str]:
        """Get list of available chime types."""
```

### SoundpackManager Class Design
```python
class SoundpackManager:
    """Manages collection of soundpacks and current selection."""
    
    def __init__(self, sounds_directory: Path):
        """Initialize manager with base sounds directory."""
        
    def discover_soundpacks(self) -> List[str]:
        """Scan directory for available soundpacks."""
        
    def get_soundpack(self, name: str) -> Soundpack:
        """Get loaded soundpack by name."""
        
    def load_soundpack(self, name: str) -> bool:
        """Load specific soundpack. Returns True if successful."""
        
    @property
    def available_soundpacks(self) -> List[str]:
        """Get list of available soundpack names."""
```

### Integration Points
1. **App startup**: Initialize SoundpackManager, load default soundpack
2. **Soundpack dropdown change**: Load selected soundpack
3. **Test Chime button**: Play hourly chime from current soundpack
4. **Clock update task**: Check time and play appropriate chime if enabled
5. **Cleanup**: No special cleanup needed (AudioPlayer handles resources)

## Implementation Plan

### MVP (Minimum Viable Product)
1. **Soundpack structure** [P:mvp-1]
   - Create resources/sounds/ directory structure
   - Add placeholder .gitkeep files

2. **Soundpack class with tests** [P:mvp-2]
   - Write tests for Soundpack class (TDD)
   - Implement Soundpack class
   - Test loading, validation, path retrieval

3. **SoundpackManager class with tests** [P:mvp-3]
   - Write tests for SoundpackManager (TDD)
   - Implement SoundpackManager
   - Test discovery, loading, switching

4. **Find audio files** [P:mvp-4]
   - Search for royalty-free classic chime sounds (bell/clock)
   - Search for nature sounds (birds, wind chimes, water)
   - Search for digital sounds (beeps, synth tones)
   - Document sources and licenses in ATTRIBUTIONS.md

5. **UI integration** [P:mvp-5]
   - Update app.py to use SoundpackManager
   - Connect Test Chime button to play hourly sound
   - Update soundpack dropdown to load selected pack
   - Add error handling and status feedback

6. **Automatic chiming** [P:mvp-6]
   - Implement time-based chime logic in clock update task
   - Check interval switches (hourly/half/quarter)
   - Play appropriate chime at correct time
   - Prevent duplicate chimes (track last chime time)

### Iteration 1: Testing & Polish
7. **Manual testing** [P:iter1-1]
   - Test all three soundpacks load correctly
   - Verify chimes play at correct times
   - Test with NVDA screen reader
   - Verify volume control affects chimes

8. **Error handling** [P:iter1-2]
   - Graceful handling of missing files
   - User-friendly error messages
   - Fallback to test beep if soundpack fails

### Iteration 2: Documentation
9. **Documentation** [P:iter2-1]
   - Update README with soundpack information
   - Document how to add custom soundpacks
   - Add troubleshooting section

## Audio File Requirements

### Classic Soundpack
- **Theme**: Traditional clock chimes (grandfather clock, church bells)
- **Hour**: Full chime sequence (e.g., Westminster chimes)
- **Half**: Shorter chime or single bell
- **Quarter**: Brief bell tone

### Nature Soundpack
- **Theme**: Natural, calming sounds
- **Hour**: Bird calls or wind chimes (longer)
- **Half**: Gentle water sound or shorter bird call
- **Quarter**: Soft chime or nature accent

### Digital Soundpack
- **Theme**: Modern, electronic tones
- **Hour**: Multi-tone digital sequence
- **Half**: Two-tone beep
- **Quarter**: Single tone beep

### File Specifications
- **Format**: WAV (preferred) or OGG Vorbis
- **Sample Rate**: 44.1kHz or 48kHz
- **Bit Depth**: 16-bit minimum
- **Duration**: 1-5 seconds (longer for hourly)
- **Licensing**: CC0, CC-BY, or Public Domain

### Search Sources
- Freesound.org (CC-licensed sounds)
- OpenGameArt.org (CC0 sounds)
- ZapSplat.com (free tier)
- BBC Sound Effects (free for personal use)
- sonniss.com GameAudioGDC (annual free bundles)

## Testing Strategy

### Unit Tests
- Soundpack class methods (load, validate, get_path)
- SoundpackManager discovery and switching
- Path resolution and file existence checks
- Error handling for missing/invalid files

### Integration Tests
- App startup with soundpack loading
- Dropdown selection triggers soundpack change
- Test Chime button plays correct sound
- Automatic chiming at correct times
- Volume control affects chime playback

### Manual Testing
- Listen to all sounds in all soundpacks
- Verify timing accuracy (chimes at :00, :15, :30, :45)
- Test with different interval switch combinations
- NVDA screen reader compatibility
- Performance with rapid soundpack switching

## Success Criteria
- ✅ All three soundpacks have complete audio files
- ✅ Soundpacks load successfully on app startup
- ✅ User can switch soundpacks via dropdown
- ✅ Test Chime plays hourly sound of current soundpack
- ✅ Automatic chiming works correctly based on time
- ✅ All audio files properly attributed
- ✅ All unit tests passing
- ✅ Manual accessibility testing completed
- ✅ No errors in logs during normal operation

## Dependencies
- Existing AudioPlayer class (Phase 2)
- pathlib for file system operations
- No new external packages required

## Timeline Estimate
- Soundpack classes: 1-2 hours
- Audio file sourcing: 1-2 hours
- UI integration: 1 hour
- Automatic chiming: 1 hour
- Testing & polish: 1-2 hours
- **Total**: 5-8 hours

## Risks & Mitigation
- **Risk**: Cannot find suitable free audio files
  - **Mitigation**: Generate simple tones programmatically if needed
- **Risk**: Audio files too large, slow loading
  - **Mitigation**: Compress/optimize files, lazy load on demand
- **Risk**: Chiming interrupts user workflow
  - **Mitigation**: Non-blocking playback (already implemented in AudioPlayer)

## References
- sound_lib documentation: https://sound-lib.readthedocs.io/
- Freesound API: https://freesound.org/docs/api/
- Creative Commons licenses: https://creativecommons.org/licenses/

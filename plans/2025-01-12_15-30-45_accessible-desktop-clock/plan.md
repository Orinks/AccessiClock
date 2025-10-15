# Spec Provenance
Created: 2025-01-12T15:30:45Z  
User request: Native desktop clock application for accessibility (blind/visually impaired users)  
Framework choice: Toga (BeeWare) - native Windows widgets with cross-platform capability  
Scope: MVP with multiple built-in soundpacks, configurable intervals, accessible UI—no custom soundpack creation yet

# Spec Header

**Project**: Accessible Desktop Clock  
**Smallest Scope**: Windows-first clock app with 3 built-in soundpacks, hourly/15min/30min intervals, accessible native controls (ComboBox, DetailedList, Switch)  
**Non-Goals**: Custom soundpack creation, cloud sharing, mobile versions, web interface, complex scheduling (minutes/seconds precision)

# Paths to supplementary guidelines
- Design guidance: https://raw.githubusercontent.com/memextech/templates/refs/heads/main/design/minimalist-b2b-professional.md

# Decision Snapshot

**Framework**: Toga (BeeWare) - Uses native Windows widgets that NVDA/JAWS recognize automatically  
**Audio**: Python threading with `pygame` or `playsound` for background audio playback  
**Architecture**: Main UI thread + background timer/audio threads (no GUI thread conflicts)  
**Packaging**: Briefcase (BeeWare's bundler) for native Windows executable  
**Accessibility**: Native Windows controls inherit platform accessibility APIs by default

**Alternative considered**: wxPython (rejected due to threading issues), Tauri (rejected to avoid learning Rust), Python+web frontend (rejected for complexity)

# Architecture at a Glance

```
├── src/
│   ├── main.py              # Toga app entry point, main window
│   ├── ui/
│   │   ├── main_window.py   # Primary clock interface
│   │   └── settings_window.py # Configuration dialog  
│   ├── audio/
│   │   ├── player.py        # Background audio playback
│   │   ├── scheduler.py     # Timer/interval management
│   │   └── soundpacks/
│   │       ├── classic.py   # Westminster chimes
│   │       ├── nature.py    # Birds/water sounds  
│   │       └── digital.py   # Digital beeps/tones
│   ├── models/
│   │   ├── settings.py      # User preferences storage
│   │   └── soundpack.py     # Soundpack interface
│   └── utils/
│       └── accessibility.py # ARIA/focus management helpers
├── resources/
│   └── sounds/             # Audio files (.wav/.ogg)
└── pyproject.toml          # Briefcase configuration
```

**Key UI Components**:
- Main clock display (digital/analog toggle)
- Soundpack selection (Toga `Selection` widget)  
- Interval configuration (checkboxes for hour/15min/30min)
- Volume control (Toga `Slider`)
- Settings dialog with proper focus management

**Threading Model**:
- Main thread: UI updates only
- Timer thread: Interval checking (separate from GUI)
- Audio thread: Sound playback (non-blocking)
- Communication: Thread-safe queues for status updates

# Implementation Plan

## Phase 1: Core Structure (Day 1)
- Set up Toga project with Briefcase
- Create main window with basic clock display
- Implement native Windows widgets (ComboBox, Switch controls)
- Test NVDA compatibility with basic controls

## Phase 2: Audio Foundation (Day 2)  
- Audio playback system using `pygame` mixer
- Background timer thread for interval checking
- Thread-safe communication between audio and UI
- Basic sound loading from resources/sounds/

## Phase 3: Soundpack System (Day 3)
- Define soundpack interface (metadata + audio files)
- Implement 3 built-in soundpacks (classic/nature/digital)
- Soundpack selection UI with proper accessibility labels
- Test soundpack switching and audio playback

## Phase 4: Interval Configuration (Day 4)
- Hour/15min/30min checkbox configuration
- Timer logic for multiple intervals
- Settings persistence (JSON file in user directory)
- Accessible settings dialog with proper tab order

## Phase 5: Polish & Accessibility (Day 5)
- Digital/analog display toggle
- Volume control with audio feedback
- Comprehensive NVDA/JAWS testing
- Focus management and keyboard shortcuts
- Error handling and user feedback

## Phase 6: Packaging (Day 6)
- Briefcase configuration for Windows executable  
- Audio file bundling and resource management
- Testing packaged app accessibility
- Basic documentation and setup instructions

# Verification & Demo Script

**Accessibility Testing**:
1. Launch NVDA screen reader
2. Open clock application
3. Verify all controls announce properly (soundpack dropdown, interval checkboxes, volume slider)
4. Navigate using Tab key - confirm logical focus order
5. Test spacebar/Enter activation of all buttons
6. Verify audio feedback works with screen reader active

**Functionality Testing**:
1. Select different soundpacks - audio should change
2. Configure intervals (hourly + 15min) - should trigger at appropriate times
3. Adjust volume - should affect chime volume immediately
4. Toggle digital/analog display - visual mode should change
5. Save settings - should persist between app launches

**Threading Verification**:
1. UI should remain responsive during audio playback
2. Clock should update smoothly while chimes play
3. Settings changes should take effect without freezing interface
4. App should handle system sleep/wake properly

# Deploy

**Development**: `briefcase dev` for testing with hot reload  
**Packaging**: `briefcase build windows` for standalone .exe  
**Distribution**: Single executable file, no installer required  
**Requirements**: Windows 10+ (for native accessibility API support)

**Accessibility Validation**:
- Test with NVDA 2024+ (free download)
- Verify with Windows Narrator (built-in)
- Optional: JAWS testing if available
- Confirm all features work without visual interface

**Performance Targets**:
- App launch: <3 seconds
- Audio playback latency: <100ms
- Memory usage: <50MB idle
- No audio dropouts during system load
# AccessiClock wxPython Migration: Feature Inventory + Parity Checklist

Branch: `rewrite/wxpython-core-manual`  
Base: `dev`

## Scope for this phase (must-have)

These are the baseline behaviors required for a usable first wxPython version.

- [x] Native wxPython app entrypoint (`accessiclock.main:main`)
- [x] Main window opens and can be navigated with keyboard only
- [x] Predictable startup focus (initial focus lands on a stable control)
- [x] Config path setup (portable + normal mode)
- [x] Logging setup (file + console)
- [x] Settings load/save scaffold with safe defaults
- [x] Startup/shutdown flow scaffold in app class
- [x] Initial keyboard shortcut map documented in code and README
- [x] Smoke tests for settings/shortcuts/logging scaffolding

## Existing feature inventory

### Core clock behavior
- [x] Time display updates every second
- [x] Hourly chime logic
- [x] Half-hour chime logic
- [x] Quarter-hour chime logic
- [x] Quiet hours in clock service

### Audio + voice
- [x] Sound playback through `AudioPlayer`
- [x] Clock pack sound lookup
- [x] Test chime action
- [x] TTS announce current time

### Accessibility + UX
- [x] Keyboard reachable controls (Tab order + mnemonics)
- [x] Screen-reader-friendly labels/names on key controls
- [x] Status text updates for user feedback
- [x] Focus-safe startup behavior

## Later phase items (not required for this run)

- [ ] Full settings dialog parity audit and cleanup
- [ ] Clock manager UX polish and validation messaging
- [ ] Better accessibility pass for dialog content and error states
- [ ] Structured app state object (if needed after more features land)
- [ ] CI matrix that runs GUI smoke checks on Windows
- [ ] Packaging polish (PyInstaller/win installer flow)

## Notes

This phase intentionally keeps architecture lean: minimal new modules for logging, settings persistence, and shortcut mapping. No new heavy framework layer was introduced.

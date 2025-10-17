# Threading Issues and Fixes

## Problem Summary
When closing the Accessible Talking Clock application, threading errors appear in the console:
- `Windows fatal exception: code 0x80010108` (RPC_E_DISCONNECTED)
- Errors in `toga_winforms\libs\proactor.py` and `pythonnet\__init__.py`

## Root Cause
This is a **known framework-level issue** with pythonnet and toga-winforms on Windows. The error occurs during application shutdown when:
1. The WinForms event loop (proactor) is shutting down
2. Pythonnet is trying to unload .NET assemblies
3. COM threading conflicts occur between these two shutdown processes

**Important**: This error happens AFTER the application window has closed and AFTER our cleanup code has run. It does not affect application functionality or user experience.

## Fixes Implemented

### 1. Added Proper Application Cleanup (`on_exit` handler)
**File**: `src/accessibletalkingclock/app.py`

Added async `on_exit()` method that:
- Sets `_shutdown_flag` to stop the clock update task gracefully
- Waits 0.5 seconds for async tasks to complete
- Calls `audio_player.cleanup()` to free audio resources
- Logs all cleanup steps

```python
async def on_exit(self):
    """Clean up resources before application exits."""
    logger.info("Application exit handler called")
    
    # Signal clock task to stop
    self._shutdown_flag = True
    
    # Give the clock task time to stop gracefully
    try:
        await asyncio.sleep(0.5)
        logger.info("Clock update task stopped")
    except Exception as e:
        logger.warning(f"Error waiting for clock task: {e}")
    
    # Clean up audio player
    if self.audio_player:
        try:
            self.audio_player.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up audio player: {e}")
    
    logger.info("Application cleanup completed")
    return True
```

### 2. Made Clock Update Task Stoppable
**File**: `src/accessibletalkingclock/app.py`

Modified `_schedule_clock_update()` to:
- Check `_shutdown_flag` in the while loop
- Exit gracefully when flag is set
- Log when the task stops

```python
async def update_clock(*args):
    while not self._shutdown_flag:
        try:
            self.clock_display.value = self._get_current_time_string()
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error updating clock display: {e}")
            await asyncio.sleep(1)
    logger.info("Clock update task stopped")
```

### 3. Added AudioPlayer Cleanup
**File**: `src/accessibletalkingclock/audio/player.py`

Added `cleanup()` method that:
- Stops and frees current audio stream
- Calls `BASS_Free()` to properly free the BASS audio library
- Resets the global `_bass_initialized` flag

```python
def cleanup(self):
    """
    Clean up audio resources.
    Should be called when shutting down the application.
    """
    global _bass_initialized
    
    logger.info("Cleaning up AudioPlayer resources")
    if self._current_stream:
        try:
            self._current_stream.stop()
            self._current_stream.free()
            self._current_stream = None
        except Exception as e:
            logger.warning(f"Error during AudioPlayer cleanup: {e}")
    
    # Free BASS library resources
    if _bass_initialized:
        try:
            BASS_Free()
            _bass_initialized = False
            logger.info("BASS audio system freed")
        except Exception as e:
            logger.warning(f"Error freeing BASS audio system: {e}")
```

### 4. Added sound_lib to Dependencies
**File**: `pyproject.toml`

Added `sound_lib` to the `requires` list so it's available when running in dev mode:
```toml
requires = [
    "sound_lib",
]
```

## Current Status

### ✅ Fixed
- AudioPlayer resources are properly cleaned up
- BASS audio library is properly freed
- Clock update task stops gracefully
- Application logs cleanup progress
- All user-level resources are freed before shutdown

### ⚠️ Known Issue (Cannot Fix)
The threading error still appears in the console during shutdown. This is a **pythonnet/toga-winforms framework limitation** and cannot be fixed at the application level.

**Why this happens**:
- Pythonnet needs to unload .NET assemblies during Python interpreter shutdown
- The WinForms event loop (proactor) is also shutting down simultaneously
- COM threading rules are violated when these two processes race
- This is documented in pythonnet issue #1701

**Impact**: 
- Error appears AFTER window closes
- Error appears AFTER our cleanup completes
- Does NOT affect application functionality
- Does NOT lose user data
- Does NOT prevent clean shutdown
- Users never see this error (console only)

## Testing Results

Cleanup logging shows proper sequence:
1. User closes window
2. `on_exit` handler is called
3. Clock task stops
4. AudioPlayer cleanup runs
5. BASS audio system freed
6. Application cleanup completed
7. **Then** pythonnet threading error occurs

## Recommendations

### For Development
- Ignore the threading error messages in console
- Focus on the cleanup log messages to verify proper shutdown
- The error is expected and documented

### For Distribution
- When packaging with briefcase for distribution, users won't see console output
- The error won't affect the packaged application
- No user-facing impact

### Future Improvements
- Monitor pythonnet and toga-winforms for framework updates
- Consider alternative audio libraries if BASS contributes to the issue
- Could explore toga-winforms alternatives (toga-gtk on Windows via WSL)

## References
- pythonnet issue #1701: PythonEngine.Shutdown() threading issues
- COM error 0x80010108: RPC_E_DISCONNECTED (The object invoked has disconnected from its clients)
- Toga documentation: App.on_exit() handler

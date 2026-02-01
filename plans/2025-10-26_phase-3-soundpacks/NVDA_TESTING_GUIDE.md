# NVDA Testing Guide for Phase 3

## Prerequisites
- NVDA screen reader installed and running
- Application built and ready to run

## How to Run the Application

1. Open PowerShell
2. Navigate to project directory:
   ```powershell
   cd C:\Users\joshu\Workspace\accessible_talking_clock
   ```

3. Activate virtual environment:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

4. Navigate to app directory:
   ```powershell
   cd accessibletalkingclock
   ```

5. Run the application:
   ```powershell
   python -m briefcase dev
   ```

## Testing Checklist

### Basic Navigation ✓
- [ ] Press Tab to navigate through controls
- [ ] Verify Tab order is logical (top to bottom):
  1. Clock display (read-only text field)
  2. Soundpack dropdown
  3. Volume button
  4. Hourly chime switch
  5. Half-hour chime switch
  6. Quarter-hour chime switch
  7. Test Chime button
  8. Settings button

### Control Announcements ✓
- [ ] **Clock Display**: NVDA should announce current time when focused
- [ ] **Soundpack Dropdown**: NVDA should announce "Soundpack: Classic" (or current selection)
- [ ] **Volume Button**: NVDA should announce "Change Volume button"
- [ ] **Interval Switches**: NVDA should announce switch state (on/off)
- [ ] **Test Chime Button**: NVDA should announce "Test Chime button"

### Status Messages ✓
- [ ] Change soundpack → NVDA should announce "Soundpack changed to [name]"
- [ ] Click volume button → NVDA should announce "Volume set to [N]%"
- [ ] Toggle interval switch → NVDA should announce "Chime intervals: [list]"
- [ ] Click Test Chime → NVDA should announce "Playing [soundpack] hour chime at [volume]%"

### Keyboard Interaction ✓
- [ ] Tab key moves focus between controls
- [ ] Enter/Space activates buttons
- [ ] Arrow keys change dropdown selection
- [ ] Space toggles switches

### Soundpack Testing ✓
- [ ] Change soundpack to "Digital" → Verify NVDA announces change
- [ ] Click Test Chime → Should play digital hour chime
- [ ] Change soundpack to "Nature" → Verify NVDA announces change
- [ ] Click Test Chime → Should play nature hour chime
- [ ] Change soundpack to "Classic" → Verify NVDA announces change
- [ ] Click Test Chime → Should play classic hour chime

### Volume Testing ✓
- [ ] Click Volume button multiple times
- [ ] Verify NVDA announces each volume level: 25%, 50%, 75%, 100%, back to 25%
- [ ] Click Test Chime at different volumes
- [ ] Verify audio loudness changes accordingly

### Automatic Chiming Testing ⏰
**Note**: This requires waiting for specific times. Recommended approach:

#### Hourly Chime Test
1. Enable "Hourly" switch
2. Wait until the next hour (e.g., 3:00 PM)
3. Verify hour chime plays automatically
4. Check that only one chime plays (no duplicates)

#### Half-Hour Chime Test
1. Enable "Half-hour" switch
2. Wait until the next half hour (e.g., 3:30 PM)
3. Verify half chime plays automatically
4. Check that only one chime plays (no duplicates)

#### Quarter-Hour Chime Test
1. Enable "Quarter-hour" switch
2. Wait until the next quarter hour (e.g., 3:15 PM or 3:45 PM)
3. Verify quarter chime plays automatically
4. Check that only one chime plays (no duplicates)

#### Combined Test
1. Enable all three switches (hourly, half-hour, quarter-hour)
2. Wait through a complete hour to verify all chimes play at correct times:
   - :00 → hour chime
   - :15 → quarter chime
   - :30 → half chime
   - :45 → quarter chime

#### Disable Test
1. Disable all switches
2. Wait through multiple time markers
3. Verify NO chimes play when switches are off

## Common Issues and Solutions

### Issue: NVDA not announcing status messages
**Solution**: Status messages appear in the status label. Try navigating to the status label with Tab or using NVDA's review cursor.

### Issue: Can't hear chimes
**Solution**: 
- Check system volume
- Check application volume (use Volume button)
- Verify sound files exist in `resources/sounds/` directories

### Issue: Duplicate chimes playing
**Solution**: This should NOT happen. If it does, this is a bug. Note the time and circumstances.

### Issue: Chimes not playing automatically
**Solution**:
- Verify the correct interval switch is enabled
- Check that the soundpack is loaded (use Test Chime button first)
- Verify audio player is working

## Expected Behavior Summary

### On Startup:
- Application loads with Classic soundpack
- Volume set to 50%
- Clock displays current time, updating every second
- All switches start in "off" state

### Soundpack Switching:
- Selecting a soundpack loads it immediately
- Status message confirms the change
- Test Chime button plays the new soundpack's hour chime

### Automatic Chiming:
- Chimes play only when corresponding switch is enabled
- Only one chime per minute (no duplicates)
- Chime type matches the time:
  - Hour chime at :00
  - Half chime at :30
  - Quarter chime at :15 and :45

### Volume Control:
- Volume cycles through: 25% → 50% → 75% → 100% → 25%
- All chimes (test and automatic) respect current volume setting

## Reporting Issues

If you encounter any issues during testing, please note:
1. What you were doing
2. What you expected to happen
3. What actually happened
4. Any NVDA announcements that seemed incorrect
5. Any console error messages

## Success Criteria

Phase 3 is complete when:
- ✅ All controls are keyboard accessible
- ✅ All controls announce correctly with NVDA
- ✅ All three soundpacks load and play correctly
- ✅ Automatic chiming works at correct times
- ✅ No duplicate chimes
- ✅ Volume control works properly
- ✅ Status messages are announced by NVDA
- ✅ Tab navigation is logical and complete

"""
Manual test script for AudioPlayer integration.
Run this to verify audio playback works without launching the full GUI.
"""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from accessibletalkingclock.audio import AudioPlayer

def main():
    print("=== AudioPlayer Manual Test ===\n")
    
    # Initialize audio player
    print("Initializing AudioPlayer...")
    try:
        player = AudioPlayer(volume_percent=75)
        print(f"✓ AudioPlayer initialized with volume: {player.get_volume()}%\n")
    except Exception as e:
        print(f"✗ Failed to initialize AudioPlayer: {e}")
        return 1
    
    # Find test sound file
    test_sound = Path(__file__).parent / "src" / "accessibletalkingclock" / "audio" / "test_sound.wav"
    if not test_sound.exists():
        print(f"✗ Test sound not found at: {test_sound}")
        return 1
    
    print(f"Found test sound: {test_sound}\n")
    
    # Test playback
    print("Playing test sound (0.5 seconds)...")
    try:
        player.play_sound(str(test_sound))
        print("✓ Sound playback started")
        
        # Check if playing
        time.sleep(0.1)
        if player.is_playing():
            print("✓ Audio is playing")
        else:
            print("  Note: Audio may have already finished (short file)")
        
        # Wait for sound to finish
        time.sleep(0.6)
        print("✓ Playback complete\n")
        
    except Exception as e:
        print(f"✗ Error during playback: {e}")
        return 1
    
    # Test volume control
    print("Testing volume control...")
    for vol in [25, 50, 75, 100]:
        player.set_volume(vol)
        assert player.get_volume() == vol
        print(f"✓ Volume set to {vol}%")
    
    print("\n=== All Tests Passed ===")
    print("\nAudio system is working correctly!")
    print("The UI integration should allow:")
    print("  - Volume button cycles through 0%, 25%, 50%, 75%, 100%")
    print("  - Test Chime button plays the test sound")
    print("  - Audio plays without blocking the clock")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

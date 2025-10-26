# Sound Attributions

This file contains attribution information for all audio files used in the Accessible Talking Clock soundpacks.

## All Soundpacks

All sound files in this project were **procedurally generated** using the `generate_sounds.py` script included in the project.

- **Source**: Procedurally generated
- **Method**: Pure sine wave synthesis with ADSR envelopes
- **Author**: Accessible Talking Clock Project
- **License**: MIT License (same as project)
- **Generation Script**: `src/accessibletalkingclock/generate_sounds.py`

### Technical Details

**Classic Soundpack**:
- Westminster-style chime sequence using bell frequencies (E5, C5, D5, G5)
- ADSR envelope applied for natural bell decay
- **hour.wav**: 4-note sequence (2.9 seconds)
- **half.wav**: 2-note sequence (1.5 seconds)
- **quarter.wav**: Single bell tone (0.6 seconds)

**Nature Soundpack**:
- Wind chime effect using harmonious frequencies (A4, C5, E5, G5)
- Multiple tones mixed together with staggered durations
- Gentle attack and long release for natural sound
- **hour.wav**: 4-tone mixed chime (1.8 seconds)
- **half.wav**: 2-tone mixed chime (1.0 seconds)
- **quarter.wav**: Single gentle tone (0.8 seconds)

**Digital Soundpack**:
- Electronic beep sequences with clean attack/release
- Ascending frequency patterns for hour chime
- **hour.wav**: 3-tone ascending sequence (A4, C#5, E5) (0.75 seconds)
- **half.wav**: 2-tone sequence (A4, C#5) (0.4 seconds)
- **quarter.wav**: Single beep (A4) (0.1 seconds)

### Audio Specifications

- **Format**: WAV (Waveform Audio File Format)
- **Sample Rate**: 44,100 Hz
- **Bit Depth**: 16-bit
- **Channels**: Mono
- **Encoding**: PCM (Pulse Code Modulation)

### Regenerating Sounds

To regenerate the sounds (e.g., with different frequencies or durations), run:

```bash
cd accessibletalkingclock/src/accessibletalkingclock
python generate_sounds.py
```

---

**Note**: These sounds are original works created specifically for this project. They do not sample or incorporate any copyrighted material.

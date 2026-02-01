# Sound Recommendations for Accessible Talking Clock

This document contains curated recommendations for CC0 (public domain) sounds from Freesound.org for the three soundpacks.

## Classic Soundpack (Clock Chimes)

All sounds from **3bagbrew** on Freesound, CC0 license:

### Hour Chime
- **Sound ID**: 609763
- **Name**: German Grandfather Clock Tick & Chime x12.wav
- **URL**: https://freesound.org/people/3bagbrew/sounds/609763/
- **Description**: Antique German grandfather clock chiming 12 o'clock
- **Duration**: 1:11
- **License**: CC0 (Public Domain)
- **Author**: 3bagbrew
- **Notes**: We can extract just the chime portion (without ticking)

### Half-Hour Chime
- **Sound ID**: 73351
- **Name**: grandfather_clock_chimes.wav
- **URL**: https://freesound.org/people/3bagbrew/sounds/73351/
- **Description**: Grandfather clock with twelve fast chimes
- **Duration**: 0:45
- **License**: CC0 (Public Domain)
- **Author**: 3bagbrew
- **Notes**: Can extract a shorter section for half-hour

### Quarter-Hour Chime
- **Alternative Option**: Use designerschoice's third quarter chimes
- **Sound ID**: 805325
- **Name**: CLOCKChim-Samsung Galaxy Smartphone, CU_Grandfather Clock, Third Quarter Chimes
- **URL**: https://freesound.org/people/designerschoice/sounds/805325/
- **Description**: Grandfather clock's third quarter chime
- **Duration**: 0:19
- **License**: CC0 (Public Domain)
- **Author**: designerschoice

## Nature Soundpack

### Hour Chime (Wind Chimes)
**Search needed**: Wind chime sounds on Freesound with CC0 filter
- **Search URL**: https://freesound.org/search/?q=wind+chime&f=license%3A%22Creative+Commons+0%22
- **Recommendation**: Look for longer, melodic wind chime sequences

### Half-Hour Chime (Bird Call)
**Search needed**: Short bird call sounds on Freesound with CC0 filter
- **Search URL**: https://freesound.org/search/?q=bird+call&f=license%3A%22Creative+Commons+0%22
- **Alternative source**: Pixabay CC0 bird sounds
- **Recommendation**: Cheerful, short bird chirp (1-2 seconds)

### Quarter-Hour Chime (Soft Chime)
**Search needed**: Gentle chime or bell sounds
- **Search URL**: https://freesound.org/search/?q=gentle+bell&f=license%3A%22Creative+Commons+0%22
- **Recommendation**: Single soft bell tone or tingsha

## Digital Soundpack

### Hour Chime (Multi-Tone Sequence)
**Pack**: Erokia - Electronic Samples Misc (CC0)
- **Pack URL**: https://freesound.org/people/Erokia/packs/26717/
- **License**: CC0 (Public Domain)
- **Author**: Erokia
- **Notes**: Contains various electronic alarm/notification sounds

### Half-Hour Chime (Two-Tone Beep)
**Search needed**: Two-tone digital beep
- **Search URL**: https://freesound.org/search/?q=beep+two+tone&f=license%3A%22Creative+Commons+0%22
- **Alternative**: Generate programmatically (440Hz + 554Hz tones)

### Quarter-Hour Chime (Single Beep)
**Search needed**: Short single beep
- **Search URL**: https://freesound.org/search/?q=beep+short&f=license%3A%22Creative+Commons+0%22
- **Alternative**: Use existing test_sound.wav from Phase 2

## Download Instructions

1. Create a free Freesound.org account (required to download)
2. Search for each sound by ID or URL
3. Download in WAV format (highest quality available)
4. Place in appropriate soundpack directory
5. Update ATTRIBUTIONS.md with sound details

## Audio Processing Notes

Some sounds may need processing:
- **Trim silence**: Remove leading/trailing silence
- **Normalize volume**: Ensure consistent loudness across sounds
- **Extract segments**: Some longer sounds may need specific portions extracted
- **Format conversion**: Convert to consistent format (16-bit, 44.1kHz WAV)

Tools for processing:
- **Audacity** (free, open-source): https://www.audacityteam.org/
- **FFmpeg** (command-line): Can automate batch processing
- **sound_lib** (Python): Could process programmatically if needed

## Fallback Strategy

If we cannot find suitable sounds:
1. **Classic**: Use existing test beep at different pitches
2. **Nature**: Generate simple tones with envelope shaping
3. **Digital**: Generate tones programmatically using sound_lib

## License Compliance

All recommended sounds are CC0 (Public Domain):
- ✅ No attribution required (but we'll provide it anyway in ATTRIBUTIONS.md)
- ✅ Free for commercial use
- ✅ Can be modified
- ✅ No restrictions

## Next Steps

1. Create Freesound account
2. Download recommended classic chimes (already identified)
3. Search and download nature sounds (wind chimes, bird)
4. Search and download digital beeps (or generate)
5. Process sounds if needed (trim, normalize)
6. Place in correct directories
7. Update ATTRIBUTIONS.md with details
8. Test all sounds in application

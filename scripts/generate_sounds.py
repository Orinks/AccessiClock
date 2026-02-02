#!/usr/bin/env python3
"""
Generate placeholder sound files for AccessiClock clock packs.

This script creates simple sine wave tones as placeholder sounds.
For production, these should be replaced with proper audio files.
"""

import math
import struct
import wave
from pathlib import Path


def generate_tone(
    filename: Path,
    frequency: float = 440.0,
    duration: float = 0.5,
    sample_rate: int = 44100,
    volume: float = 0.5,
) -> None:
    """
    Generate a simple sine wave tone WAV file.
    
    Args:
        filename: Output file path.
        frequency: Tone frequency in Hz.
        duration: Duration in seconds.
        sample_rate: Sample rate in Hz.
        volume: Volume from 0.0 to 1.0.
    """
    num_samples = int(sample_rate * duration)
    
    # Generate samples
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        # Apply fade in/out to avoid clicks
        fade_samples = int(sample_rate * 0.01)  # 10ms fade
        if i < fade_samples:
            fade = i / fade_samples
        elif i > num_samples - fade_samples:
            fade = (num_samples - i) / fade_samples
        else:
            fade = 1.0
        
        value = volume * fade * math.sin(2 * math.pi * frequency * t)
        # Convert to 16-bit integer
        samples.append(int(value * 32767))
    
    # Write WAV file
    filename.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(filename), 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        
        for sample in samples:
            wav.writeframes(struct.pack('<h', sample))
    
    print(f"Generated: {filename}")


def generate_chime(
    filename: Path,
    base_freq: float = 440.0,
    num_notes: int = 1,
    note_duration: float = 0.3,
    gap: float = 0.1,
) -> None:
    """
    Generate a simple chime sound with multiple notes.
    
    Args:
        filename: Output file path.
        base_freq: Base frequency in Hz.
        num_notes: Number of notes in the chime.
        note_duration: Duration of each note.
        gap: Gap between notes.
    """
    sample_rate = 44100
    
    samples = []
    note_samples = int(sample_rate * note_duration)
    gap_samples = int(sample_rate * gap)
    
    # Musical interval: major chord (1, 5/4, 3/2)
    intervals = [1.0, 1.25, 1.5, 2.0]  # Root, major 3rd, 5th, octave
    
    for note in range(num_notes):
        freq = base_freq * intervals[note % len(intervals)]
        
        for i in range(note_samples):
            t = i / sample_rate
            # Exponential decay
            decay = math.exp(-3 * t / note_duration)
            # Fade in/out
            fade_samples = int(sample_rate * 0.01)
            if i < fade_samples:
                fade = i / fade_samples
            elif i > note_samples - fade_samples:
                fade = (note_samples - i) / fade_samples
            else:
                fade = 1.0
            
            value = 0.5 * fade * decay * math.sin(2 * math.pi * freq * t)
            samples.append(int(value * 32767))
        
        # Add gap (silence)
        if note < num_notes - 1:
            samples.extend([0] * gap_samples)
    
    # Write WAV file
    filename.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(filename), 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        for sample in samples:
            wav.writeframes(struct.pack('<h', sample))
    
    print(f"Generated: {filename}")


def generate_default_pack(base_dir: Path) -> None:
    """Generate sounds for the default clock pack."""
    pack_dir = base_dir / "default"
    
    # Hour chime: 4 notes
    generate_chime(pack_dir / "hour.wav", base_freq=523.25, num_notes=4)
    
    # Half hour: 2 notes
    generate_chime(pack_dir / "half_hour.wav", base_freq=523.25, num_notes=2)
    
    # Quarter hour: 1 note
    generate_chime(pack_dir / "quarter_hour.wav", base_freq=523.25, num_notes=1)
    
    # Preview: same as hour
    generate_chime(pack_dir / "preview.wav", base_freq=523.25, num_notes=4)
    
    # Startup: ascending arpeggio
    generate_chime(pack_dir / "startup.wav", base_freq=392.0, num_notes=4, note_duration=0.2)


def generate_digital_pack(base_dir: Path) -> None:
    """Generate sounds for the digital clock pack."""
    pack_dir = base_dir / "digital"
    
    # Hour: 3 beeps
    generate_chime(pack_dir / "hour.wav", base_freq=880.0, num_notes=3, note_duration=0.15, gap=0.1)
    
    # Half hour: 2 beeps
    generate_chime(pack_dir / "half_hour.wav", base_freq=880.0, num_notes=2, note_duration=0.15, gap=0.1)
    
    # Quarter hour: 1 beep
    generate_tone(pack_dir / "quarter_hour.wav", frequency=880.0, duration=0.15)
    
    # Preview: same as hour
    generate_chime(pack_dir / "preview.wav", base_freq=880.0, num_notes=3, note_duration=0.15, gap=0.1)
    
    # Startup: quick ascending beeps
    generate_chime(pack_dir / "startup.wav", base_freq=660.0, num_notes=3, note_duration=0.1, gap=0.05)


def generate_westminster_pack(base_dir: Path) -> None:
    """Generate sounds for the Westminster clock pack."""
    pack_dir = base_dir / "westminster"
    
    # Westminster chime frequencies (E4, G#4, F#4, B3 sequence)
    # Simplified version using base frequency
    
    # Hour: 4 Westminster-style notes
    generate_chime(pack_dir / "hour.wav", base_freq=329.63, num_notes=4, note_duration=0.5, gap=0.2)
    
    # Half hour: 2 notes
    generate_chime(pack_dir / "half_hour.wav", base_freq=329.63, num_notes=2, note_duration=0.5, gap=0.2)
    
    # Quarter hour: 1 note
    generate_chime(pack_dir / "quarter_hour.wav", base_freq=329.63, num_notes=1, note_duration=0.5)
    
    # Preview: same as hour
    generate_chime(pack_dir / "preview.wav", base_freq=329.63, num_notes=4, note_duration=0.5, gap=0.2)
    
    # Startup: single deep tone
    generate_tone(pack_dir / "startup.wav", frequency=261.63, duration=1.0)


def main():
    """Generate all clock pack sounds."""
    # Determine base directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    clocks_dir = project_dir / "src" / "accessiclock" / "clocks"
    
    print(f"Generating clock pack sounds in: {clocks_dir}")
    print()
    
    print("=== Default Pack ===")
    generate_default_pack(clocks_dir)
    print()
    
    print("=== Digital Pack ===")
    generate_digital_pack(clocks_dir)
    print()
    
    print("=== Westminster Pack ===")
    generate_westminster_pack(clocks_dir)
    print()
    
    print("Done! All placeholder sounds generated.")
    print("\nNote: These are simple placeholder tones.")
    print("For better quality, replace with proper audio files.")


if __name__ == "__main__":
    main()

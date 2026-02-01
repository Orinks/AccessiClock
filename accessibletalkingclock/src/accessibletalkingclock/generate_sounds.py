"""
Generate synthetic chime sounds for soundpacks.

Creates simple but pleasant chime sounds using synthesized tones.
This provides a quick way to populate soundpacks without requiring external audio files.
"""

import wave
import math
import struct
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


def generate_tone(
    frequency: float,
    duration: float,
    sample_rate: int = 44100,
    amplitude: float = 0.5
) -> List[float]:
    """
    Generate a pure sine wave tone.
    
    Args:
        frequency: Frequency in Hz
        duration: Duration in seconds
        sample_rate: Sample rate in Hz (default: 44100)
        amplitude: Amplitude 0.0-1.0 (default: 0.5)
        
    Returns:
        List of sample values
    """
    num_samples = int(duration * sample_rate)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = amplitude * math.sin(2 * math.pi * frequency * t)
        samples.append(sample)
    
    return samples


def apply_envelope(
    samples: List[float],
    attack: float = 0.01,
    decay: float = 0.1,
    sustain: float = 0.7,
    release: float = 0.2,
    sample_rate: int = 44100
) -> List[float]:
    """
    Apply ADSR envelope to samples for more natural sound.
    
    Args:
        samples: Audio samples
        attack: Attack time in seconds
        decay: Decay time in seconds
        sustain: Sustain level (0.0-1.0)
        release: Release time in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        Samples with envelope applied
    """
    num_samples = len(samples)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    
    sustain_samples = num_samples - attack_samples - decay_samples - release_samples
    if sustain_samples < 0:
        sustain_samples = 0
    
    enveloped = []
    
    for i, sample in enumerate(samples):
        if i < attack_samples:
            # Attack: ramp up from 0 to 1
            envelope = i / attack_samples
        elif i < attack_samples + decay_samples:
            # Decay: ramp down from 1 to sustain level
            t = (i - attack_samples) / decay_samples
            envelope = 1.0 - (1.0 - sustain) * t
        elif i < attack_samples + decay_samples + sustain_samples:
            # Sustain: hold at sustain level
            envelope = sustain
        else:
            # Release: ramp down from sustain to 0
            t = (i - attack_samples - decay_samples - sustain_samples) / release_samples
            envelope = sustain * (1.0 - t)
        
        enveloped.append(sample * envelope)
    
    return enveloped


def mix_samples(samples_list: List[List[float]]) -> List[float]:
    """
    Mix multiple sample lists together.
    
    Args:
        samples_list: List of sample lists to mix
        
    Returns:
        Mixed samples
    """
    if not samples_list:
        return []
    
    max_length = max(len(s) for s in samples_list)
    mixed = [0.0] * max_length
    
    for samples in samples_list:
        for i, sample in enumerate(samples):
            mixed[i] += sample / len(samples_list)  # Average to prevent clipping
    
    return mixed


def save_wav(samples: List[float], filename: Path, sample_rate: int = 44100):
    """
    Save samples to WAV file.
    
    Args:
        samples: Audio samples
        filename: Output filename
        sample_rate: Sample rate in Hz
    """
    logger.info(f"Saving {len(samples)} samples to {filename}")
    
    # Convert to 16-bit integers
    max_amplitude = 32767
    int_samples = [int(s * max_amplitude) for s in samples]
    
    # Pack samples
    packed_samples = b''.join(struct.pack('<h', s) for s in int_samples)
    
    # Write WAV file
    with wave.open(str(filename), 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(packed_samples)
    
    logger.info(f"Saved {filename} successfully")


def generate_classic_chimes(output_dir: Path):
    """
    Generate classic bell-like chimes.
    
    Args:
        output_dir: Directory to save files (e.g., resources/sounds/classic/)
    """
    logger.info("Generating classic chimes")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Hour chime: Westminster-style sequence (E, C, D, G)
    notes = [
        (659.25, 0.5),  # E5
        (523.25, 0.5),  # C5
        (587.33, 0.5),  # D5
        (783.99, 1.0),  # G5 (longer)
    ]
    
    all_samples = []
    for freq, duration in notes:
        tone = generate_tone(freq, duration, amplitude=0.4)
        tone = apply_envelope(tone, attack=0.01, decay=0.1, sustain=0.7, release=0.3)
        all_samples.extend(tone)
        # Add short silence between notes
        all_samples.extend([0.0] * 4410)  # 0.1 seconds
    
    save_wav(all_samples, output_dir / "hour.wav")
    
    # Half-hour chime: Two bells (E, C)
    notes = [
        (659.25, 0.5),  # E5
        (523.25, 0.8),  # C5 (longer)
    ]
    
    all_samples = []
    for freq, duration in notes:
        tone = generate_tone(freq, duration, amplitude=0.4)
        tone = apply_envelope(tone, attack=0.01, decay=0.1, sustain=0.7, release=0.3)
        all_samples.extend(tone)
        all_samples.extend([0.0] * 4410)
    
    save_wav(all_samples, output_dir / "half.wav")
    
    # Quarter chime: Single bell (E)
    tone = generate_tone(659.25, 0.6, amplitude=0.4)
    tone = apply_envelope(tone, attack=0.01, decay=0.1, sustain=0.7, release=0.3)
    save_wav(tone, output_dir / "quarter.wav")


def generate_nature_chimes(output_dir: Path):
    """
    Generate nature-inspired chimes (wind chime effect).
    
    Args:
        output_dir: Directory to save files
    """
    logger.info("Generating nature chimes")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Hour chime: Multiple harmonious tones (wind chime effect)
    frequencies = [440.0, 523.25, 659.25, 783.99]  # A4, C5, E5, G5
    durations = [1.5, 1.6, 1.7, 1.8]  # Slightly staggered
    
    all_tones = []
    for freq, duration in zip(frequencies, durations):
        tone = generate_tone(freq, duration, amplitude=0.2)
        tone = apply_envelope(tone, attack=0.02, decay=0.2, sustain=0.6, release=0.5)
        all_tones.append(tone)
    
    mixed = mix_samples(all_tones)
    save_wav(mixed, output_dir / "hour.wav")
    
    # Half-hour: Two harmonious tones
    frequencies = [523.25, 659.25]  # C5, E5
    all_tones = []
    for freq in frequencies:
        tone = generate_tone(freq, 1.0, amplitude=0.3)
        tone = apply_envelope(tone, attack=0.02, decay=0.2, sustain=0.6, release=0.4)
        all_tones.append(tone)
    
    mixed = mix_samples(all_tones)
    save_wav(mixed, output_dir / "half.wav")
    
    # Quarter: Single gentle tone
    tone = generate_tone(659.25, 0.8, amplitude=0.3)
    tone = apply_envelope(tone, attack=0.02, decay=0.2, sustain=0.6, release=0.4)
    save_wav(tone, output_dir / "quarter.wav")


def generate_digital_chimes(output_dir: Path):
    """
    Generate digital beep chimes.
    
    Args:
        output_dir: Directory to save files
    """
    logger.info("Generating digital chimes")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Hour chime: Three-tone sequence (ascending)
    frequencies = [440.0, 554.37, 659.25]  # A4, C#5, E5
    all_samples = []
    
    for freq in frequencies:
        tone = generate_tone(freq, 0.2, amplitude=0.5)
        tone = apply_envelope(tone, attack=0.001, decay=0.05, sustain=0.8, release=0.05)
        all_samples.extend(tone)
        all_samples.extend([0.0] * 2205)  # 0.05 seconds silence
    
    save_wav(all_samples, output_dir / "hour.wav")
    
    # Half-hour: Two-tone beep
    frequencies = [440.0, 554.37]
    all_samples = []
    
    for freq in frequencies:
        tone = generate_tone(freq, 0.15, amplitude=0.5)
        tone = apply_envelope(tone, attack=0.001, decay=0.05, sustain=0.8, release=0.05)
        all_samples.extend(tone)
        all_samples.extend([0.0] * 2205)
    
    save_wav(all_samples, output_dir / "half.wav")
    
    # Quarter: Single beep
    tone = generate_tone(440.0, 0.1, amplitude=0.5)
    tone = apply_envelope(tone, attack=0.001, decay=0.05, sustain=0.8, release=0.05)
    save_wav(tone, output_dir / "quarter.wav")


def generate_all_soundpacks(base_dir: Path):
    """
    Generate all soundpack chimes.
    
    Args:
        base_dir: Base sounds directory (e.g., resources/sounds/)
    """
    logger.info(f"Generating all soundpacks in {base_dir}")
    
    generate_classic_chimes(base_dir / "classic")
    generate_nature_chimes(base_dir / "nature")
    generate_digital_chimes(base_dir / "digital")
    
    logger.info("All soundpacks generated successfully")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Determine path to sounds directory
    script_dir = Path(__file__).parent
    sounds_dir = script_dir / "resources" / "sounds"
    
    print(f"Generating soundpack chimes in: {sounds_dir}")
    generate_all_soundpacks(sounds_dir)
    print("\nDone! You can now test the sounds in the application.")

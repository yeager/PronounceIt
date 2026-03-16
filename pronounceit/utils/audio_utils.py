"""Audio utility functions."""

import wave
import struct

import numpy as np


def write_wav(filepath, audio_data, sample_rate=44100):
    """Skriv numpy-array till WAV-fil."""
    # Convert float32 to int16
    audio_int16 = (audio_data * 32767).astype(np.int16)

    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())


def read_wav(filepath):
    """Läs WAV-fil till numpy float32-array.

    Returns:
        (audio_data, sample_rate) tuple
    """
    with wave.open(filepath, "r") as wf:
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        return audio, sample_rate


def normalize(audio_data):
    """Normalisera ljudnivå till [-1, 1]."""
    peak = np.max(np.abs(audio_data))
    if peak > 0:
        return audio_data / peak
    return audio_data

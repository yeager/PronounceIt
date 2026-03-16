"""Tests for spectrogram analyzer."""

import numpy as np
import pytest

from pronounceit.audio.analyzer import SpectrogramAnalyzer


def test_compute_basic():
    """Test basic spectrogram computation."""
    analyzer = SpectrogramAnalyzer()
    # Generate a simple sine wave
    sr = 44100
    duration = 0.5
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)

    result = analyzer.compute(audio, sr)

    assert result.frequencies is not None
    assert result.times is not None
    assert result.power is not None
    assert result.sample_rate == sr
    assert len(result.frequencies) > 0
    assert len(result.times) > 0


def test_compute_short_audio():
    """Test with very short audio (shorter than nperseg)."""
    analyzer = SpectrogramAnalyzer()
    audio = np.zeros(100, dtype=np.float32)
    result = analyzer.compute(audio, 44100)
    assert result.power is not None


def test_compute_silence():
    """Test with silent audio."""
    analyzer = SpectrogramAnalyzer()
    audio = np.zeros(44100, dtype=np.float32)
    result = analyzer.compute(audio, 44100)
    # Power should be very low
    assert np.max(result.power) < 0

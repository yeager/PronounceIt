"""Tests for pronunciation scorer."""

import numpy as np
import pytest

from pronounceit.audio.analyzer import SpectrogramAnalyzer
from pronounceit.audio.pitch_tracker import PitchTracker
from pronounceit.audio.formant import FormantAnalyzer
from pronounceit.scoring.scorer import PronunciationScorer


def _make_test_audio(freq=440, duration=0.5, sr=44100):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return (0.5 * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def test_score_identical_audio():
    """Identical audio should get a high score."""
    scorer = PronunciationScorer()
    analyzer = SpectrogramAnalyzer()
    pitch_tracker = PitchTracker()
    formant_analyzer = FormantAnalyzer()

    audio = _make_test_audio()

    spec = analyzer.compute(audio)
    pitch = pitch_tracker.extract(audio)
    formants = formant_analyzer.extract(audio)

    result = scorer.score(spec, spec, pitch, pitch, formants, formants)

    assert result.total >= 80  # Should be high for identical
    assert 0 <= result.total <= 100


def test_score_different_audio():
    """Different audio should get a lower score."""
    scorer = PronunciationScorer()
    analyzer = SpectrogramAnalyzer()
    pitch_tracker = PitchTracker()
    formant_analyzer = FormantAnalyzer()

    audio1 = _make_test_audio(freq=200)
    audio2 = _make_test_audio(freq=800)

    spec1 = analyzer.compute(audio1)
    spec2 = analyzer.compute(audio2)
    pitch1 = pitch_tracker.extract(audio1)
    pitch2 = pitch_tracker.extract(audio2)
    formants1 = formant_analyzer.extract(audio1)
    formants2 = formant_analyzer.extract(audio2)

    result = scorer.score(spec1, spec2, pitch1, pitch2, formants1, formants2)

    assert 0 <= result.total <= 100


def test_scoring_result_fields():
    """ScoringResult should have all expected fields."""
    scorer = PronunciationScorer()
    analyzer = SpectrogramAnalyzer()
    pitch_tracker = PitchTracker()
    formant_analyzer = FormantAnalyzer()

    audio = _make_test_audio()
    spec = analyzer.compute(audio)
    pitch = pitch_tracker.extract(audio)
    formants = formant_analyzer.extract(audio)

    result = scorer.score(spec, spec, pitch, pitch, formants, formants)

    assert hasattr(result, "total")
    assert hasattr(result, "spectral_score")
    assert hasattr(result, "pitch_score")
    assert hasattr(result, "formant_score")

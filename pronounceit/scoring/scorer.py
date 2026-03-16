"""Pronunciation scoring engine."""

import numpy as np
from pronounceit.data.models import ScoringResult
from pronounceit.audio.comparator import SpectrogramComparator


class PronunciationScorer:
    """Beräknar uttalspoäng baserat på spektral-, tonhöjds- och formantlikhet.

    Vikter:
      - Spektral likhet: 40%
      - Tonhöjdsnoggrannhet: 30%
      - Formantnoggrannhet: 30%
    """

    SPECTRAL_WEIGHT = 0.4
    PITCH_WEIGHT = 0.3
    FORMANT_WEIGHT = 0.3

    def __init__(self):
        self.comparator = SpectrogramComparator()

    def score(self, user_spec, ref_spec, user_pitch, ref_pitch,
              user_formants, ref_formants, language="sv"):
        """Beräkna kompositpoäng 0-100.

        Args:
            user_spec, ref_spec: SpectrogramResult
            user_pitch, ref_pitch: PitchResult
            user_formants, ref_formants: FormantResult
            language: Språkkod

        Returns:
            ScoringResult
        """
        spectral = self._score_spectral(user_spec, ref_spec)
        pitch = self._score_pitch(user_pitch, ref_pitch)
        formant = self._score_formant(user_formants, ref_formants)

        total = (
            self.SPECTRAL_WEIGHT * spectral
            + self.PITCH_WEIGHT * pitch
            + self.FORMANT_WEIGHT * formant
        )

        return ScoringResult(
            total=round(total, 1),
            spectral_score=round(spectral, 1),
            pitch_score=round(pitch, 1),
            formant_score=round(formant, 1),
            details={"language": language},
        )

    def _score_spectral(self, user_spec, ref_spec):
        """Poängsätt spektral likhet via DTW-avstånd."""
        result = self.comparator.compare(user_spec, ref_spec)
        # Normalize distance to 0-100 score (lower distance = higher score)
        # Typical DTW distances range 0-500; map to score
        max_distance = 300.0
        score = max(0, 100 * (1 - result.distance / max_distance))
        return min(100, score)

    def _score_pitch(self, user_pitch, ref_pitch):
        """Poängsätt tonhöjdskonturens likhet via korrelation."""
        user_f0 = user_pitch.frequencies
        ref_f0 = ref_pitch.frequencies

        # Match lengths
        min_len = min(len(user_f0), len(ref_f0))
        if min_len == 0:
            return 50.0

        u = user_f0[:min_len]
        r = ref_f0[:min_len]

        # Only compare voiced frames
        voiced = (u > 0) & (r > 0)
        if np.sum(voiced) < 3:
            return 50.0

        u_voiced = u[voiced]
        r_voiced = r[voiced]

        # Correlation
        if np.std(u_voiced) < 1e-6 or np.std(r_voiced) < 1e-6:
            return 50.0

        corr = np.corrcoef(u_voiced, r_voiced)[0, 1]
        if np.isnan(corr):
            return 50.0

        # Map correlation (-1 to 1) to score (0 to 100)
        score = max(0, (corr + 1) / 2 * 100)
        return min(100, score)

    def _score_formant(self, user_formants, ref_formants):
        """Poängsätt formantprecision (F1, F2)."""
        min_len = min(len(user_formants.f1), len(ref_formants.f1))
        if min_len == 0:
            return 50.0

        f1_diff = np.abs(user_formants.f1[:min_len] - ref_formants.f1[:min_len])
        f2_diff = np.abs(user_formants.f2[:min_len] - ref_formants.f2[:min_len])

        # Filter out zero (unvoiced) frames
        valid = (user_formants.f1[:min_len] > 0) & (ref_formants.f1[:min_len] > 0)
        if np.sum(valid) < 2:
            return 50.0

        avg_f1_diff = np.mean(f1_diff[valid])
        avg_f2_diff = np.mean(f2_diff[valid])

        # Typical formant differences: 0-500 Hz
        max_diff = 400.0
        f1_score = max(0, 100 * (1 - avg_f1_diff / max_diff))
        f2_score = max(0, 100 * (1 - avg_f2_diff / max_diff))

        return min(100, (f1_score + f2_score) / 2)

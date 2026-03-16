"""Formant analysis using LPC (Linear Predictive Coding)."""

import numpy as np
from scipy.signal import lfilter, lpc


class FormantResult:
    """Container for formant analysis data."""

    def __init__(self, times, f1, f2, f3):
        self.times = times
        self.f1 = f1
        self.f2 = f2
        self.f3 = f3


class FormantAnalyzer:
    """LPC-baserad formantanalys.

    Extraherar F1, F2, F3 som är avgörande för vokalidentifiering.
    Särskilt viktigt för svenska med 17-18 vokalfonem.
    """

    def __init__(self, lpc_order=12, frame_size=2048, hop_size=512):
        self.lpc_order = lpc_order
        self.frame_size = frame_size
        self.hop_size = hop_size

    def extract(self, audio_data, sample_rate=44100):
        """Extrahera formantfrekvenser (F1, F2, F3) per ram.

        Returns:
            FormantResult med formantserier.
        """
        n_frames = max(1, (len(audio_data) - self.frame_size) // self.hop_size + 1)
        times = np.zeros(n_frames)
        f1 = np.zeros(n_frames)
        f2 = np.zeros(n_frames)
        f3 = np.zeros(n_frames)

        for i in range(n_frames):
            start = i * self.hop_size
            frame = audio_data[start : start + self.frame_size]

            if len(frame) < self.frame_size:
                frame = np.pad(frame, (0, self.frame_size - len(frame)))

            times[i] = start / sample_rate
            formants = self._extract_frame_formants(frame, sample_rate)
            if len(formants) >= 1:
                f1[i] = formants[0]
            if len(formants) >= 2:
                f2[i] = formants[1]
            if len(formants) >= 3:
                f3[i] = formants[2]

        return FormantResult(times, f1, f2, f3)

    def _extract_frame_formants(self, frame, sample_rate):
        """Extrahera formanter från en enskild ram via LPC."""
        # Pre-emphasis
        pre_emph = np.append(frame[0], frame[1:] - 0.97 * frame[:-1])

        # Window
        windowed = pre_emph * np.hanning(len(pre_emph))

        # Energy check
        if np.sum(windowed ** 2) < 1e-6:
            return []

        try:
            # LPC coefficients
            a = lpc(windowed, self.lpc_order)

            # Find roots of the LPC polynomial
            roots = np.roots(a)

            # Keep roots inside the unit circle with positive imaginary part
            roots = roots[np.imag(roots) > 0]
            roots = roots[np.abs(roots) < 1.0]

            if len(roots) == 0:
                return []

            # Convert to frequencies
            angles = np.angle(roots)
            freqs = angles * (sample_rate / (2 * np.pi))

            # Sort and filter to speech range (200-5000 Hz)
            freqs = np.sort(freqs)
            freqs = freqs[(freqs > 200) & (freqs < 5000)]

            return freqs[:3].tolist()
        except Exception:
            return []

"""Pitch (F0) tracking using autocorrelation."""

import numpy as np


class PitchResult:
    """Container for pitch tracking data."""

    def __init__(self, times, frequencies, confidence):
        self.times = times
        self.frequencies = frequencies  # F0 in Hz, 0 = unvoiced
        self.confidence = confidence


class PitchTracker:
    """Real-time grundtonsextraktion med autokorrelation.

    Implementerar en enkel men robust autokorrelationsbaserad
    F0-detektor, lämplig för talanalys (80-400 Hz).
    """

    def __init__(self, min_f0=80, max_f0=400, frame_size=2048, hop_size=512):
        self.min_f0 = min_f0
        self.max_f0 = max_f0
        self.frame_size = frame_size
        self.hop_size = hop_size

    def extract(self, audio_data, sample_rate=44100):
        """Extrahera F0-kontur från ljuddata.

        Returns:
            PitchResult med tider, frekvenser och konfidens.
        """
        min_lag = int(sample_rate / self.max_f0)
        max_lag = int(sample_rate / self.min_f0)

        n_frames = max(1, (len(audio_data) - self.frame_size) // self.hop_size + 1)
        times = np.zeros(n_frames)
        frequencies = np.zeros(n_frames)
        confidence = np.zeros(n_frames)

        for i in range(n_frames):
            start = i * self.hop_size
            frame = audio_data[start : start + self.frame_size]

            if len(frame) < self.frame_size:
                frame = np.pad(frame, (0, self.frame_size - len(frame)))

            times[i] = start / sample_rate
            f0, conf = self._autocorrelation_f0(frame, sample_rate, min_lag, max_lag)
            frequencies[i] = f0
            confidence[i] = conf

        return PitchResult(times, frequencies, confidence)

    def _autocorrelation_f0(self, frame, sample_rate, min_lag, max_lag):
        """Beräkna F0 med autokorrelation för en ram."""
        # Windowing
        windowed = frame * np.hanning(len(frame))

        # Energy check
        energy = np.sum(windowed ** 2)
        if energy < 1e-6:
            return 0.0, 0.0

        # Normalized autocorrelation
        corr = np.correlate(windowed, windowed, mode="full")
        corr = corr[len(corr) // 2:]  # Keep positive lags only

        if corr[0] == 0:
            return 0.0, 0.0

        corr = corr / corr[0]  # Normalize

        # Find peak in valid lag range
        max_lag = min(max_lag, len(corr) - 1)
        if min_lag >= max_lag:
            return 0.0, 0.0

        search_region = corr[min_lag:max_lag]
        if len(search_region) == 0:
            return 0.0, 0.0

        peak_idx = np.argmax(search_region) + min_lag
        peak_val = corr[peak_idx]

        # Confidence threshold
        if peak_val < 0.3:
            return 0.0, 0.0

        f0 = sample_rate / peak_idx
        return f0, peak_val

"""Spectrogram computation using scipy."""

import numpy as np
from scipy import signal


class SpectrogramResult:
    """Container for spectrogram data."""

    def __init__(self, frequencies, times, power, sample_rate):
        self.frequencies = frequencies
        self.times = times
        self.power = power  # Power in dB
        self.sample_rate = sample_rate


class SpectrogramAnalyzer:
    """Beräknar spektrogram med scipy.signal.spectrogram."""

    def __init__(self, nperseg=512, noverlap=384):
        self.nperseg = nperseg
        self.noverlap = noverlap

    def compute(self, audio_data, sample_rate=44100):
        """Beräkna spektrogram från ljuddata.

        Args:
            audio_data: numpy array med ljudsamplar (float32, -1 till 1)
            sample_rate: samplingsfrekvens

        Returns:
            SpectrogramResult med frekvenser, tider och effekt i dB
        """
        if len(audio_data) < self.nperseg:
            # Pad short audio
            audio_data = np.pad(audio_data, (0, self.nperseg - len(audio_data)))

        freqs, times, Sxx = signal.spectrogram(
            audio_data,
            fs=sample_rate,
            nperseg=self.nperseg,
            noverlap=self.noverlap,
            window="hann",
        )

        # Convert to dB, avoid log(0)
        power_db = 10 * np.log10(Sxx + 1e-10)

        return SpectrogramResult(freqs, times, power_db, sample_rate)

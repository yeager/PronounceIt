"""Dynamic Time Warping comparison of spectrograms."""

import numpy as np


class ComparisonResult:
    """Result of spectrogram comparison."""

    def __init__(self, distance, alignment_path, per_frame_distance):
        self.distance = distance  # Overall DTW distance (0 = perfect)
        self.alignment_path = alignment_path  # List of (i, j) pairs
        self.per_frame_distance = per_frame_distance  # Per-frame costs


class SpectrogramComparator:
    """Jämför spektrogram med Dynamic Time Warping (DTW).

    DTW hanterar att användaren talar i annan hastighet
    än referensen. Sakoe-Chiba band begränsar beräkningstiden.
    """

    def __init__(self, band_width_ratio=0.2):
        self.band_width_ratio = band_width_ratio

    def compare(self, user_spec, ref_spec):
        """Jämför användarens spektrogram med referens.

        Args:
            user_spec: SpectrogramResult från användaren
            ref_spec: SpectrogramResult referens

        Returns:
            ComparisonResult med DTW-avstånd och alignment.
        """
        # Use power spectrograms, transpose to (time, freq)
        user_matrix = user_spec.power.T
        ref_matrix = ref_spec.power.T

        n = len(user_matrix)
        m = len(ref_matrix)

        if n == 0 or m == 0:
            return ComparisonResult(float("inf"), [], np.array([]))

        # Sakoe-Chiba band width
        band = max(1, int(max(n, m) * self.band_width_ratio))

        # Cost matrix
        cost = self._frame_distance_matrix(user_matrix, ref_matrix)

        # DTW with band constraint
        dtw = np.full((n + 1, m + 1), float("inf"))
        dtw[0, 0] = 0.0

        for i in range(1, n + 1):
            j_start = max(1, i - band)
            j_end = min(m, i + band) + 1
            for j in range(j_start, j_end):
                dtw[i, j] = cost[i - 1, j - 1] + min(
                    dtw[i - 1, j],      # insertion
                    dtw[i, j - 1],      # deletion
                    dtw[i - 1, j - 1],  # match
                )

        total_distance = dtw[n, m]

        # Backtrace
        path = self._backtrace(dtw, n, m)

        # Per-frame distance
        per_frame = np.array([cost[i, j] for i, j in path]) if path else np.array([])

        return ComparisonResult(total_distance, path, per_frame)

    def _frame_distance_matrix(self, A, B):
        """Beräkna euklidiskt avstånd mellan alla rampar."""
        n, m = len(A), len(B)
        cost = np.zeros((n, m))
        for i in range(n):
            for j in range(m):
                diff = A[i] - B[j]
                cost[i, j] = np.sqrt(np.mean(diff ** 2))
        return cost

    def _backtrace(self, dtw, n, m):
        """Spåra optimal alignment-väg bakåt."""
        path = []
        i, j = n, m
        while i > 0 and j > 0:
            path.append((i - 1, j - 1))
            candidates = [
                (dtw[i - 1, j - 1], i - 1, j - 1),
                (dtw[i - 1, j], i - 1, j),
                (dtw[i, j - 1], i, j - 1),
            ]
            _, i, j = min(candidates, key=lambda x: x[0])
        path.reverse()
        return path

"""Pitch contour overlay for reference and user recordings."""

import numpy as np
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

import matplotlib
matplotlib.use("GTK4Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg

from pronounceit.i18n import _


class PitchView(Gtk.Box):
    """Visar tonhöjdskontur (F0) för referens och användare.

    Överlappande visning ger omedelbar visuell feedback
    på intonationsmönster.
    """

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)

        self.fig, self.ax = plt.subplots(figsize=(10, 2), dpi=100)
        self.fig.patch.set_facecolor("#1e1e24")
        self.fig.subplots_adjust(left=0.06, right=0.98, top=0.85, bottom=0.2)
        self.ax.set_facecolor("#1e1e24")
        self.ax.set_title(_("Tonhöjdskontur (F0)"), fontsize=10, color="white")
        self.ax.set_xlabel(_("Time (s)"), fontsize=8, color="white")
        self.ax.set_ylabel(_("Hz"), fontsize=8, color="white")
        self.ax.tick_params(colors="white", labelsize=7)

        self.canvas = FigureCanvasGTK4Agg(self.fig)
        self.canvas.set_size_request(800, 150)
        self.append(self.canvas)

        self._ref_line = None
        self._user_line = None

    def update_reference(self, pitch_result):
        """Visa referensens tonhöjdskontur."""
        self.ax.clear()
        self.ax.set_facecolor("#1e1e24")
        self.ax.set_title(_("Tonhöjdskontur (F0)"), fontsize=10, color="white")
        self.ax.set_xlabel(_("Time (s)"), fontsize=8, color="white")
        self.ax.set_ylabel(_("Hz"), fontsize=8, color="white")
        self.ax.tick_params(colors="white", labelsize=7)

        # Only plot voiced frames
        voiced = pitch_result.frequencies > 0
        if np.any(voiced):
            times = pitch_result.times[voiced]
            freqs = pitch_result.frequencies[voiced]
            self.ax.plot(times, freqs, "o-", color="#4fc3f7", markersize=2,
                         linewidth=1.5, label=_("Referens"), alpha=0.8)
            self.ax.legend(fontsize=7, facecolor="#2e2e34", labelcolor="white")

        self.canvas.draw_idle()

    def update_user(self, pitch_result):
        """Lägg till användarens tonhöjdskontur."""
        voiced = pitch_result.frequencies > 0
        if np.any(voiced):
            times = pitch_result.times[voiced]
            freqs = pitch_result.frequencies[voiced]
            self.ax.plot(times, freqs, "s-", color="#ff7043", markersize=2,
                         linewidth=1.5, label=_("Din inspelning"), alpha=0.8)
            self.ax.legend(fontsize=7, facecolor="#2e2e34", labelcolor="white")

        self.canvas.draw_idle()

    def clear(self):
        self.ax.clear()
        self.canvas.draw_idle()

"""Side-by-side spectrogram display using matplotlib in GTK4."""

import numpy as np
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

import matplotlib
matplotlib.use("GTK4Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg

from pronounceit.i18n import _


class SpectrogramView(Gtk.Box):
    """Visar referens- och användarspektrogram sida vid sida.

    Använder matplotlib inbäddat i GTK4 för professionell visning.
    """

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)

        self.fig, (self.ax_ref, self.ax_user) = plt.subplots(
            1, 2, figsize=(10, 3), dpi=100
        )
        self.fig.patch.set_facecolor("#1e1e24")
        self.fig.subplots_adjust(wspace=0.3, left=0.06, right=0.98, top=0.88, bottom=0.15)

        for ax in (self.ax_ref, self.ax_user):
            ax.set_facecolor("#1e1e24")
            ax.tick_params(colors="white", labelsize=7)
            ax.xaxis.label.set_color("white")
            ax.yaxis.label.set_color("white")
            ax.title.set_color("white")

        self.ax_ref.set_title(_("Referens"), fontsize=10)
        self.ax_ref.set_xlabel(_("Time (s)"), fontsize=8)
        self.ax_ref.set_ylabel(_("Frekvens (Hz)"), fontsize=8)

        self.ax_user.set_title(_("Din inspelning"), fontsize=10)
        self.ax_user.set_xlabel(_("Time (s)"), fontsize=8)
        self.ax_user.set_ylabel(_("Frekvens (Hz)"), fontsize=8)

        self.canvas = FigureCanvasGTK4Agg(self.fig)
        self.canvas.set_size_request(800, 250)
        self.append(self.canvas)

        self._ref_img = None
        self._user_img = None

    def update_reference(self, spec_result, title=""):
        """Visa referensspektrogram."""
        self.ax_ref.clear()
        self.ax_ref.set_facecolor("#1e1e24")
        self.ax_ref.set_title(
            f"{_('Referens')}: {title}" if title else _("Referens"),
            fontsize=10, color="white",
        )
        self.ax_ref.set_xlabel(_("Time (s)"), fontsize=8, color="white")
        self.ax_ref.set_ylabel(_("Frekvens (Hz)"), fontsize=8, color="white")
        self.ax_ref.tick_params(colors="white", labelsize=7)

        self._ref_img = self.ax_ref.pcolormesh(
            spec_result.times,
            spec_result.frequencies,
            spec_result.power,
            shading="gouraud",
            cmap="magma",
        )

        # Limit frequency display to speech range
        self.ax_ref.set_ylim(0, 5000)
        self.canvas.draw_idle()

    def update_user(self, spec_result, title=""):
        """Visa användarens spektrogram."""
        self.ax_user.clear()
        self.ax_user.set_facecolor("#1e1e24")
        self.ax_user.set_title(
            title or _("Din inspelning"),
            fontsize=10, color="white",
        )
        self.ax_user.set_xlabel(_("Time (s)"), fontsize=8, color="white")
        self.ax_user.set_ylabel(_("Frekvens (Hz)"), fontsize=8, color="white")
        self.ax_user.tick_params(colors="white", labelsize=7)

        self._user_img = self.ax_user.pcolormesh(
            spec_result.times,
            spec_result.frequencies,
            spec_result.power,
            shading="gouraud",
            cmap="magma",
        )

        self.ax_user.set_ylim(0, 5000)
        self.canvas.draw_idle()

    def clear(self):
        """Rensa båda spektrogrammen."""
        self.ax_ref.clear()
        self.ax_user.clear()
        self.canvas.draw_idle()

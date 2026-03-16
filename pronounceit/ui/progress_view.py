"""Progress tracking view with improvement charts."""

import numpy as np
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

import matplotlib
matplotlib.use("GTK4Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg

from pronounceit.i18n import _


class ProgressView(Gtk.Box):
    """Visar framsteg och förbättring över tid.

    Linjediagram per ord och genomsnitt per språk.
    """

    def __init__(self, database, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        self.database = database
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(8)
        self.set_margin_bottom(8)

        self._build_ui()

    def _build_ui(self):
        # Title
        title = Gtk.Label(label=_("Your progress"))
        title.add_css_class("title-2")
        self.append(title)

        # Stats row
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24,
                            halign=Gtk.Align.CENTER)
        stats_box.set_margin_top(8)
        stats_box.set_margin_bottom(8)

        self.total_sessions = Gtk.Label(label=_("Exercises: 0"))
        stats_box.append(self.total_sessions)

        self.avg_score = Gtk.Label(label=_("Average: --"))
        stats_box.append(self.avg_score)

        self.best_score_label = Gtk.Label(label=_("Best: --"))
        stats_box.append(self.best_score_label)

        self.append(stats_box)

        # Chart
        self.fig, (self.ax_progress, self.ax_lang) = plt.subplots(
            1, 2, figsize=(10, 3.5), dpi=100
        )
        self.fig.patch.set_facecolor("#1e1e24")
        self.fig.subplots_adjust(wspace=0.3, left=0.08, right=0.96, top=0.88, bottom=0.18)

        for ax in (self.ax_progress, self.ax_lang):
            ax.set_facecolor("#1e1e24")
            ax.tick_params(colors="white", labelsize=7)
            ax.title.set_color("white")
            ax.xaxis.label.set_color("white")
            ax.yaxis.label.set_color("white")

        self.canvas = FigureCanvasGTK4Agg(self.fig)
        self.canvas.set_size_request(800, 280)
        self.canvas.set_vexpand(True)
        self.append(self.canvas)

        # Refresh button
        refresh_btn = Gtk.Button(label=_("Update"))
        refresh_btn.set_halign(Gtk.Align.CENTER)
        refresh_btn.connect("clicked", lambda btn: self.refresh())
        self.append(refresh_btn)

    def refresh(self):
        """Uppdatera diagram med senaste data."""
        progress = self.database.get_all_progress()

        # Update stats
        if progress:
            scores = [p["score"] for p in progress]
            self.total_sessions.set_label(_("Exercises: {}").format(len(scores)))
            self.avg_score.set_label(_("Average: {:.0f}").format(np.mean(scores)))
            self.best_score_label.set_label(_("Best: {:.0f}").format(max(scores)))
        else:
            self.total_sessions.set_label(_("Exercises: 0"))
            self.avg_score.set_label(_("Average: --"))
            self.best_score_label.set_label(_("Best: --"))

        # Progress over time chart
        self.ax_progress.clear()
        self.ax_progress.set_facecolor("#1e1e24")
        self.ax_progress.set_title(_("Score over time"), fontsize=10, color="white")
        self.ax_progress.set_xlabel(_("Exercise #"), fontsize=8, color="white")
        self.ax_progress.set_ylabel(_("Points"), fontsize=8, color="white")
        self.ax_progress.tick_params(colors="white", labelsize=7)
        self.ax_progress.set_ylim(0, 105)

        if progress:
            scores = [p["score"] for p in progress]
            x = list(range(1, len(scores) + 1))
            self.ax_progress.plot(x, scores, "o-", color="#4fc3f7", markersize=4,
                                  linewidth=1.5)

            # Trend line
            if len(scores) >= 3:
                z = np.polyfit(x, scores, 1)
                trend = np.poly1d(z)
                self.ax_progress.plot(x, trend(x), "--", color="#ff7043",
                                      linewidth=1, alpha=0.7, label=_("Trend"))
                self.ax_progress.legend(fontsize=7, facecolor="#2e2e34",
                                        labelcolor="white")

        # Per-language chart
        self.ax_lang.clear()
        self.ax_lang.set_facecolor("#1e1e24")
        self.ax_lang.set_title(_("Average per language"), fontsize=10, color="white")
        self.ax_lang.set_ylabel(_("Points"), fontsize=8, color="white")
        self.ax_lang.tick_params(colors="white", labelsize=7)
        self.ax_lang.set_ylim(0, 105)

        lang_scores = self.database.get_average_scores_by_language()
        if lang_scores:
            lang_names = {"sv": "Svenska", "en": "English", "de": "Deutsch", "fr": "Français"}
            langs = list(lang_scores.keys())
            avgs = list(lang_scores.values())
            labels = [lang_names.get(l, l) for l in langs]
            colors = ["#4fc3f7", "#ff7043", "#66bb6a", "#ab47bc"]
            self.ax_lang.bar(labels, avgs, color=colors[:len(langs)])

        self.canvas.draw_idle()

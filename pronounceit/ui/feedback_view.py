"""Scoring and feedback display."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

from pronounceit.i18n import _


class FeedbackView(Gtk.Box):
    """Visar uttalspoäng och pedagogisk feedback."""

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        self.set_margin_top(8)
        self._build_ui()

    def _build_ui(self):
        # Score section
        score_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16,
                            halign=Gtk.Align.CENTER)

        # Overall score
        self.score_label = Gtk.Label(label="--")
        self.score_label.add_css_class("title-1")
        score_box.append(self.score_label)

        # Sub-scores
        sub_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        self.spectral_bar = self._make_score_row(_("Spectral"))
        sub_box.append(self.spectral_bar)

        self.pitch_bar = self._make_score_row(_("Pitch"))
        sub_box.append(self.pitch_bar)

        self.formant_bar = self._make_score_row(_("Formant"))
        sub_box.append(self.formant_bar)

        score_box.append(sub_box)
        self.append(score_box)

        # Level bar for overall score
        self.level_bar = Gtk.LevelBar()
        self.level_bar.set_min_value(0)
        self.level_bar.set_max_value(100)
        self.level_bar.set_size_request(400, 20)
        self.level_bar.set_halign(Gtk.Align.CENTER)
        self.append(self.level_bar)

        # Feedback text
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(-1, 100)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.feedback_text = Gtk.TextView()
        self.feedback_text.set_editable(False)
        self.feedback_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.feedback_text.set_cursor_visible(False)
        self.feedback_text.set_top_margin(8)
        self.feedback_text.set_bottom_margin(8)
        self.feedback_text.set_left_margin(12)
        self.feedback_text.set_right_margin(12)
        scroll.set_child(self.feedback_text)
        self.append(scroll)

    def _make_score_row(self, label_text):
        """Skapa en rad med etikett och nivåindikator."""
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        label = Gtk.Label(label=label_text)
        label.set_size_request(80, -1)
        label.set_xalign(0)
        box.append(label)

        bar = Gtk.LevelBar()
        bar.set_min_value(0)
        bar.set_max_value(100)
        bar.set_size_request(200, 12)
        box.append(bar)

        value_label = Gtk.Label(label="--")
        value_label.set_size_request(40, -1)
        box.append(value_label)

        box._bar = bar
        box._value_label = value_label
        return box

    def show_result(self, score_result, feedback_text):
        """Visa poäng och feedback."""
        self.score_label.set_label(f"{score_result.total:.0f}")
        self.level_bar.set_value(score_result.total)

        # Update sub-scores
        self._update_score_row(self.spectral_bar, score_result.spectral_score)
        self._update_score_row(self.pitch_bar, score_result.pitch_score)
        self._update_score_row(self.formant_bar, score_result.formant_score)

        # Feedback text
        buf = self.feedback_text.get_buffer()
        buf.set_text(feedback_text)

    def _update_score_row(self, row, value):
        row._bar.set_value(value)
        row._value_label.set_label(f"{value:.0f}")

    def clear(self):
        self.score_label.set_label("--")
        self.level_bar.set_value(0)
        buf = self.feedback_text.get_buffer()
        buf.set_text("")

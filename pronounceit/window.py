"""Main application window."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk, Gio

from pronounceit.i18n import _
from pronounceit.ui.recording_view import RecordingView
from pronounceit.ui.spectrogram_view import SpectrogramView
from pronounceit.ui.pitch_view import PitchView
from pronounceit.ui.feedback_view import FeedbackView
from pronounceit.ui.word_browser_view import WordBrowserView
from pronounceit.ui.progress_view import ProgressView
from pronounceit.audio.recorder import Recorder
from pronounceit.audio.analyzer import SpectrogramAnalyzer
from pronounceit.audio.pitch_tracker import PitchTracker
from pronounceit.audio.formant import FormantAnalyzer
from pronounceit.audio.comparator import SpectrogramComparator
from pronounceit.scoring.scorer import PronunciationScorer
from pronounceit.scoring.feedback import FeedbackGenerator


class MainWindow(Adw.ApplicationWindow):
    """Huvudfönster med flikar för övning, ordlista och framsteg."""

    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self.set_default_size(1000, 700)
        self.set_title("PronounceIt")

        # Audio components
        self.recorder = Recorder()
        self.analyzer = SpectrogramAnalyzer()
        self.pitch_tracker = PitchTracker()
        self.formant_analyzer = FormantAnalyzer()
        self.comparator = SpectrogramComparator()
        self.scorer = PronunciationScorer()
        self.feedback_gen = FeedbackGenerator()

        # Current reference data
        self._current_word = None
        self._reference_audio = None
        self._user_audio = None

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        # Main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)

        # Header bar with view switcher
        header = Adw.HeaderBar()
        self.view_switcher = Adw.ViewSwitcher()
        header.set_title_widget(self.view_switcher)

        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_model = Gio.Menu()
        menu_model.append(_("About PronounceIt"), "app.about")
        menu_model.append(_("Quit"), "app.quit")
        menu_button.set_menu_model(menu_model)
        header.pack_end(menu_button)

        self.main_box.append(header)

        # View stack
        self.stack = Adw.ViewStack()
        self.view_switcher.set_stack(self.stack)

        # Practice page
        self._build_practice_page()

        # Word list page
        self.word_browser = WordBrowserView(database=self.database)
        self.stack.add_titled_with_icon(
            self.word_browser, "words", _("Glossary of terms"),
            "view-list-symbolic"
        )

        # Progress page
        self.progress_view = ProgressView(database=self.database)
        self.stack.add_titled_with_icon(
            self.progress_view, "progress", _("Progress"),
            "emblem-ok-symbolic"
        )

        self.main_box.append(self.stack)

    def _build_practice_page(self):
        practice_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        practice_box.set_margin_start(12)
        practice_box.set_margin_end(12)
        practice_box.set_margin_top(8)
        practice_box.set_margin_bottom(8)

        # Word display
        self.word_label = Gtk.Label(label=_("Select a word from the dictionary"))
        self.word_label.add_css_class("title-1")
        practice_box.append(self.word_label)

        self.ipa_label = Gtk.Label(label="")
        self.ipa_label.add_css_class("title-3")
        practice_box.append(self.ipa_label)

        # Spectrogram view
        self.spectrogram_view = SpectrogramView()
        practice_box.append(self.spectrogram_view)

        # Pitch view
        self.pitch_view = PitchView()
        practice_box.append(self.pitch_view)

        # Recording controls
        self.recording_view = RecordingView(recorder=self.recorder)
        practice_box.append(self.recording_view)

        # Feedback
        self.feedback_view = FeedbackView()
        practice_box.append(self.feedback_view)

        self.stack.add_titled_with_icon(
            practice_box, "practice", _("Exercise"),
            "audio-input-microphone-symbolic"
        )

    def _connect_signals(self):
        self.recorder.connect("recording-complete", self._on_recording_complete)
        self.word_browser.connect("word-selected", self._on_word_selected)

    def _on_word_selected(self, widget, word_data):
        """Handle word selection from browser."""
        self._current_word = word_data
        self.word_label.set_label(word_data["text"])
        self.ipa_label.set_label(f"/{word_data['ipa']}/")

        # Load and display reference spectrogram
        ref_audio = self.database.load_reference_audio(word_data)
        if ref_audio is not None:
            self._reference_audio = ref_audio
            ref_spec = self.analyzer.compute(ref_audio)
            self.spectrogram_view.update_reference(ref_spec, word_data["text"])
            ref_pitch = self.pitch_tracker.extract(ref_audio)
            self.pitch_view.update_reference(ref_pitch)

        # Switch to practice view
        self.stack.set_visible_child_name("practice")

    def _on_recording_complete(self, recorder, audio_data, sample_rate):
        """Analyze recording and show results."""
        self._user_audio = audio_data

        # Compute spectrogram
        user_spec = self.analyzer.compute(audio_data, sample_rate)
        self.spectrogram_view.update_user(user_spec, _("Your recording"))

        # Pitch tracking
        user_pitch = self.pitch_tracker.extract(audio_data, sample_rate)
        self.pitch_view.update_user(user_pitch)

        # Formant analysis
        user_formants = self.formant_analyzer.extract(audio_data, sample_rate)

        # Scoring
        if self._reference_audio is not None and self._current_word:
            ref_spec = self.analyzer.compute(self._reference_audio)
            ref_pitch = self.pitch_tracker.extract(self._reference_audio)
            ref_formants = self.formant_analyzer.extract(self._reference_audio)

            score_result = self.scorer.score(
                user_spec, ref_spec,
                user_pitch, ref_pitch,
                user_formants, ref_formants,
                language=self._current_word.get("language", "sv"),
            )

            # Show feedback
            feedback_text = self.feedback_gen.generate(
                score_result, self._current_word
            )
            self.feedback_view.show_result(score_result, feedback_text)

            # Save progress
            self.database.save_progress(
                word_id=self._current_word["id"],
                score=score_result.total,
                spectral=score_result.spectral_score,
                pitch=score_result.pitch_score,
                formant=score_result.formant_score,
            )

            # Update progress view
            self.progress_view.refresh()

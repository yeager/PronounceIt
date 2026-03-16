"""Word/phrase browser with filtering."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, GObject, Gio, Adw

from pronounceit.i18n import _


class WordBrowserView(Gtk.Box):
    """Ordlistevy med filtrering per språk och svårighetsgrad.

    Signalerar 'word-selected' när ett ord väljs.
    """

    __gsignals__ = {
        "word-selected": (GObject.SignalFlags.RUN_LAST, None, (object,)),
    }

    LANGUAGE_NAMES = {
        "sv": "Svenska",
        "en": "English",
        "de": "Deutsch",
        "fr": "Français",
    }

    LANGUAGE_FLAGS = {
        "sv": "\U0001f1f8\U0001f1ea",
        "en": "\U0001f1ec\U0001f1e7",
        "de": "\U0001f1e9\U0001f1ea",
        "fr": "\U0001f1eb\U0001f1f7",
    }

    def __init__(self, database, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8, **kwargs)
        self.database = database
        self._current_language = "sv"
        self._words = []

        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(8)
        self.set_margin_bottom(8)

        self._build_ui()
        self._load_words()

    def _build_ui(self):
        # Filter bar
        filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Language selector
        lang_label = Gtk.Label(label=_("Språk:"))
        filter_box.append(lang_label)

        self.lang_dropdown = Gtk.DropDown.new_from_strings(
            [f"{self.LANGUAGE_FLAGS[k]} {v}"
             for k, v in self.LANGUAGE_NAMES.items()]
        )
        self.lang_dropdown.set_selected(0)  # Svenska first
        self.lang_dropdown.connect("notify::selected", self._on_language_changed)
        filter_box.append(self.lang_dropdown)

        # Difficulty filter
        diff_label = Gtk.Label(label=_("Svårighetsgrad:"))
        diff_label.set_margin_start(16)
        filter_box.append(diff_label)

        self.diff_dropdown = Gtk.DropDown.new_from_strings(
            [_("Alla"), "1 - " + _("Lätt"), "2", "3 - " + _("Medel"),
             "4", "5 - " + _("Svår")]
        )
        self.diff_dropdown.set_selected(0)
        self.diff_dropdown.connect("notify::selected", self._on_filter_changed)
        filter_box.append(self.diff_dropdown)

        # Search
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(_("Sök ord..."))
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", self._on_search_changed)
        filter_box.append(self.search_entry)

        self.append(filter_box)

        # Word list
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.add_css_class("boxed-list")
        self.list_box.connect("row-activated", self._on_row_activated)
        scroll.set_child(self.list_box)
        self.append(scroll)

    def _load_words(self):
        """Ladda ord från databasen."""
        self._words = self.database.get_words(language=self._current_language)
        self._populate_list(self._words)

    def _populate_list(self, words):
        """Fyll listan med ord."""
        # Remove existing rows
        while True:
            row = self.list_box.get_row_at_index(0)
            if row is None:
                break
            self.list_box.remove(row)

        for word in words:
            row = Adw.ActionRow()
            row.set_title(word["text"])
            row.set_subtitle(f"/{word['ipa']}/  ·  {word.get('category', '')}")

            # Difficulty indicator
            diff_label = Gtk.Label(label="\u2605" * word.get("difficulty", 1))
            diff_label.add_css_class("dim-label")
            row.add_suffix(diff_label)

            # Best score if available
            best = self.database.get_best_score(word["id"])
            if best is not None:
                score_label = Gtk.Label(label=f"{best:.0f}")
                score_label.add_css_class("accent")
                row.add_suffix(score_label)

            # Navigation indicator
            arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
            row.add_suffix(arrow)
            row.set_activatable(True)

            row._word_data = word
            self.list_box.append(row)

    def _on_row_activated(self, list_box, row):
        if hasattr(row, "_word_data"):
            self.emit("word-selected", row._word_data)

    def _on_language_changed(self, dropdown, param):
        lang_keys = list(self.LANGUAGE_NAMES.keys())
        idx = dropdown.get_selected()
        if 0 <= idx < len(lang_keys):
            self._current_language = lang_keys[idx]
            self._load_words()

    def _on_filter_changed(self, dropdown, param):
        self._apply_filters()

    def _on_search_changed(self, entry):
        self._apply_filters()

    def _apply_filters(self):
        """Tillämpa sök- och svårighetsfiltret."""
        diff_idx = self.diff_dropdown.get_selected()
        search_text = self.search_entry.get_text().lower()

        filtered = self._words
        if diff_idx > 0:
            filtered = [w for w in filtered if w.get("difficulty", 1) == diff_idx]
        if search_text:
            filtered = [
                w for w in filtered
                if search_text in w["text"].lower() or search_text in w.get("ipa", "")
            ]
        self._populate_list(filtered)

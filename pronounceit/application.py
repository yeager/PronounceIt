"""Main Gtk.Application for PronounceIt."""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib
from pronounceit import __app_id__, __version__
from pronounceit.i18n import _
from pronounceit.window import MainWindow
from pronounceit.data.database import Database


class PronounceItApp(Adw.Application):
    """Huvudapplikation för PronounceIt."""

    def __init__(self):
        super().__init__(
            application_id=__app_id__,
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self.database = None

    def do_startup(self):
        Adw.Application.do_startup(self)
        self.database = Database()
        self._setup_actions()

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self, database=self.database)
        win.present()

    def _setup_actions(self):
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<primary>q"])

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.add_action(about_action)

    def _on_about(self, action, param):
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="PronounceIt",
            application_icon="audio-input-microphone-symbolic",
            developer_name="PronounceIt Team",
            version=__version__,
            comments=_("Uttalsträning för alla språk med visuell feedback och spektrogram"),
            license_type=Gio.License.MIT_X11,
        )
        about.present()

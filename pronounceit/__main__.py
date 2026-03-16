"""Entry point for PronounceIt."""

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from pronounceit.application import PronounceItApp


def main():
    app = PronounceItApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())

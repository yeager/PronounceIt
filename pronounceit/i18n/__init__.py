"""Internationalization setup for PronounceIt."""

import gettext
import locale
import os

LOCALE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "po")
DOMAIN = "pronounceit"

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

_lang = os.environ.get("LANGUAGE", os.environ.get("LANG", "sv_SE"))
_languages = [_lang.split(".")[0], "sv"]

_translation = gettext.translation(
    DOMAIN, LOCALE_DIR, languages=_languages, fallback=True
)

_ = _translation.gettext
ngettext = _translation.ngettext

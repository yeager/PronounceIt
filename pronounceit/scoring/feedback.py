"""Pedagogical feedback generation in Swedish."""

from pronounceit.i18n import _
from pronounceit.data.models import ScoringResult


class FeedbackGenerator:
    """Genererar pedagogisk feedback på svenska baserat på uttalspoäng.

    Designad för logopeder och språkelever.
    """

    def generate(self, result, word_data=None):
        """Generera feedback-text baserat på poängresultat.

        Args:
            result: ScoringResult
            word_data: dict med ordinfo (text, ipa, language, category)

        Returns:
            str med feedback på svenska
        """
        parts = []

        # Overall assessment
        parts.append(self._overall_feedback(result.total))

        # Spectral feedback
        if result.spectral_score < 60:
            parts.append(
                _("Spektral analys visar att ljudet skiljer sig från referensen. "
                  "Försök lyssna noga på referensen och imitera.")
            )
        elif result.spectral_score < 80:
            parts.append(
                _("Ljudet är nära referensen men kan förbättras. "
                  "Fokusera på artikulationens precision.")
            )

        # Pitch feedback
        if result.pitch_score < 50:
            parts.append(
                _("Tonhöjdsmönstret avviker markant. "
                  "Var uppmärksam på intonationen och betoningen.")
            )
        elif result.pitch_score < 70:
            parts.append(
                _("Intonationen kan förbättras. "
                  "Lyssna på melodin i referensuttalet.")
            )

        # Formant feedback
        if result.formant_score < 50:
            parts.append(
                _("Vokalerna behöver justeras. "
                  "Kontrollera tungans och läpparnas position.")
            )
        elif result.formant_score < 70:
            parts.append(
                _("Vokalerna är nära men kan finslipas. "
                  "Tänk på munöppning och tungposition.")
            )

        # Language-specific tips
        if word_data:
            lang_tip = self._language_specific_tip(
                word_data.get("language", "sv"),
                word_data.get("category", ""),
                result,
            )
            if lang_tip:
                parts.append(lang_tip)

        return "\n\n".join(parts)

    def _overall_feedback(self, total_score):
        """Generera övergripande bedömning."""
        if total_score >= 90:
            return _("Utmärkt! Ditt uttal är mycket nära referensen. Bra jobbat!")
        elif total_score >= 75:
            return _("Bra uttal! Några små justeringar kan göra det ännu bättre.")
        elif total_score >= 60:
            return _("Godkänt uttal. Fortsätt öva för att förbättra precisionen.")
        elif total_score >= 40:
            return _("Uttalet behöver mer övning. Lyssna noga på referensen och försök igen.")
        else:
            return _("Försök igen! Lyssna på referensen och fokusera på ett ljud i taget.")

    def _language_specific_tip(self, language, category, result):
        """Generera språkspecifika tips."""
        if language == "sv":
            return self._swedish_tip(category, result)
        elif language == "de":
            return self._german_tip(category, result)
        elif language == "fr":
            return self._french_tip(category, result)
        return None

    def _swedish_tip(self, category, result):
        """Svenska uttaltips."""
        tips = []
        if category == "vowel" and result.formant_score < 70:
            tips.append(
                _("Svenska har många vokaler. "
                  "Tänk särskilt på skillnaden mellan lång och kort vokal, "
                  "t.ex. 'hus' /hʉːs/ vs 'huss' /hɵs/.")
            )
        if result.pitch_score < 60:
            tips.append(
                _("Svenskan har ordaccenter (accent 1 och accent 2). "
                  "Tonhöjdsmönstret är viktigt för ordets betydelse.")
            )
        return " ".join(tips) if tips else None

    def _german_tip(self, category, result):
        """Tyska uttaltips."""
        if category == "vowel" and result.formant_score < 70:
            return _(
                "Tyska vokaler har tydlig skillnad mellan spända och ospända. "
                "T.ex. /iː/ i 'Miete' vs /ɪ/ i 'Mitte'."
            )
        return None

    def _french_tip(self, category, result):
        """Franska uttaltips."""
        if category == "vowel" and result.formant_score < 70:
            return _(
                "Franska nasalvokaler kräver att luft släpps genom näsan. "
                "Öva med /ɑ̃/ i 'dans' och /ɛ̃/ i 'vin'."
            )
        return None

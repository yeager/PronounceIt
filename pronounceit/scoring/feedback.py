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
                _("Spectral analysis shows that the sound is different from the reference. Try to listen carefully to the reference and imitate.")
            )
        elif result.spectral_score < 80:
            parts.append(
                _("The sound is close to the reference but can be improved. Focus on the precision of articulation.")
            )

        # Pitch feedback
        if result.pitch_score < 50:
            parts.append(
                _("The pitch pattern differs markedly. Pay attention to intonation and stress.")
            )
        elif result.pitch_score < 70:
            parts.append(
                _("Intonation can be improved. "
                  "Listen to the melody in the reference pronunciation.")
            )

        # Formant feedback
        if result.formant_score < 50:
            parts.append(
                _("The vowels need to be adjusted. "
                  "Check the position of your tongue and lips.")
            )
        elif result.formant_score < 70:
            parts.append(
                _("The vowels are close but can be refined. "
                  "Think about mouth opening and tongue position.")
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
            return _("Excellent! Your pronunciation is very close to the reference. Well done!")
        elif total_score >= 75:
            return _("Good pronunciation! A few small adjustments can make it even better.")
        elif total_score >= 60:
            return _("Approved pronunciation. Keep practicing to improve accuracy.")
        elif total_score >= 40:
            return _("Pronunciation needs more practice. Listen carefully to the reference and try again.")
        else:
            return _("Try it again! Listen to the reference and focus on one sound at a time.")

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
                _("Swedish has many vowels. e.g. 'hus' /hʉːs/ vs 'huss' /hɵs/.")
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
                "German vowels have a clear distinction between tense and non-tense. "
                "T.ex. /iː/ i 'Miete' vs /ɪ/ i 'Mitte'."
            )
        return None

    def _french_tip(self, category, result):
        """Franska uttaltips."""
        if category == "vowel" and result.formant_score < 70:
            return _(
                "French nasal vowels require air to be released through the nose. "
                "Practice with /ɑ̃/ in 'dans' och /ɛ̃/ i 'vin'."
            )
        return None

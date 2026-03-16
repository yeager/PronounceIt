"""Data models for PronounceIt."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Word:
    """Representerar ett ord/fras för uttalsträning."""

    id: int
    text: str
    ipa: str
    language: str  # 'sv', 'en', 'de', 'fr'
    category: str  # 'vowel', 'consonant', 'minimal_pair', 'phrase'
    difficulty: int  # 1-5
    reference_audio_path: str = ""
    notes: str = ""  # Pedagogiska anteckningar

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "ipa": self.ipa,
            "language": self.language,
            "category": self.category,
            "difficulty": self.difficulty,
            "reference_audio_path": self.reference_audio_path,
            "notes": self.notes,
        }


@dataclass
class ProgressEntry:
    """En uttalsträningsresultat."""

    id: int = 0
    word_id: int = 0
    timestamp: str = ""
    score: float = 0.0
    spectral_score: float = 0.0
    pitch_score: float = 0.0
    formant_score: float = 0.0


@dataclass
class ScoringResult:
    """Resultat från uttalspoängsättning."""

    total: float = 0.0
    spectral_score: float = 0.0
    pitch_score: float = 0.0
    formant_score: float = 0.0
    details: dict = field(default_factory=dict)

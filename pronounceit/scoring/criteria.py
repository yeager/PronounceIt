"""Language-specific scoring criteria and formant targets."""

# Approximate formant targets for common vowels per language.
# Values are (F1_Hz, F2_Hz) for adult speakers.
# Used by the scorer to evaluate formant accuracy.

VOWEL_TARGETS = {
    "sv": {
        # Swedish long vowels
        "iː": (270, 2300),
        "yː": (280, 1900),
        "ʉː": (300, 1600),
        "eː": (370, 2200),
        "øː": (390, 1700),
        "oː": (370, 700),
        "ɛː": (550, 1900),
        "aː": (700, 1200),
        "ɑː": (650, 1050),
    },
    "en": {
        "iː": (270, 2300),
        "ɪ": (390, 1900),
        "ɛ": (550, 1800),
        "æ": (700, 1700),
        "ɑː": (700, 1100),
        "ɔː": (500, 750),
        "ʊ": (370, 950),
        "uː": (300, 750),
        "ʌ": (600, 1200),
        "ɜː": (500, 1500),
    },
    "de": {
        "iː": (270, 2300),
        "ɪ": (380, 1900),
        "eː": (350, 2200),
        "ɛ": (550, 1800),
        "aː": (700, 1200),
        "oː": (370, 700),
        "ɔ": (500, 850),
        "uː": (300, 750),
        "ʊ": (380, 950),
        "yː": (280, 1900),
        "ʏ": (350, 1700),
        "øː": (390, 1600),
        "œ": (480, 1500),
    },
    "fr": {
        "i": (280, 2300),
        "e": (370, 2200),
        "ɛ": (550, 1800),
        "a": (700, 1300),
        "ɑ": (650, 1050),
        "o": (370, 750),
        "ɔ": (500, 850),
        "u": (300, 750),
        "y": (280, 1900),
        "ø": (380, 1600),
        "œ": (480, 1500),
        "ə": (450, 1350),
    },
}

# Pitch range expectations per language (Hz, for adult speakers)
PITCH_RANGES = {
    "sv": {"min": 75, "max": 350, "notes": "Swedish has word accents (accent 1 & 2)"},
    "en": {"min": 75, "max": 300, "notes": "English uses stress-timed rhythm"},
    "de": {"min": 75, "max": 300, "notes": "German has declarative falling intonation"},
    "fr": {"min": 80, "max": 320, "notes": "French uses syllable-timed rhythm"},
}

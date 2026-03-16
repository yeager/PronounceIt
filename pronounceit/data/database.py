"""SQLite database for words and progress tracking."""

import json
import os
import sqlite3
from datetime import datetime

import numpy as np


class Database:
    """Hanterar ordlista och framstegsdata i SQLite.

    Ordlistan förladdas från JSON-filer vid första start.
    Framstegsdata sparas i ~/.local/share/pronounceit/.
    """

    def __init__(self, db_path=None):
        if db_path is None:
            data_dir = os.path.join(
                os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")),
                "pronounceit",
            )
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "pronounceit.db")

        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()
        self._seed_if_empty()

    def _create_tables(self):
        cur = self._conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                ipa TEXT NOT NULL,
                language TEXT NOT NULL,
                category TEXT DEFAULT '',
                difficulty INTEGER DEFAULT 1,
                reference_audio_path TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                score REAL NOT NULL,
                spectral_score REAL DEFAULT 0,
                pitch_score REAL DEFAULT 0,
                formant_score REAL DEFAULT 0,
                FOREIGN KEY (word_id) REFERENCES words(id)
            )
        """)
        self._conn.commit()

    def _seed_if_empty(self):
        """Ladda ordlistor från JSON om databasen är tom."""
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM words")
        if cur.fetchone()[0] > 0:
            return

        wordlist_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "wordlists"
        )
        wordlist_dir = os.path.normpath(wordlist_dir)

        if not os.path.isdir(wordlist_dir):
            return

        for filename in sorted(os.listdir(wordlist_dir)):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(wordlist_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    words = json.load(f)
                for w in words:
                    cur.execute(
                        """INSERT INTO words (text, ipa, language, category, difficulty, notes)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            w["text"],
                            w["ipa"],
                            w["language"],
                            w.get("category", ""),
                            w.get("difficulty", 1),
                            w.get("notes", ""),
                        ),
                    )
            except (json.JSONDecodeError, KeyError, OSError):
                continue

        self._conn.commit()

    def get_words(self, language=None, category=None, difficulty=None):
        """Hämta ord, valfritt filtrerade."""
        query = "SELECT * FROM words WHERE 1=1"
        params = []
        if language:
            query += " AND language = ?"
            params.append(language)
        if category:
            query += " AND category = ?"
            params.append(category)
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        query += " ORDER BY difficulty, text"

        cur = self._conn.cursor()
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]

    def get_best_score(self, word_id):
        """Hämta bästa poäng för ett ord."""
        cur = self._conn.cursor()
        cur.execute(
            "SELECT MAX(score) FROM progress WHERE word_id = ?", (word_id,)
        )
        row = cur.fetchone()
        return row[0] if row and row[0] is not None else None

    def save_progress(self, word_id, score, spectral=0, pitch=0, formant=0):
        """Spara övningsresultat."""
        cur = self._conn.cursor()
        cur.execute(
            """INSERT INTO progress (word_id, timestamp, score, spectral_score,
               pitch_score, formant_score) VALUES (?, ?, ?, ?, ?, ?)""",
            (word_id, datetime.now().isoformat(), score, spectral, pitch, formant),
        )
        self._conn.commit()

    def get_all_progress(self):
        """Hämta all framstegsdata sorterad efter tid."""
        cur = self._conn.cursor()
        cur.execute(
            """SELECT p.*, w.text, w.language FROM progress p
               JOIN words w ON p.word_id = w.id
               ORDER BY p.timestamp"""
        )
        return [dict(row) for row in cur.fetchall()]

    def get_average_scores_by_language(self):
        """Hämta genomsnittspoäng per språk."""
        cur = self._conn.cursor()
        cur.execute(
            """SELECT w.language, AVG(p.score) as avg_score
               FROM progress p JOIN words w ON p.word_id = w.id
               GROUP BY w.language"""
        )
        return {row["language"]: row["avg_score"] for row in cur.fetchall()}

    def load_reference_audio(self, word_data):
        """Ladda referensljud för ett ord.

        Returnerar numpy array eller None om filen saknas.
        """
        ref_path = word_data.get("reference_audio_path", "")
        if not ref_path:
            # Generate synthetic reference tone as placeholder
            return self._generate_placeholder(word_data)

        full_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "reference_audio", ref_path
        )
        full_path = os.path.normpath(full_path)

        if not os.path.isfile(full_path):
            return self._generate_placeholder(word_data)

        try:
            import wave
            with wave.open(full_path, "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
                return audio
        except Exception:
            return self._generate_placeholder(word_data)

    def _generate_placeholder(self, word_data):
        """Generera ett syntetiskt platshållarljud.

        Skapar en enkel ton som representerar ordet tills
        riktiga inspelningar finns tillgängliga.
        """
        duration = 0.5 + len(word_data.get("text", "")) * 0.05
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

        # Base frequency varies by language
        base_freq = {"sv": 180, "en": 160, "de": 170, "fr": 190}.get(
            word_data.get("language", "sv"), 170
        )

        # Simple harmonic signal with envelope
        envelope = np.exp(-t * 2) * (1 - np.exp(-t * 50))
        signal = envelope * (
            0.5 * np.sin(2 * np.pi * base_freq * t)
            + 0.3 * np.sin(2 * np.pi * base_freq * 2 * t)
            + 0.1 * np.sin(2 * np.pi * base_freq * 3 * t)
        )
        return signal.astype(np.float32)

    def close(self):
        self._conn.close()

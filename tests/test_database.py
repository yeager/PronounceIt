"""Tests for database operations."""

import os
import tempfile

import pytest

from pronounceit.data.database import Database


@pytest.fixture
def db():
    """Create a temporary database."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database = Database(db_path=path)
    yield database
    database.close()
    os.unlink(path)


def test_create_tables(db):
    """Database should create tables on init."""
    cur = db._conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert "words" in tables
    assert "progress" in tables


def test_seed_words(db):
    """Database should seed words from JSON files."""
    words = db.get_words()
    assert len(words) > 0


def test_get_words_by_language(db):
    """Should filter words by language."""
    sv_words = db.get_words(language="sv")
    en_words = db.get_words(language="en")

    for w in sv_words:
        assert w["language"] == "sv"
    for w in en_words:
        assert w["language"] == "en"


def test_save_and_get_progress(db):
    """Should save and retrieve progress."""
    words = db.get_words()
    if not words:
        pytest.skip("No words in database")

    word_id = words[0]["id"]
    db.save_progress(word_id, score=75.5, spectral=80, pitch=70, formant=76)

    progress = db.get_all_progress()
    assert len(progress) == 1
    assert progress[0]["score"] == 75.5


def test_best_score(db):
    """Should return the best score for a word."""
    words = db.get_words()
    if not words:
        pytest.skip("No words in database")

    word_id = words[0]["id"]
    db.save_progress(word_id, score=60)
    db.save_progress(word_id, score=85)
    db.save_progress(word_id, score=72)

    best = db.get_best_score(word_id)
    assert best == 85


def test_average_by_language(db):
    """Should compute average scores by language."""
    words = db.get_words(language="sv")
    if not words:
        pytest.skip("No Swedish words")

    db.save_progress(words[0]["id"], score=80)
    db.save_progress(words[0]["id"], score=90)

    avgs = db.get_average_scores_by_language()
    assert "sv" in avgs
    assert avgs["sv"] == 85.0

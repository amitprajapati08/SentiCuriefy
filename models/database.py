# models/database.py
import sqlite3
import bcrypt
from datetime import datetime
from config import Config


def _get_conn():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Schema ────────────────────────────────────────────────────────

def init_db():
    with _get_conn() as conn:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT    NOT NULL,
                email        TEXT    NOT NULL UNIQUE,
                password     TEXT    NOT NULL,
                created_at   TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        # Sentiment history — now with user_id (nullable for guests)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER REFERENCES users(id),
                text            TEXT    NOT NULL,
                sentiment       TEXT    NOT NULL,
                sentiment_score REAL    NOT NULL DEFAULT 0.0,
                emotion         TEXT,
                created_at      TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        # Community shares
        conn.execute("""
            CREATE TABLE IF NOT EXISTS community_shares (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT    NOT NULL,
                category        TEXT    NOT NULL,
                mood            TEXT    NOT NULL,
                text            TEXT    NOT NULL,
                sentiment_score REAL    NOT NULL DEFAULT 0.0,
                sentiment       TEXT    NOT NULL,
                created_at      TEXT    DEFAULT (datetime('now','localtime'))
            )
        """)
        conn.commit()


# ── User auth ─────────────────────────────────────────────────────

def create_user(name, email, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed)
            )
            conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Email already registered."


def verify_user(email, password):
    """Returns user dict if credentials valid, else None."""
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    if row and bcrypt.checkpw(password.encode(), row["password"].encode()):
        return dict(row)
    return None


def get_user_by_id(user_id):
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
    return dict(row) if row else None


# ── History write ─────────────────────────────────────────────────

def add_to_history(text, sentiment_score, sentiment, emotion, user_id=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _get_conn() as conn:
        conn.execute(
            """INSERT INTO sentiment_history
               (user_id, text, sentiment_score, sentiment, emotion, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, text, sentiment_score, sentiment, emotion, now)
        )
        conn.commit()


def delete_history_item(item_id):
    with _get_conn() as conn:
        conn.execute("DELETE FROM sentiment_history WHERE id = ?", (item_id,))
        conn.commit()


def clear_history():
    with _get_conn() as conn:
        conn.execute("DELETE FROM sentiment_history")
        conn.commit()


# ── History read ──────────────────────────────────────────────────

def get_history(limit=None):
    limit = limit or Config.HISTORY_LIMIT
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM sentiment_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_user_history(user_id, limit=50):
    with _get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM sentiment_history
               WHERE user_id = ?
               ORDER BY id DESC LIMIT ?""",
            (user_id, limit)
        ).fetchall()
    return [dict(r) for r in rows]


def get_user_stats(user_id):
    with _get_conn() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM sentiment_history WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        pos = conn.execute(
            "SELECT COUNT(*) FROM sentiment_history WHERE user_id=? AND sentiment='positive'",
            (user_id,)
        ).fetchone()[0]
        neg = conn.execute(
            "SELECT COUNT(*) FROM sentiment_history WHERE user_id=? AND sentiment='negative'",
            (user_id,)
        ).fetchone()[0]
        neu = conn.execute(
            "SELECT COUNT(*) FROM sentiment_history WHERE user_id=? AND sentiment='neutral'",
            (user_id,)
        ).fetchone()[0]
        emotions = conn.execute(
            """SELECT emotion, COUNT(*) as cnt FROM sentiment_history
               WHERE user_id=? AND emotion IS NOT NULL
               GROUP BY emotion ORDER BY cnt DESC LIMIT 5""",
            (user_id,)
        ).fetchall()
    return {
        "total":       total,
        "positive":    pos,
        "negative":    neg,
        "neutral":     neu,
        "pos_pct":     round(pos / total * 100, 1) if total else 0,
        "neg_pct":     round(neg / total * 100, 1) if total else 0,
        "neu_pct":     round(neu / total * 100, 1) if total else 0,
        "top_emotions": [dict(r) for r in emotions],
    }


# ── Dashboard stats (global) ──────────────────────────────────────

def get_dashboard_stats():
    with _get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM sentiment_history").fetchone()[0]
        pos   = conn.execute("SELECT COUNT(*) FROM sentiment_history WHERE sentiment='positive'").fetchone()[0]
        neg   = conn.execute("SELECT COUNT(*) FROM sentiment_history WHERE sentiment='negative'").fetchone()[0]
        neu   = conn.execute("SELECT COUNT(*) FROM sentiment_history WHERE sentiment='neutral'").fetchone()[0]
        avg   = conn.execute("SELECT AVG(sentiment_score) FROM sentiment_history").fetchone()[0]
        recent = conn.execute("SELECT * FROM sentiment_history ORDER BY id DESC LIMIT 10").fetchall()
        emotions = conn.execute(
            """SELECT emotion, COUNT(*) as cnt FROM sentiment_history
               WHERE emotion IS NOT NULL GROUP BY emotion ORDER BY cnt DESC LIMIT 5"""
        ).fetchall()
    return {
        "total":        total,
        "positive":     pos, "negative": neg, "neutral": neu,
        "avg_score":    round((avg or 0) * 100, 1),
        "recent":       [dict(r) for r in recent],
        "top_emotions": [dict(r) for r in emotions],
        "pos_pct": round(pos / total * 100, 1) if total else 0,
        "neg_pct": round(neg / total * 100, 1) if total else 0,
        "neu_pct": round(neu / total * 100, 1) if total else 0,
        "dist":    {"positive": pos, "negative": neg, "neutral": neu},
        "trend":   [], "intents": [],
    }


# ── Community shares ──────────────────────────────────────────────

def save_share(name, category, mood, text, sentiment_score, sentiment):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _get_conn() as conn:
        conn.execute(
            """INSERT INTO community_shares
               (name, category, mood, text, sentiment_score, sentiment, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, category, mood, text, sentiment_score, sentiment, now)
        )
        conn.commit()


def get_community_shares(limit=20):
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM community_shares ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_community_stats():
    return get_dashboard_stats()

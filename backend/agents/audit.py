import sqlite3
from datetime import datetime, timezone

DB_PATH = "audit.db"


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            event_type TEXT,
            verdict TEXT,
            similarity_score REAL,
            github_status TEXT,
            detail TEXT,
            created_at TEXT
        )
    """)
    return conn


def log_audit_event(thread_id: str, event_type: str, verdict: str = "", similarity_score: float = 0.0, github_status: str = "", detail: str = ""):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO audit_log (thread_id, event_type, verdict, similarity_score, github_status, detail, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (thread_id, event_type, verdict, similarity_score, github_status, detail, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()


def get_audit_log(limit: int = 100):
    conn = _get_conn()
    rows = conn.execute(
        "SELECT thread_id, event_type, verdict, similarity_score, github_status, detail, created_at FROM audit_log ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [
        {
            "thread_id": r[0],
            "event_type": r[1],
            "verdict": r[2],
            "similarity_score": r[3],
            "github_status": r[4],
            "detail": r[5],
            "created_at": r[6],
        }
        for r in rows
    ]
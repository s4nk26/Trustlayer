"""
SQLite Database Schema, Persistence & Analytics Layer
TrustLayer: Human Verification for the AI Era
Zeal College of Engineering & Research, Pune-41
"""

import sqlite3
import json
import os
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verifications.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the verification records SQLite table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            verdict TEXT NOT NULL,
            score REAL NOT NULL,
            confidence_level TEXT NOT NULL,
            challenges_completed INTEGER NOT NULL,
            total_challenges INTEGER NOT NULL,
            duration_sec REAL NOT NULL,
            details_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_verification(session_data: dict) -> int:
    """
    Inserts or updates a completed verification session in SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    session_id = session_data.get("session_id", "UNKNOWN")
    verdict = session_data.get("verdict", "FAILED")
    score = float(session_data.get("score", 0.0))
    confidence = session_data.get("confidence_level", "N/A")
    completed = len(session_data.get("completed_challenges", []))
    total = int(session_data.get("total_challenges", 3))
    duration = float(session_data.get("duration_sec", 0.0))
    details = json.dumps(session_data)

    cursor.execute("""
        INSERT OR REPLACE INTO verifications 
        (session_id, verdict, score, confidence_level, challenges_completed, total_challenges, duration_sec, details_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, verdict, score, confidence, completed, total, duration, details))

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_all_verifications(limit: int = 100) -> list:
    """
    Fetches the most recent verification sessions.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_id, timestamp, verdict, score, confidence_level, 
               challenges_completed, total_challenges, duration_sec 
        FROM verifications 
        ORDER BY id DESC 
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_verification_by_session_id(session_id: str) -> dict:
    """
    Retrieves full verification details for a given session.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM verifications WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["details"] = json.loads(data["details_json"])
        del data["details_json"]
        return data
    return None


def get_dashboard_analytics() -> dict:
    """
    Aggregates overall system KPIs and analytics for the Admin Dashboard.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM verifications")
    total_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM verifications WHERE verdict = 'VERIFIED'")
    verified_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM verifications WHERE verdict = 'SUSPICIOUS'")
    suspicious_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM verifications WHERE verdict = 'FAILED'")
    failed_count = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score), AVG(duration_sec) FROM verifications")
    avg_row = cursor.fetchone()
    avg_score = round(avg_row[0], 1) if avg_row and avg_row[0] is not None else 0.0
    avg_duration = round(avg_row[1], 2) if avg_row and avg_row[1] is not None else 0.0

    pass_rate = round((verified_count / max(1, total_count)) * 100.0, 1) if total_count > 0 else 0.0

    # Score distribution brackets
    cursor.execute("SELECT COUNT(*) FROM verifications WHERE score >= 80")
    bracket_high = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM verifications WHERE score >= 50 AND score < 80")
    bracket_med = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM verifications WHERE score < 50")
    bracket_low = cursor.fetchone()[0]

    conn.close()

    return {
        "total_verifications": total_count,
        "verified_count": verified_count,
        "suspicious_count": suspicious_count,
        "failed_count": failed_count,
        "pass_rate_pct": pass_rate,
        "avg_score_pct": avg_score,
        "avg_duration_sec": avg_duration,
        "score_distribution": {
            "high_80_100": bracket_high,
            "medium_50_79": bracket_med,
            "low_0_49": bracket_low
        }
    }



# Aliases for server endpoints compatibility
get_verification_stats = get_dashboard_analytics
get_recent_verifications = get_all_verifications

# Auto-initialize database on import
init_db()

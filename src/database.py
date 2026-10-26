"""
SQLite Database Storage Module for MediGuide AI.
Provides local, privacy-conscious electronic health record (EHR) persistence
with full Patient ID indexing, longitudinal medical history retrieval, and parameterized SQL queries.
"""

import json
import logging
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

from src.config import DEFAULT_DB_PATH
from src.models import PatientSession

logger = logging.getLogger(__name__)


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create a database connection with row factory enabled."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize database tables with parameterized schema and auto-migration."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT DEFAULT 'MG-2026-0001',
                patient_name TEXT DEFAULT 'Patient',
                gender TEXT DEFAULT 'Male',
                blood_group TEXT DEFAULT 'Unknown',
                created_at TEXT NOT NULL,
                symptoms_text TEXT NOT NULL,
                age_group TEXT NOT NULL,
                duration TEXT NOT NULL,
                severity INTEGER NOT NULL,
                triage_level TEXT NOT NULL,
                suggested_specialty TEXT NOT NULL,
                assessment_json TEXT NOT NULL,
                country TEXT DEFAULT 'India 🇮🇳',
                language TEXT DEFAULT 'English',
                emergency_contact TEXT DEFAULT '',
                notes TEXT
            )
        """)

        # Auto-migrate existing columns if missing
        cursor.execute("PRAGMA table_info(patient_sessions)")
        existing_cols = [row["name"] for row in cursor.fetchall()]

        migration_cols = {
            "patient_id": "TEXT DEFAULT 'MG-2026-0001'",
            "patient_name": "TEXT DEFAULT 'Patient'",
            "gender": "TEXT DEFAULT 'Male'",
            "blood_group": "TEXT DEFAULT 'Unknown'",
            "country": "TEXT DEFAULT 'India 🇮🇳'",
            "language": "TEXT DEFAULT 'English'",
            "emergency_contact": "TEXT DEFAULT ''"
        }

        for col, col_type in migration_cols.items():
            if col not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE patient_sessions ADD COLUMN {col} {col_type}")
                except Exception as e:
                    logger.warning(f"Could not add column {col}: {e}")

        # Index on patient_id for fast clinical history lookup
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_id ON patient_sessions(patient_id)")

        conn.commit()
        logger.info("Database initialized successfully with EHR patient indexing.")


def save_session(session: PatientSession, db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Save a new clinical assessment session record linked to a Patient ID.
    Returns newly inserted session_id.
    """
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patient_sessions (
                patient_id,
                patient_name,
                gender,
                blood_group,
                created_at,
                symptoms_text,
                age_group,
                duration,
                severity,
                triage_level,
                suggested_specialty,
                assessment_json,
                country,
                language,
                emergency_contact,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.patient_id or "MG-2026-0001",
            session.patient_name or "Patient",
            session.gender or "Male",
            session.blood_group or "Unknown",
            session.created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            session.symptoms_text,
            session.age_group,
            session.duration,
            session.severity,
            session.triage_level,
            session.suggested_specialty,
            session.assessment_json,
            session.country or "India 🇮🇳",
            session.language or "English",
            session.emergency_contact or "",
            session.notes or ""
        ))
        conn.commit()
        return cursor.lastrowid


def get_all_sessions(db_path: str = DEFAULT_DB_PATH, limit: int = 100) -> List[Dict]:
    """Retrieve all saved patient assessment sessions ordered by most recent."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM patient_sessions
            ORDER BY session_id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_patient_history(patient_id: str, db_path: str = DEFAULT_DB_PATH) -> List[Dict]:
    """
    Retrieve the complete longitudinal medical consultation history for a given Patient ID.
    Ordered chronologically (newest first).
    """
    init_db(db_path)
    clean_id = patient_id.strip()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM patient_sessions
            WHERE UPPER(patient_id) = UPPER(?)
            ORDER BY session_id DESC
        """, (clean_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_all_patient_ids(db_path: str = DEFAULT_DB_PATH) -> List[str]:
    """Return distinct list of all registered Patient IDs."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT patient_id FROM patient_sessions ORDER BY session_id DESC")
        rows = cursor.fetchall()
        return [row["patient_id"] for row in rows if row["patient_id"]]


def get_session_by_id(session_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict]:
    """Retrieve a single session by primary key ID."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patient_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_session(session_id: int, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Delete a specific session by ID using parameterized query."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patient_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_all_sessions(db_path: str = DEFAULT_DB_PATH) -> int:
    """Wipe all saved session records."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patient_sessions")
        conn.commit()
        return cursor.rowcount


def get_session_count(db_path: str = DEFAULT_DB_PATH) -> int:
    """Count total saved sessions."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patient_sessions")
        count = cursor.fetchone()[0]
        return count


def get_next_patient_id(db_path: str = DEFAULT_DB_PATH) -> str:
    """
    Generate sequential Patient ID e.g. MG-2026-01, MG-2026-02.
    Queries database for highest existing sequential ID and increments.
    """
    init_db(db_path)
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT patient_id FROM patient_sessions")
            ids = [row["patient_id"] for row in cursor.fetchall() if row["patient_id"]]
            seq_numbers = []
            for pid in ids:
                if pid and pid.startswith("MG-2026-"):
                    suffix = pid.replace("MG-2026-", "")
                    if suffix.isdigit():
                        seq_numbers.append(int(suffix))
            next_num = max(seq_numbers) + 1 if seq_numbers else 1
            return f"MG-2026-{next_num:02d}"
    except Exception as e:
        logger.warning(f"Error determining next sequential patient ID: {e}")
        return "MG-2026-01"

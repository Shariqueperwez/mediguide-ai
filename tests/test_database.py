"""
Unit tests for SQLite Database persistence in MediGuide AI.
Validates parameterized operations: insert, query, delete, and wipe.
"""

import os
import unittest
from pathlib import Path
from src.database import (
    init_db,
    save_session,
    get_all_sessions,
    get_session_by_id,
    delete_session,
    clear_all_sessions,
    get_session_count
)
from src.models import PatientSession


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = str(Path(__file__).parent / "test_mediguide.db")
        init_db(self.test_db_path)
        clear_all_sessions(self.test_db_path)

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def test_save_and_retrieve_session(self):
        session = PatientSession(
            created_at="2026-10-19 12:00:00",
            symptoms_text="Fever and chills since yesterday",
            age_group="Adult (18-64)",
            duration="1-3 days",
            severity=4,
            triage_level="ROUTINE",
            suggested_specialty="General Physician",
            assessment_json='{"symptom_summary": ["Fever"]}',
            notes="Follow up in 48 hours"
        )
        sid = save_session(session, db_path=self.test_db_path)
        self.assertGreater(sid, 0)

        # Retrieve
        fetched = get_session_by_id(sid, db_path=self.test_db_path)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["symptoms_text"], "Fever and chills since yesterday")
        self.assertEqual(fetched["severity"], 4)

        # Count
        count = get_session_count(db_path=self.test_db_path)
        self.assertEqual(count, 1)

    def test_delete_session(self):
        session = PatientSession(
            created_at="2026-10-19 12:00:00",
            symptoms_text="Toothache",
            age_group="Adult",
            duration="1 day",
            severity=5,
            triage_level="ROUTINE",
            suggested_specialty="Dentistry",
            assessment_json="{}",
            notes=""
        )
        sid = save_session(session, db_path=self.test_db_path)
        deleted = delete_session(sid, db_path=self.test_db_path)
        self.assertTrue(deleted)
        self.assertIsNone(get_session_by_id(sid, db_path=self.test_db_path))

    def test_get_next_patient_id_sequential(self):
        from src.database import get_next_patient_id
        # First ID should be MG-2026-01
        self.assertEqual(get_next_patient_id(self.test_db_path), "MG-2026-01")

        # Save session with MG-2026-01
        session1 = PatientSession(
            patient_id="MG-2026-01",
            patient_name="Patient 1",
            symptoms_text="Fever",
            age_group="Adult",
            duration="1 day",
            severity=3,
            triage_level="ROUTINE",
            suggested_specialty="General Physician",
            assessment_json="{}"
        )
        save_session(session1, db_path=self.test_db_path)

        # Next ID should be MG-2026-02
        self.assertEqual(get_next_patient_id(self.test_db_path), "MG-2026-02")


if __name__ == "__main__":
    unittest.main()

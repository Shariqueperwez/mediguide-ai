"""
Unit tests for Report Generator and AI Service in MediGuide AI.
Validates PDF generation with ReportLab, CSV exports, and offline AI fallbacks.
"""

import unittest
from src.models import UserSymptomProfile, StructuredAssessment, TriageLevel
from src.ai_service import ai_service
from src.report_generator import generate_pdf_report, generate_csv_export


class TestReportAndAIService(unittest.TestCase):
    def test_pdf_report_generation(self):
        """Verify that ReportLab builds a valid PDF byte buffer without crashing."""
        sample_data = {
            "created_at": "2026-10-19 14:00:00",
            "symptoms_text": "Throbbing headache and slight fever",
            "age_group": "Adult (18-64)",
            "duration": "2 days",
            "severity": 4,
            "triage_level": "ROUTINE",
            "suggested_specialty": "General Physician",
            "recommended_action": "Consult a general physician if symptoms persist.",
            "assessment_json": '{"possible_explanations": ["Tension headache", "Viral infection"], "general_guidance": ["Rest", "Hydration"]}',
            "notes": "Patient reports no prior migraine history."
        }
        pdf_bytes = generate_pdf_report(sample_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 500)
        # Check PDF file signature
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_csv_export(self):
        """Verify CSV export formatting."""
        sessions = [
            {
                "session_id": 1,
                "created_at": "2026-10-19 14:00:00",
                "symptoms_text": "Cough and sore throat",
                "age_group": "Adult (18-64)",
                "duration": "3 days",
                "severity": 3,
                "triage_level": "ROUTINE",
                "suggested_specialty": "Otolaryngology (ENT)",
                "notes": ""
            }
        ]
        csv_str = generate_csv_export(sessions)
        self.assertIn("Session ID", csv_str)
        self.assertIn("Cough and sore throat", csv_str)

    def test_ai_service_offline_demo_fallback(self):
        """Verify that AI service returns a validated StructuredAssessment even in demo mode."""
        profile = UserSymptomProfile(
            symptoms_text="Severe chest pain radiating to left arm",
            age_group="Adult (18-64)",
            duration="1 hour",
            severity=9
        )
        assessment, source = ai_service.assess_symptoms(profile)
        self.assertIsInstance(assessment, StructuredAssessment)
        self.assertEqual(assessment.triage_level, TriageLevel.EMERGENCY)
        self.assertTrue(assessment.requires_urgent_evaluation)
        self.assertTrue(len(assessment.warning_signs) > 0)


if __name__ == "__main__":
    unittest.main()

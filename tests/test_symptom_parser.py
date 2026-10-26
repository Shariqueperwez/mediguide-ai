"""
Unit tests for SymptomParser in MediGuide AI.
Validates entity extraction, duration recognition, and missing information detection.
"""

import unittest
from src.symptom_parser import SymptomParser


class TestSymptomParser(unittest.TestCase):
    def test_symptom_extraction(self):
        text = "I have had a throbbing headache, slight fever, and nausea since yesterday."
        symptoms = SymptomParser.extract_symptoms(text)
        self.assertIn("Headache", symptoms)
        self.assertIn("Fever", symptoms)
        self.assertIn("Nausea", symptoms)

    def test_duration_extraction_yesterday(self):
        text = "I have a sore throat since yesterday."
        duration = SymptomParser.extract_duration(text)
        self.assertIn("yesterday", duration.lower())

    def test_duration_extraction_days(self):
        text = "I have had a cough for 3 days."
        duration = SymptomParser.extract_duration(text)
        self.assertIn("3 days", duration.lower())

    def test_missing_information_detection(self):
        # Text with no temperature, no onset, no medications
        text = "I feel sick with fever."
        missing, follow_ups = SymptomParser.identify_missing_information(text)
        self.assertTrue(len(missing) > 0)
        self.assertTrue(len(follow_ups) > 0)
        # Should ask about thermometer / body temperature
        has_temp_q = any("temperature" in q.lower() or "thermometer" in q.lower() for q in follow_ups)
        self.assertTrue(has_temp_q)

    def test_body_area_extraction(self):
        text = "Sharp pain in my knee and lower back."
        systems = SymptomParser.extract_body_systems(text)
        self.assertIn("Joints", systems)
        self.assertIn("Back", systems)


if __name__ == "__main__":
    unittest.main()

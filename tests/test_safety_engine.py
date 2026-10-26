"""
Unit tests for the Independent Safety Engine in MediGuide AI.
Validates emergency detection, rule coverage, and false-positive prevention.
"""

import unittest
from src.safety_engine import SafetyEngine, TriageLevel


class TestSafetyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SafetyEngine()

    def test_emergency_chest_pain(self):
        """Acute chest pain with radiation should trigger EMERGENCY triage."""
        text = "I have severe crushing chest pain radiating to my left arm and jaw"
        res = self.engine.evaluate(text)
        self.assertTrue(res.is_emergency)
        self.assertEqual(res.triage_level, TriageLevel.EMERGENCY)
        self.assertIn("112", res.recommended_action)

    def test_emergency_stroke_fast(self):
        """Stroke FAST signs must trigger EMERGENCY triage."""
        text = "My mother has sudden facial drooping and slurred speech"
        res = self.engine.evaluate(text)
        self.assertTrue(res.is_emergency)
        self.assertEqual(res.triage_level, TriageLevel.EMERGENCY)

    def test_emergency_respiratory_distress(self):
        """Severe shortness of breath with cyanosis must trigger EMERGENCY triage."""
        text = "Gasping for air, severe difficulty breathing and my lips are turning blue"
        res = self.engine.evaluate(text)
        self.assertTrue(res.is_emergency)
        self.assertEqual(res.triage_level, TriageLevel.EMERGENCY)

    def test_emergency_anaphylaxis(self):
        """Swollen throat and tongue must trigger EMERGENCY triage."""
        text = "My throat and tongue are swelling up rapidly after eating nuts and I cannot swallow"
        res = self.engine.evaluate(text)
        self.assertTrue(res.is_emergency)
        self.assertEqual(res.triage_level, TriageLevel.EMERGENCY)

    def test_emergency_uncontrolled_hemorrhage(self):
        """Uncontrolled spurting bleeding must trigger EMERGENCY triage."""
        text = "Deep cut on my leg with uncontrolled heavy bleeding that won't stop"
        res = self.engine.evaluate(text)
        self.assertTrue(res.is_emergency)
        self.assertEqual(res.triage_level, TriageLevel.EMERGENCY)

    def test_urgent_severe_abdominal_pain(self):
        """Excruciating abdominal pain should trigger URGENT triage."""
        text = "Worst abdominal pain of my life in the right lower belly with fever"
        res = self.engine.evaluate(text)
        self.assertTrue(res.is_urgent)
        self.assertEqual(res.triage_level, TriageLevel.URGENT)

    def test_urgent_infant_fever(self):
        """Infant under 3 months with fever must trigger URGENT triage."""
        text = "My 2 month old baby has fever of 101"
        res = self.engine.evaluate(text)
        self.assertTrue(res.is_urgent)

    def test_non_emergency_mild_headache(self):
        """Mild headache should not trigger emergency flags."""
        text = "I have a mild headache from working late on the computer"
        res = self.engine.evaluate(text, severity=2)
        self.assertFalse(res.is_emergency)
        self.assertFalse(res.is_urgent)
        self.assertEqual(res.triage_level, TriageLevel.SELF_CARE)

    def test_routine_rash(self):
        """Mild itching and rash should be routed to routine outpatient care."""
        text = "Mild itchy rash on my arm for two days"
        res = self.engine.evaluate(text, severity=4)
        self.assertFalse(res.is_emergency)
        self.assertEqual(res.triage_level, TriageLevel.ROUTINE)


if __name__ == "__main__":
    unittest.main()

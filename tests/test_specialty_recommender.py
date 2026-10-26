"""
Unit tests for SpecialtyRecommender in MediGuide AI.
Validates mapping of symptoms to medical specialties and emergency overrides.
"""

import unittest
from src.models import TriageLevel
from src.specialty_recommender import specialty_recommender


class TestSpecialtyRecommender(unittest.TestCase):
    def test_dermatology_mapping(self):
        res = specialty_recommender.recommend("I have an itchy red rash and eczema on my arm")
        self.assertEqual(res["specialty"], "Dermatology")

    def test_ophthalmology_mapping(self):
        res = specialty_recommender.recommend("Blurred vision and redness in my left eye")
        self.assertEqual(res["specialty"], "Ophthalmology")

    def test_dentistry_mapping(self):
        res = specialty_recommender.recommend("Severe toothache and cavity in molar")
        self.assertEqual(res["specialty"], "Dentistry")

    def test_orthopedics_mapping(self):
        res = specialty_recommender.recommend("Swollen knee and joint pain after sports injury")
        self.assertEqual(res["specialty"], "Orthopedics")

    def test_ent_mapping(self):
        res = specialty_recommender.recommend("Earache, hearing loss, and runny nose with sinus pressure")
        self.assertEqual(res["specialty"], "Otolaryngology (ENT)")

    def test_pediatrics_override(self):
        res = specialty_recommender.recommend("Fever and cough", age_group="Child (2-12)")
        self.assertEqual(res["specialty"], "Pediatrics")

    def test_emergency_override(self):
        res = specialty_recommender.recommend("Crushing chest pain", triage_level=TriageLevel.EMERGENCY)
        self.assertIn("Emergency", res["specialty"])
        self.assertTrue(res["is_emergency_override"])

    def test_fallback_to_general_physician(self):
        res = specialty_recommender.recommend("Feeling generally unwell and tired")
        self.assertIn("General Physician", res["specialty"])


if __name__ == "__main__":
    unittest.main()

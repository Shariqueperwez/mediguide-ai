"""
Unit tests for Provider Search and Geocoding in MediGuide AI.
Validates Haversine distance calculations, coordinate resolution, strict radius enforcement,
and clinically accurate specialty filtering (no unrelated facilities).
"""

import unittest
from src.geocoding_service import haversine_distance, geocoding_service
from src.provider_search import provider_search_service, matches_specialty
from src.specialty_recommender import SPECIALTY_CATALOG
from src.models import HealthcareProvider


class TestProviderSearch(unittest.TestCase):
    def test_haversine_distance_accuracy(self):
        # Known coordinates:
        # Connaught Place Delhi (28.6315, 77.2167) to AIIMS Delhi (28.5672, 77.2100) ~ 7.2 km
        dist = haversine_distance(28.6315, 77.2167, 28.5672, 77.2100)
        self.assertAlmostEqual(dist, 7.2, delta=0.5)

        # Same point should be 0.0
        dist_zero = haversine_distance(12.9716, 77.5946, 12.9716, 77.5946)
        self.assertEqual(dist_zero, 0.0)

    def test_geocoding_preset_resolution(self):
        # Test resolution of common hub
        res = geocoding_service.geocode_location("Delhi")
        self.assertIsNotNone(res)
        lat, lon, name = res
        self.assertAlmostEqual(lat, 28.6139, delta=0.1)

    def test_provider_search_fallback_and_filtering(self):
        # Search around Connaught Place coordinates
        providers = provider_search_service.search_providers(
            latitude=28.6315,
            longitude=77.2167,
            radius_km=25.0
        )
        self.assertTrue(len(providers) > 0)
        # Should be sorted by distance
        distances = [p.distance_km for p in providers if p.distance_km is not None]
        self.assertEqual(distances, sorted(distances))

    def test_strict_radius_enforcement(self):
        # When radius is 15.0 km, NO provider > 15.05 km should ever be returned
        radius = 15.0
        providers = provider_search_service.search_providers(
            latitude=26.1209,
            longitude=85.3647,
            radius_km=radius,
            location_query="Muzaffarpur, Bihar"
        )
        self.assertTrue(len(providers) > 0)
        for p in providers:
            self.assertIsNotNone(p.distance_km)
            self.assertLessEqual(
                p.distance_km,
                radius + 0.05,
                f"Provider {p.name} at {p.distance_km} km exceeds requested radius {radius} km"
            )

    def test_specialty_matching_rejects_unrelated_facilities(self):
        dental_p = HealthcareProvider(
            id="d1", name="Shanti Dental & Maxillofacial Care", provider_type="Clinic",
            specialty="Dentistry, Root Canal & Dental Surgery", address="Kalambagh Road",
            latitude=26.119, longitude=85.376, distance_km=1.2, directions_url="http://maps",
            data_source="Test"
        )
        heart_p = HealthcareProvider(
            id="h1", name="Urmila Heart Hospital", provider_type="Hospital",
            specialty="Cardiology, Cardiac Intensive Care & Emergency", address="Juran Chhapra",
            latitude=26.126, longitude=85.394, distance_km=2.5, directions_url="http://maps",
            data_source="Test"
        )
        eye_p = HealthcareProvider(
            id="e1", name="City Eye Hospital", provider_type="Clinic",
            specialty="Ophthalmology, Cataract & Retina Care", address="Zero Mile",
            latitude=26.146, longitude=85.405, distance_km=3.0, directions_url="http://maps",
            data_source="Test"
        )

        # Dentistry should match dental_p, and reject heart_p and eye_p
        self.assertTrue(matches_specialty(dental_p, "Dentistry"))
        self.assertFalse(matches_specialty(heart_p, "Dentistry"))
        self.assertFalse(matches_specialty(eye_p, "Dentistry"))

        # Cardiology should match heart_p, and reject dental_p and eye_p
        self.assertTrue(matches_specialty(heart_p, "Cardiology"))
        self.assertFalse(matches_specialty(dental_p, "Cardiology"))
        self.assertFalse(matches_specialty(eye_p, "Cardiology"))

    def test_specialty_catalog_has_emergency_medicine(self):
        # Emergency Medicine / Trauma Center must be in SPECIALTY_CATALOG
        names = [s.specialty for s in SPECIALTY_CATALOG]
        self.assertIn("Emergency Medicine / Trauma Center", names)

    def test_muzaffarpur_ophthalmology_returns_multiple_eye_hospitals(self):
        # Searching Ophthalmology in Muzaffarpur should return multiple prominent eye hospitals
        providers = provider_search_service.search_providers(
            latitude=26.1209,
            longitude=85.3647,
            radius_km=15.0,
            specialty_filter="Ophthalmology",
            location_query="Muzaffarpur, Bihar"
        )
        self.assertGreater(len(providers), 1, "Expected multiple eye hospitals in Muzaffarpur")
        names = [p.name for p in providers]
        # Jaiswal Eye Hospital should be present
        has_jaiswal = any("Jaiswal" in n for n in names)
        self.assertTrue(has_jaiswal, f"Jaiswal Eye Hospital should be in results: {names}")


if __name__ == "__main__":
    unittest.main()

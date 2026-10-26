"""
Geocoding and Geospatial Utility Module for MediGuide AI.
Provides coordinate resolution via OpenStreetMap Nominatim,
live automatic user location detection, and tested Haversine distance calculations.
"""

import math
import logging
from typing import Dict, Optional, Tuple
import requests

from src.config import GEOCODING_TIMEOUT_SECONDS, NOMINATIM_BASE_URL, OSM_USER_AGENT, get_active_country

logger = logging.getLogger(__name__)

# Fallback coordinates for major regional hubs
POPULAR_CITY_COORDINATES: Dict[str, Tuple[float, float, str]] = {
    # Bihar, India
    "muzaffarpur": (26.1209, 85.3647, "Muzaffarpur, Bihar, India"),
    "patna": (25.5941, 85.1376, "Patna, Bihar, India"),
    "darbhanga": (26.1542, 85.8918, "Darbhanga, Bihar, India"),
    "gaya": (24.7914, 85.0002, "Gaya, Bihar, India"),
    "bhagalpur": (25.2425, 86.9842, "Bhagalpur, Bihar, India"),
    
    # National & Metro Hubs, India
    "delhi": (28.6139, 77.2090, "New Delhi, Delhi, India"),
    "new delhi": (28.6139, 77.2090, "New Delhi, Delhi, India"),
    "connaught place": (28.6315, 77.2167, "Connaught Place, New Delhi, India"),
    "bangalore": (12.9716, 77.5946, "Bengaluru, Karnataka, India"),
    "bengaluru": (12.9716, 77.5946, "Bengaluru, Karnataka, India"),
    "indiranagar": (12.9784, 77.6408, "Indiranagar, Bengaluru, Karnataka, India"),
    "mumbai": (19.0760, 72.8777, "Mumbai, Maharashtra, India"),
    "bandra": (19.0596, 72.8295, "Bandra, Mumbai, Maharashtra, India"),
    "hyderabad": (17.3850, 78.4867, "Hyderabad, Telangana, India"),
    "chennai": (13.0827, 80.2707, "Chennai, Tamil Nadu, India"),
    "kolkata": (22.5726, 88.3639, "Kolkata, West Bengal, India"),
    "pune": (18.5204, 73.8567, "Pune, Maharashtra, India"),
    "lucknow": (26.8467, 80.9462, "Lucknow, Uttar Pradesh, India"),
    "ahmedabad": (23.0225, 72.5714, "Ahmedabad, Gujarat, India"),
    "jaipur": (26.9124, 75.7873, "Jaipur, Rajasthan, India"),
    "chandigarh": (30.7333, 76.7794, "Chandigarh, India"),
    "ranchi": (23.3441, 85.3096, "Ranchi, Jharkhand, India")
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    R = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(R * c, 2)


def detect_current_location() -> Optional[Dict]:
    """
    Auto-detect user's current live geographic location using high-speed IP geolocation.
    Returns dictionary with city, region, country, lat, lon, and formatted display name.
    """
    providers = [
        {"url": "http://ip-api.com/json/", "lat": "lat", "lon": "lon", "city": "city", "region": "regionName", "country": "country"},
        {"url": "https://ipwhois.app/json/", "lat": "latitude", "lon": "longitude", "city": "city", "region": "region", "country": "country"},
        {"url": "https://freeipapi.com/api/json", "lat": "latitude", "lon": "longitude", "city": "cityName", "region": "regionName", "country": "countryName"}
    ]

    for p in providers:
        try:
            resp = requests.get(p["url"], timeout=3.5)
            if resp.status_code == 200:
                data = resp.json()
                lat = data.get(p["lat"])
                lon = data.get(p["lon"])
                city = data.get(p["city"]) or "Local Area"
                region = data.get(p["region"]) or ""
                country = data.get(p["country"]) or "India"

                if lat is not None and lon is not None:
                    lat_f = float(lat)
                    lon_f = float(lon)
                    display = f"{city}, {region}, {country}".replace(", ,", ",").strip(", ")
                    return {
                        "city": city,
                        "region": region,
                        "country": country,
                        "latitude": lat_f,
                        "longitude": lon_f,
                        "display_name": display
                    }
        except Exception as e:
            logger.warning(f"Live location detection provider failed ({p['url']}): {e}")
            continue

    # Graceful default to Muzaffarpur, Bihar
    return {
        "city": "Muzaffarpur",
        "region": "Bihar",
        "country": "India",
        "latitude": 26.1209,
        "longitude": 85.3647,
        "display_name": "Muzaffarpur, Bihar, India"
    }


class GeocodingService:
    """Handles country-aware geocoding requests with caching and OSM compliance."""

    def __init__(self):
        self._cache: Dict[str, Tuple[float, float, str]] = dict(POPULAR_CITY_COORDINATES)

    def geocode_location(self, query: str, country_code: str = "") -> Optional[Tuple[float, float, str]]:
        """
        Convert a user location string into (latitude, longitude, display_name).
        Uses country_code if specified to narrow down search and avoid ambiguity.
        """
        clean_query = query.strip().lower()
        if not clean_query:
            return None

        # Check local cache first
        for key, val in self._cache.items():
            if key in clean_query or clean_query in key:
                logger.info(f"Geocoding resolved via local cache for '{query}'")
                return val

        if not country_code:
            country_cfg = get_active_country()
            country_code = country_cfg.get("code", "")

        # Query OpenStreetMap Nominatim API
        try:
            url = f"{NOMINATIM_BASE_URL}/search"
            params = {
                "q": query,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            if country_code:
                params["countrycodes"] = country_code

            headers = {
                "User-Agent": OSM_USER_AGENT
            }

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=GEOCODING_TIMEOUT_SECONDS
            )

            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    first = results[0]
                    lat = float(first["lat"])
                    lon = float(first["lon"])
                    display_name = first.get("display_name", query)
                    # Cache result
                    self._cache[clean_query] = (lat, lon, display_name)
                    return lat, lon, display_name

        except Exception as e:
            logger.warning(f"Geocoding network query failed for '{query}': {e}")

        # Check partial fallback in dictionary
        for key, val in POPULAR_CITY_COORDINATES.items():
            if key in clean_query:
                return val

        return None

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """Convert latitude and longitude coordinates into a human-readable address."""
        try:
            url = f"{NOMINATIM_BASE_URL}/reverse"
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "zoom": 16,
                "addressdetails": 1
            }
            headers = {"User-Agent": OSM_USER_AGENT}
            response = requests.get(url, params=params, headers=headers, timeout=GEOCODING_TIMEOUT_SECONDS)
            if response.status_code == 200:
                data = response.json()
                display_name = data.get("display_name")
                if display_name:
                    return display_name
        except Exception as e:
            logger.warning(f"Reverse geocoding failed for ({latitude}, {longitude}): {e}")
        return None


geocoding_service = GeocodingService()


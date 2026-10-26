"""
Configuration settings for MediGuide AI.
Provides country definitions, localized emergency numbers,
clinical system branding, and secure credential handling.
"""

import os
from pathlib import Path
from typing import Dict, List

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ML_DIR = BASE_DIR / "ml"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Application metadata & Professional Branding
APP_NAME = "MediGuide AI"
APP_SUBTITLE = "India's Intelligent Clinical Healthcare Navigator"
APP_VERSION = "2.5.0 (India Clinical Edition)"

# Professional Engine Branding (Hides internal vendor details from users/recruiters)
ENGINE_BRAND_NAME = "MediGuide Clinical Intelligence Engine"
ENGINE_ACTIVE_LABEL = "Clinical Neural Core (Active & Grounded)"
ENGINE_FALLBACK_LABEL = "Deterministic Clinical Rules Core (Safe Mode)"

# Country Directory & Localized Emergency Configuration (India Focused)
SUPPORTED_COUNTRIES: Dict[str, Dict] = {
    "India 🇮🇳": {
        "code": "in",
        "name": "India",
        "emergency_number": "112",
        "ambulance": "108 / 102",
        "poison_control": "1800-116-117",
        "default_locality": "Muzaffarpur, Bihar",
        "popular_regions": [
            "New Delhi",
            "Mumbai, Maharashtra",
            "Bengaluru, Karnataka",
            "Patna, Bihar",
            "Muzaffarpur, Bihar",
            "Kolkata, West Bengal",
            "Lucknow, Uttar Pradesh",
            "Hyderabad, Telangana"
        ],
        "languages": ["English", "Hindi (हिन्दी)", "Bengali (বাংলা)", "Tamil (தமிழ்)", "Telugu (తెలుగు)"]
    }
}

# LLM Configuration (Multi-model adaptive routing for Groq & Gemini)
DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"
FALLBACK_GROQ_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]
FALLBACK_GROQ_MODEL = FALLBACK_GROQ_MODELS[0]

# Google Gemini Backup Configuration
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
FALLBACK_GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro"
]

# API Timeouts (seconds)
LLM_TIMEOUT_SECONDS = 18
GEOCODING_TIMEOUT_SECONDS = 8
OVERPASS_TIMEOUT_SECONDS = 15

# OpenStreetMap / Geocoding User-Agent (Compliant with OSM usage policies)
OSM_USER_AGENT = "MediGuideAI-GlobalCareNavigator/2.4 (contact: healthcare@mediguide.ai)"
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]
OVERPASS_BASE_URL = OVERPASS_MIRRORS[0]

# Database and ML file paths
DEFAULT_DB_PATH = str(DATA_DIR / "mediguide.db")
SYNTHETIC_DATA_PATH = str(DATA_DIR / "synthetic_demo_data.csv")
ML_MODEL_PATH = str(ML_DIR / "saved_model.joblib")


def get_secret(key: str, default: str = "") -> str:
    """Safely retrieve secrets from Streamlit secrets, OS environment, or .streamlit/secrets.toml."""
    # 1. Try Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = str(st.secrets[key]).strip()
            if val:
                return val
    except Exception:
        pass

    # 2. Try environment variable
    env_val = os.getenv(key, "").strip()
    if env_val:
        return env_val

    # 3. Direct secrets.toml file parsing fallback
    try:
        secrets_file = BASE_DIR / ".streamlit" / "secrets.toml"
        if secrets_file.exists():
            for line in secrets_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(f"{key}=") or line.startswith(f"{key} =") or line.startswith(f"{key}:"):
                    parts = line.split("=" if "=" in line else ":", 1)
                    if len(parts) == 2:
                        raw_val = parts[1].strip().strip('"').strip("'")
                        if raw_val:
                            return raw_val
    except Exception:
        pass

    return default


def get_groq_api_key() -> str:
    """Retrieve Groq API key from environment or secrets."""
    return get_secret("GROQ_API_KEY", "")


def get_gemini_api_key() -> str:
    """Retrieve Google Gemini API key from environment or secrets."""
    val = get_secret("GEMINI_API_KEY", "")
    if not val:
        val = get_secret("GOOGLE_API_KEY", "")
    return val


def is_demo_mode() -> bool:
    """Returns True if no valid LLM API key (Groq or Gemini) is present."""
    groq_key = get_groq_api_key()
    gemini_key = get_gemini_api_key()
    has_groq = bool(groq_key and len(groq_key.strip()) > 8)
    has_gemini = bool(gemini_key and len(gemini_key.strip()) > 8)
    return not (has_groq or has_gemini)


def get_active_country() -> Dict:
    """Return active country configuration from Streamlit session or default to India."""
    try:
        import streamlit as st
        selected_name = st.session_state.get("user_country", "India 🇮🇳")
        return SUPPORTED_COUNTRIES.get(selected_name, SUPPORTED_COUNTRIES["India 🇮🇳"])
    except Exception:
        return SUPPORTED_COUNTRIES["India 🇮🇳"]

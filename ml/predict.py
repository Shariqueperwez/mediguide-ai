"""
ML Inference Prediction Interface for MediGuide AI.
Provides clean API to predict triage urgency level and specialty routing
from free-text symptoms using the trained scikit-learn pipelines.
"""

from pathlib import Path
from typing import Dict, Optional
import joblib

from src.config import ML_MODEL_PATH

_cached_artifacts: Optional[Dict] = None


def load_ml_pipeline() -> Optional[Dict]:
    """Lazy-load and cache the machine learning artifacts."""
    global _cached_artifacts
    if _cached_artifacts is not None:
        return _cached_artifacts

    model_path = Path(ML_MODEL_PATH)
    if not model_path.exists():
        return None

    try:
        _cached_artifacts = joblib.load(model_path)
        return _cached_artifacts
    except Exception:
        return None


def predict_care_navigation(symptoms_text: str) -> Dict:
    """
    Predict care navigation urgency and medical specialty using ML pipeline.
    Returns:
    {
        "is_available": bool,
        "predicted_triage": str,
        "triage_confidence": float,
        "predicted_specialty": str,
        "explanation": str
    }
    """
    artifacts = load_ml_pipeline()
    if not artifacts:
        return {
            "is_available": False,
            "predicted_triage": "ROUTINE",
            "triage_confidence": 0.0,
            "predicted_specialty": "General Physician",
            "explanation": "ML Model pipeline not trained or unavailable. Using rule-based engine."
        }

    try:
        triage_model = artifacts["triage_pipeline"]
        specialty_model = artifacts["specialty_pipeline"]

        # Inference
        triage_pred = triage_model.predict([symptoms_text])[0]
        triage_probs = triage_model.predict_proba([symptoms_text])[0]
        max_triage_prob = float(max(triage_probs))

        spec_pred = specialty_model.predict([symptoms_text])[0]

        return {
            "is_available": True,
            "predicted_triage": str(triage_pred),
            "triage_confidence": round(max_triage_prob, 3),
            "predicted_specialty": str(spec_pred),
            "explanation": f"ML model categorized urgency as {triage_pred} with {max_triage_prob*100:.1f}% confidence."
        }
    except Exception as e:
        return {
            "is_available": False,
            "predicted_triage": "ROUTINE",
            "triage_confidence": 0.0,
            "predicted_specialty": "General Physician",
            "explanation": f"Inference failed: {e}"
        }

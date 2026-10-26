"""
Pydantic data models for MediGuide AI.
Provides strict validation for user input, patient identity (Name & ID),
clinical context, AI responses, RAG protocol citations, and provider records.
"""

from enum import Enum
import random
import string
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def generate_patient_id() -> str:
    """Generate sequential Patient ID e.g. MG-2026-01, MG-2026-02."""
    try:
        from src.database import get_next_patient_id
        return get_next_patient_id()
    except Exception:
        return "MG-2026-01"


class TriageLevel(str, Enum):
    """Categorization of clinical urgency for routing purposes."""
    EMERGENCY = "EMERGENCY"      # Immediate emergency medical assistance needed (Call 112 / 911)
    URGENT = "URGENT"            # Seek prompt medical evaluation within 12-24 hours
    ROUTINE = "ROUTINE"          # Schedule a standard clinical appointment with a doctor
    SELF_CARE = "SELF_CARE"      # Mild symptoms suitable for self-care monitoring & rest


class DemographicCategory(str, Enum):
    """Physiological demographic classification for clinical risk stratification."""
    NEONATE = "Neonate"
    INFANT = "Infant"
    CHILD = "Child"
    TEEN = "Adolescent"
    ADULT = "Adult"
    GERIATRIC = "Older Adult"


def classify_demographic(age: int) -> str:
    """Helper to classify integer age into demographic category."""
    if age <= 0:
        return DemographicCategory.NEONATE.value
    elif age == 1:
        return DemographicCategory.INFANT.value
    elif age <= 12:
        return DemographicCategory.CHILD.value
    elif age <= 17:
        return DemographicCategory.TEEN.value
    elif age <= 64:
        return DemographicCategory.ADULT.value
    else:
        return DemographicCategory.GERIATRIC.value


class UserSymptomProfile(BaseModel):
    """User-provided symptom context, exact patient identity, and clinical history."""
    patient_id: str = Field(default_factory=generate_patient_id, description="Unique hospital / patient identifier")
    patient_name: str = Field(default="Patient", min_length=2, description="Patient's full legal name")
    gender: str = Field(default="Male", description="Biological gender")
    blood_group: Optional[str] = Field(default="Unknown", description="ABO/Rh Blood Group")
    symptoms_text: str = Field(..., min_length=3, description="Free text description of symptoms")
    exact_age: int = Field(default=30, ge=0, le=120, description="Exact patient age in years")
    age_group: str = Field(default="Adult (18-64 years)", description="Demographic classification")
    duration: str = Field(default="1-3 days", description="Duration of symptoms")
    severity: int = Field(default=3, ge=1, le=10, description="Self-reported pain/severity scale from 1 to 10")
    is_pregnant: bool = Field(default=False, description="Whether patient is currently pregnant")
    trimester: Optional[str] = Field(default=None, description="Trimester if pregnant (1st, 2nd, 3rd, Postpartum)")
    medical_history: Optional[str] = Field(default="", description="Relevant known medical conditions or notes")
    current_medications: Optional[str] = Field(default="", description="Prescription or OTC medications currently taken")
    emergency_contact: Optional[str] = Field(default="", description="Emergency contact phone number or relation")
    country: str = Field(default="India 🇮🇳", description="Selected patient country for localized protocols")
    language: str = Field(default="English", description="Target language for clinical guidance and reports")


class StructuredAssessment(BaseModel):
    """
    Validated structured schema for health navigation and guidance.
    Enforces medical boundaries and integrates RAG protocol citations.
    """
    symptom_summary: List[str] = Field(
        default_factory=list,
        description="Concise bullet points of patient-reported symptoms."
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="Important clinical details that are unknown or not provided by the user."
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="Targeted follow-up questions to ask the user."
    )
    possible_explanations: List[str] = Field(
        default_factory=list,
        description="Non-definitive general health possibilities, strictly labeled as possibilities."
    )
    general_guidance: List[str] = Field(
        default_factory=list,
        description="Evidence-based self-care and general comfort measures when appropriate."
    )
    recommended_next_step: str = Field(
        ...,
        description="Actionable next step (e.g., 'Consult a general physician', 'Visit urgent care')."
    )
    suggested_specialty: Optional[str] = Field(
        default="General Physician",
        description="Relevant medical specialty for referral navigation."
    )
    warning_signs: List[str] = Field(
        default_factory=list,
        description="Red flag symptoms that necessitate immediate emergency attention."
    )
    triage_level: TriageLevel = Field(
        default=TriageLevel.ROUTINE,
        description="Safety routing triage classification."
    )
    requires_urgent_evaluation: bool = Field(
        default=False,
        description="Whether medical evaluation should be sought immediately or promptly."
    )
    retrieved_protocols: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Clinical guidelines and evidence citations retrieved by the RAG engine."
    )
    disclaimer: str = Field(
        default=(
            "MediGuide AI provides general health information and care navigation for educational "
            "purposes only. It does not provide medical diagnosis, prescription, or clinical treatment. "
            "Always consult a qualified healthcare professional for medical concerns."
        ),
        description="Standard medical disclaimer."
    )


class HealthcareProvider(BaseModel):
    """Normalized healthcare facility or practitioner record."""
    id: str = Field(..., description="Unique provider or OSM identifier")
    name: str = Field(..., description="Name of facility or clinic")
    provider_type: str = Field(default="Clinic", description="Hospital, Clinic, Doctor, Pharmacy")
    specialty: str = Field(default="General Healthcare", description="Mapped or stated medical specialty")
    address: str = Field(default="Address not available", description="Street or locality address")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    distance_km: Optional[float] = Field(default=None, description="Calculated distance in km")
    phone: Optional[str] = Field(default=None, description="Contact phone number if officially listed")
    website: Optional[str] = Field(default=None, description="Official website or booking link if available")
    directions_url: Optional[str] = Field(default=None, description="Map directions URL")
    data_source: str = Field(default="OpenStreetMap Contributors", description="Data provenance")
    is_verified: bool = Field(default=True, description="Whether record is from a validated source")


class PatientSession(BaseModel):
    """Record of an assessment session for local SQLite storage or export."""
    session_id: Optional[int] = None
    patient_id: str = Field(default="MG-2026-0001", description="Patient unique identifier")
    patient_name: str = Field(default="Patient", description="Patient legal name")
    gender: Optional[str] = "Male"
    blood_group: Optional[str] = "Unknown"
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    symptoms_text: str
    age_group: str
    duration: str
    severity: int
    triage_level: str
    suggested_specialty: str
    assessment_json: str
    country: Optional[str] = "India 🇮🇳"
    language: Optional[str] = "English"
    emergency_contact: Optional[str] = ""
    notes: Optional[str] = ""

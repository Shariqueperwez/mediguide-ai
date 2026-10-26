"""
Medical Specialty Recommender for MediGuide AI.
Provides a transparent, clinical rule-grounded mapping from broad patient
complaints to appropriate medical specialties.

These suggestions are care navigation aids to guide the user towards
the appropriate clinical department, not definitive medical referrals.
"""

import re
from typing import Dict, List, Optional, Tuple
from src.models import TriageLevel


class SpecialtyMapping:
    """Defines a mapping between clinical keywords and a medical specialty."""
    def __init__(
        self,
        specialty: str,
        category: str,
        keywords: List[str],
        description: str,
        confidence_weight: float = 1.0
    ):
        self.specialty = specialty
        self.category = category
        self.keywords = [re.compile(rf"\b{k}\b", re.IGNORECASE) for k in keywords]
        self.description = description
        self.confidence_weight = confidence_weight

    def score(self, text: str) -> float:
        """Calculate matching score based on keyword frequency."""
        matches = sum(1 for pattern in self.keywords if pattern.search(text))
        return matches * self.confidence_weight


SPECIALTY_CATALOG: List[SpecialtyMapping] = [
    SpecialtyMapping(
        specialty="Emergency Medicine / Trauma Center",
        category="Immediate Emergency Care",
        keywords=[
            "emergency", "trauma", "unconscious", "chest pain", "heart attack", "stroke",
            "severe bleeding", "severe burn", "head injury", "anaphylaxis", "poisoning",
            "collapse", "resuscitation", "casualty"
        ],
        description="Specializes in immediate life support, acute resuscitation, severe trauma, and urgent medical emergencies.",
        confidence_weight=1.5
    ),
    SpecialtyMapping(
        specialty="Dermatology",
        category="Skin, Hair & Nails",
        keywords=[
            "rash", "skin", "eczema", "acne", "pimples", "itching", "itchy",
            "hives", "mole", "blister", "psoriasis", "dermatitis", "fungal",
            "ringworm", "scalp rash", "dry skin", "pigmentation"
        ],
        description="Specializes in skin conditions, rashes, allergic skin reactions, acne, and dermatological disorders."
    ),
    SpecialtyMapping(
        specialty="Ophthalmology",
        category="Eye & Vision",
        keywords=[
            "eye", "eyes", "vision", "blurred vision", "double vision", "pink eye",
            "conjunctivitis", "eye discharge", "watery eyes", "stye", "itchy eyes",
            "floaters", "dry eyes", "eyeball", "eyelid"
        ],
        description="Specializes in eye health, vision problems, eye infections, and optical care."
    ),
    SpecialtyMapping(
        specialty="Dentistry",
        category="Dental & Oral Health",
        keywords=[
            "tooth", "teeth", "toothache", "gum", "gums", "cavity", "wisdom tooth",
            "bleeding gums", "dental", "jaw pain when chewing", "loose tooth", "mouth ulcer"
        ],
        description="Specializes in teeth, gums, oral cavity disorders, and dental hygiene."
    ),
    SpecialtyMapping(
        specialty="Otolaryngology (ENT)",
        category="Ear, Nose & Throat",
        keywords=[
            "ear", "ears", "earache", "hearing", "tinnitus", "ringing in ear",
            "sinus", "sinusitis", "runny nose", "blocked nose", "sore throat",
            "tonsil", "tonsillitis", "hoarse voice", "loss of smell", "ear infection"
        ],
        description="Specializes in disorders of the ear, nose, throat, sinuses, and upper respiratory tract."
    ),
    SpecialtyMapping(
        specialty="Orthopedics",
        category="Musculoskeletal & Bone",
        keywords=[
            "bone", "joint", "joints", "knee", "elbow", "shoulder", "ankle",
            "wrist", "sprain", "fracture", "arthritis", "back pain", "lower back",
            "sciatica", "ligament", "swollen knee", "neck pain", "stiff joint"
        ],
        description="Specializes in bones, joints, ligaments, tendons, spine, and musculoskeletal injuries."
    ),
    SpecialtyMapping(
        specialty="Gastroenterology",
        category="Digestive System",
        keywords=[
            "stomach", "abdomen", "belly", "acid reflux", "heartburn", "gerd",
            "diarrhea", "constipation", "bloating", "nausea", "vomiting", "gas",
            "indigestion", "cramps in stomach", "ulcer", "food poisoning"
        ],
        description="Specializes in the digestive tract, stomach, intestines, liver, and gastrointestinal symptoms."
    ),
    SpecialtyMapping(
        specialty="Cardiology",
        category="Heart & Vascular",
        keywords=[
            "palpitations", "fluttering heart", "rapid heartbeat", "irregular heartbeat",
            "racing pulse", "high blood pressure", "hypertension", "swollen ankles",
            "breathless climbing stairs"
        ],
        description="Specializes in heart disorders, cardiovascular health, and circulatory management."
    ),
    SpecialtyMapping(
        specialty="General Physician / Internal Medicine",
        category="Primary Care & General Medicine",
        keywords=[
            "fever", "pyrexia", "flu", "cold", "body ache", "body aches",
            "fatigue", "weakness", "malaise", "chills", "mild cough", "shivering",
            "viral", "infection", "headache with fever", "fever and headache",
            "fever and cough", "cough and fever", "sore throat with fever", "unwell", "general checkup"
        ],
        description="Specializes in primary adult care, acute viral illnesses, common infections, and overall health evaluations.",
        confidence_weight=1.3
    ),
    SpecialtyMapping(
        specialty="Pulmonology",
        category="Respiratory & Lungs",
        keywords=[
            "chronic cough", "persistent cough", "wheezing", "asthma", "bronchitis",
            "copd", "emphysema", "coughing blood", "hemoptysis", "severe breathlessness",
            "chest congestion with breathing difficulty", "shortness of breath", "lung infection"
        ],
        description="Specializes in chronic pulmonary disease, asthma, COPD, and lower respiratory tract disorders."
    ),
    SpecialtyMapping(
        specialty="Neurology",
        category="Nervous System & Brain",
        keywords=[
            "migraine", "headache", "dizziness", "vertigo", "tingling", "numbness",
            "tremor", "trembling", "loss of balance", "nerve pain", "neuropathy"
        ],
        description="Specializes in the nervous system, brain, recurrent headaches, migraines, and nerve issues."
    ),
    SpecialtyMapping(
        specialty="Psychiatry / Mental Health",
        category="Mental Health",
        keywords=[
            "anxiety", "panic attack", "depression", "depressed", "insomnia", "cannot sleep",
            "stress", "mood swings", "hopelessness", "nervousness", "restlessness"
        ],
        description="Specializes in mental health, emotional well-being, mood disorders, and psychological support."
    ),
    SpecialtyMapping(
        specialty="Obstetrics & Gynecology",
        category="Women's Health",
        keywords=[
            "period", "menstrual", "menstruation", "cramps", "vaginal", "pelvic pain",
            "ovary", "ovarian", "pcos", "pregnancy", "pregnant", "missed period", "uterine"
        ],
        description="Specializes in female reproductive health, pregnancy, and gynecological care."
    ),
    SpecialtyMapping(
        specialty="Urology",
        category="Urinary & Men's Health",
        keywords=[
            "urination", "urine", "burning urination", "uti", "frequent urination",
            "kidney stone", "bladder", "prostate", "flank pain"
        ],
        description="Specializes in the urinary system, bladder, kidneys, and male reproductive organs."
    ),
    SpecialtyMapping(
        specialty="Pediatrics",
        category="Child Health",
        keywords=[
            "baby", "infant", "toddler", "child", "pediatric", "newborn", "kid"
        ],
        description="Specializes in medical care for infants, children, and adolescents."
    )
]


class SpecialtyRecommender:
    """Evaluates text complaints and recommends appropriate medical specialty."""

    @staticmethod
    def recommend(
        symptoms_text: str,
        triage_level: TriageLevel = TriageLevel.ROUTINE,
        age_group: str = ""
    ) -> Dict:
        """
        Determine appropriate medical specialty based on triage urgency,
        age demographics, and symptom text.
        """
        # Emergency override: if an acute emergency is detected, direct to Emergency Department
        if triage_level == TriageLevel.EMERGENCY:
            return {
                "specialty": "Emergency Medicine / Trauma Center",
                "category": "Immediate Emergency Care",
                "confidence": 1.0,
                "reasoning": (
                    "Emergency warning signs detected. Immediate clinical assessment at an "
                    "Emergency Department or Trauma Center is required."
                ),
                "is_emergency_override": True
            }

        # Age group contextual check: Pediatrics
        is_child = any(age in age_group.lower() for age in ["infant", "child", "pediatric", "under 12"])
        if is_child:
            return {
                "specialty": "Pediatrics",
                "category": "Child Health",
                "confidence": 0.9,
                "reasoning": "Patient is in the pediatric age bracket; consultation with a pediatrician is recommended.",
                "is_emergency_override": False
            }

        # Match against catalog
        scores: List[Tuple[SpecialtyMapping, float]] = []
        for mapping in SPECIALTY_CATALOG:
            score = mapping.score(symptoms_text)
            if score > 0:
                scores.append((mapping, score))

        if not scores:
            # Safe default fallback: General Physician
            return {
                "specialty": "General Physician / Internal Medicine",
                "category": "Primary Care",
                "confidence": 0.75,
                "reasoning": (
                    "Based on the reported general or systemic symptoms, a consultation with a "
                    "General Physician (Primary Care) is the most appropriate starting point for "
                    "comprehensive evaluation and further referral if needed."
                ),
                "is_emergency_override": False
            }

        # Sort by match score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        best_match, best_score = scores[0]

        # Calculate normalized confidence
        confidence = min(0.95, 0.65 + (best_score * 0.1))

        return {
            "specialty": best_match.specialty,
            "category": best_match.category,
            "confidence": round(confidence, 2),
            "reasoning": (
                f"Your reported symptoms match common presentations managed by {best_match.specialty}. "
                f"{best_match.description}"
            ),
            "is_emergency_override": False
        }


specialty_recommender = SpecialtyRecommender()

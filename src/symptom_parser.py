"""
Symptom Parsing and Entity Extraction Module for MediGuide AI.
Extracts reported symptoms, temporal duration, severity hints,
and missing clinical details from unstructured user text.
"""

import re
from typing import Dict, List, Set, Tuple


# Common anatomical and symptom keywords for heuristic extraction
BODY_AREAS = {
    "head": ["head", "forehead", "temple", "scalp"],
    "chest": ["chest", "ribs", "breastbone", "sternum"],
    "abdomen": ["stomach", "abdomen", "belly", "gut", "tummy", "navel"],
    "throat": ["throat", "pharynx", "tonsil"],
    "eyes": ["eye", "eyes", "vision", "eyeball", "eyelid"],
    "ears": ["ear", "ears", "hearing", "eardrum"],
    "nose": ["nose", "nasal", "sinus", "nostril"],
    "skin": ["skin", "rash", "hives", "itch", "blister", "mole"],
    "joints": ["joint", "knee", "elbow", "wrist", "ankle", "shoulder", "hip"],
    "back": ["back", "spine", "lumbar", "lower back", "neck"],
    "teeth": ["tooth", "teeth", "gum", "gums", "jaw"]
}

COMMON_SYMPTOM_TERMS = [
    "fever", "headache", "cough", "fatigue", "tiredness", "nausea", "vomiting",
    "diarrhea", "chills", "dizziness", "shortness of breath", "sore throat",
    "runny nose", "congestion", "muscle aches", "body pain", "abdominal pain",
    "stomach ache", "constipation", "heartburn", "acid reflux", "palpitations",
    "swelling", "redness", "itching", "rash", "wheezing", "ear pain",
    "blurred vision", "insomnia", "anxiety", "depression", "loss of appetite"
]

DURATION_PATTERNS = [
    (r"\b(\d+|a|one|two|three|several)\s+(hour|hours|hr|hrs)\b", "Hours"),
    (r"\b(\d+|a|one|two|three|several)\s+(day|days)\b", "Days"),
    (r"\b(\d+|a|one|two|three|several)\s+(week|weeks)\b", "Weeks"),
    (r"\b(\d+|a|one|two|three|several)\s+(month|months)\b", "Months"),
    (r"\bsince yesterday\b", "Since yesterday (~24 hours)"),
    (r"\bsince this morning\b", "Since this morning (<12 hours)"),
    (r"\bjust started\b", "Acute onset (just started)")
]


class SymptomParser:
    """Parses natural language symptom text into structured health attributes."""

    @staticmethod
    def extract_duration(text: str) -> str:
        """Extract detected duration from free text."""
        for pattern, label in DURATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return "Not explicitly specified in text"

    @staticmethod
    def extract_symptoms(text: str) -> List[str]:
        """Extract identified symptom keywords from text."""
        normalized = text.lower()
        extracted: List[str] = []

        for symptom in COMMON_SYMPTOM_TERMS:
            # Match word boundary
            if re.search(rf"\b{re.escape(symptom)}\b", normalized):
                extracted.append(symptom.capitalize())

        # Check body area + pain/ache combinations (e.g. "back pain", "knee pain")
        for area, synonyms in BODY_AREAS.items():
            for syn in synonyms:
                pain_pattern = rf"\b{syn}\s+(pain|ache|discomfort|soreness|swelling)\b"
                match = re.search(pain_pattern, normalized)
                if match:
                    phrase = match.group(0).capitalize()
                    if phrase not in extracted:
                        extracted.append(phrase)

        # Fallback if nothing specific matched
        if not extracted:
            # Clean first clause of user input as general concern
            first_clause = re.split(r"[,.;!?]", text)[0].strip()
            if first_clause:
                extracted.append(first_clause)

        return extracted

    @staticmethod
    def extract_body_systems(text: str) -> List[str]:
        """Detect which anatomical systems are involved."""
        normalized = text.lower()
        involved_systems = set()

        for system, keywords in BODY_AREAS.items():
            for kw in keywords:
                if re.search(rf"\b{kw}\b", normalized):
                    involved_systems.add(system.capitalize())

        return sorted(list(involved_systems))

    @staticmethod
    def identify_missing_information(
        text: str,
        age_group: str = "",
        duration: str = "",
        severity: int = 3
    ) -> Tuple[List[str], List[str]]:
        """
        Identify missing clinical context and produce targeted follow-up questions.
        Returns: (missing_information_list, follow_up_questions_list)
        """
        normalized = text.lower()
        missing: List[str] = []
        follow_ups: List[str] = []

        # 1. Check Onset
        has_onset = any(w in normalized for w in ["sudden", "gradual", "started", "since", "yesterday", "days", "hours"])
        if not has_onset and not duration:
            missing.append("Onset and exact duration (how quickly did it begin?)")
            follow_ups.append("Did your symptoms start suddenly or develop gradually over several days?")

        # 2. Check Fever temperature
        if "fever" in normalized:
            if not re.search(r"\b(\d{2,3}(\.\d)?)\s*(f|c|degrees)?\b", normalized):
                missing.append("Exact body temperature reading (e.g., in °F or °C)")
                follow_ups.append("Have you measured your body temperature with a thermometer?")

        # 3. Check Severity / Functional Impact
        if severity == 3 and not any(w in normalized for w in ["mild", "moderate", "severe", "worst", "unbearable", "bearable"]):
            missing.append("Functional impact on daily activities (work, sleep, eating)")
            follow_ups.append("Are these symptoms interfering with your ability to sleep, eat, or perform normal daily tasks?")

        # 4. Check Prior Episodes / Chronic History
        if not any(w in normalized for w in ["before", "first time", "history", "diagnosed", "chronic", "recurrent"]):
            missing.append("Prior history of similar episodes")
            follow_ups.append("Have you ever experienced these exact symptoms before?")

        # 5. Check Medications already taken
        if not any(w in normalized for w in ["took", "medication", "medicine", "pill", "paracetamol", "ibuprofen", "aspirin"]):
            missing.append("Any medications or home remedies attempted so far")
            follow_ups.append("Have you taken any over-the-counter medicines or remedies for relief yet?")

        # Limit follow ups to 3 most relevant to avoid overwhelming user
        return missing[:4], follow_ups[:3]

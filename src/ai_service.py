"""
AI Service Module for MediGuide AI.
Provides an enterprise clinical inference adapter with RAG protocol grounding,
Pydantic validation, safe rate limiting, and professional non-vendor branding.
"""

import json
import logging
import time
from typing import Any, Dict, Optional, Tuple
import requests

from src.config import (
    DEFAULT_GROQ_MODEL,
    FALLBACK_GROQ_MODELS,
    DEFAULT_GEMINI_MODEL,
    FALLBACK_GEMINI_MODELS,
    ENGINE_ACTIVE_LABEL,
    ENGINE_FALLBACK_LABEL,
    LLM_TIMEOUT_SECONDS,
    get_groq_api_key,
    get_gemini_api_key,
    is_demo_mode,
)
from src.models import StructuredAssessment, TriageLevel, UserSymptomProfile
from src.rag_engine import clinical_rag_engine
from src.safety_engine import safety_engine
from src.specialty_recommender import specialty_recommender
from src.symptom_parser import SymptomParser

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are the MediGuide Clinical Intelligence Engine (v2.4), an advanced, cautious, and empathetic healthcare care navigation assistant.

Your core objectives:
1. Summarize user-reported symptoms clearly and objectively.
2. Identify missing clinical details that a physician would need.
3. Formulate 1-3 targeted, polite follow-up questions tailored to their age bracket and medical context.
4. Ground your advice in the retrieved clinical practice guidelines provided in the prompt.
5. List 2-4 general, cautious health possibilities (strictly framed as possibilities, NEVER as definitive diagnoses).
6. Suggest safe, evidence-based general comfort measures (hydration, rest, avoiding known irritants). NEVER recommend prescription drug dosages or stopping medications.
7. Recommend clear, actionable next steps (e.g. routine doctor visit, urgent care, emergency services).
8. Suggest the most appropriate medical specialty.
9. State critical warning signs (red flags) that require immediate emergency care.

Strict Clinical Governance:
- NEVER state "You have [Condition]". Always use phrases like "Symptoms like these may sometimes be associated with...".
- NEVER prescribe medication dosages or alter prescription regimens.
- If severe symptoms (severe chest pain, stroke signs, difficulty breathing, profuse bleeding) are described, prioritize emergency action.
- When generating responses, deliver content in the patient's requested language if specified.
- Output MUST be valid JSON strictly matching the requested schema.
"""


def _generate_rule_based_fallback(
    profile: UserSymptomProfile,
    safety_result,
    retrieved_protocols: list
) -> StructuredAssessment:
    """
    Intelligent, deterministic assessment generator when live neural engine is offline.
    Uses clinical heuristics, symptom parsing, RAG knowledge, and the safety engine.
    """
    extracted_symptoms = SymptomParser.extract_symptoms(profile.symptoms_text)
    missing_info, follow_ups = SymptomParser.identify_missing_information(
        profile.symptoms_text,
        profile.age_group,
        profile.duration,
        profile.severity
    )
    rec_specialty = specialty_recommender.recommend(
        profile.symptoms_text,
        safety_result.triage_level,
        profile.age_group
    )

    is_hindi = "hindi" in profile.language.lower()

    if is_hindi:
        possibilities = []
        text_lower = profile.symptoms_text.lower()
        if any(w in text_lower for w in ["fever", "chills", "बुखार"]):
            possibilities.append("तीव्र वायरल सिंड्रोम (Acute Viral Syndrome), मौसमी फ्लू, या सामान्य संक्रामक बुखार")
        if any(w in text_lower for w in ["cough", "sore throat", "खांसी", "गला"]):
            possibilities.append("ऊपरी श्वसन मार्ग में जलन, तीव्र ग्रसनीशोथ (Pharyngitis), या मौसमी एलर्जी")
        if any(w in text_lower for w in ["headache", "सिरदर्द"]):
            possibilities.append("तनाव जनित सिरदर्द (Tension Headache), निर्जलीकरण (Dehydration), या थकावट")
        if any(w in text_lower for w in ["stomach", "पेट"]):
            possibilities.append("गैस्ट्रिक जलन, एसिडिटी (GERD), या हल्का पेट का संक्रमण")
        if not possibilities:
            possibilities.append("सामान्य अस्वस्थता जिसके लिए डॉक्टर द्वारा परीक्षण आवश्यक है")

        guidance = [
            "पर्याप्त शारीरिक आराम करें और स्वच्छ पानी/ओआरएस का सेवन बनाए रखें।",
            "बुखार के समय और लक्षणों का एक संक्षिप्त दैनिक रिकॉर्ड रखें।",
            "लक्षण ठीक होने तक भारी शारीरिक परिश्रम से बचें।"
        ]
        if any(w in text_lower for w in ["fever", "बुखार"]):
            guidance.append("हवादार और आरामदायक कमरे में रहें एवं हल्के सूती कपड़े पहनें।")
        if any(w in text_lower for w in ["cough", "खांसी"]):
            guidance.append("गुनगुने पानी में नमक डालकर गरारे करने से गले की खराश और खांसी में आराम मिल सकता है।")

        warning_signs = [
            "सीने में अचानक तेज दर्द, दबाव या भारीपन जो बाएं हाथ या जबड़े तक फैले",
            "सांस लेने में अत्यधिक कठिनाई, हांफना या होंठ नीले पड़ना",
            "अचानक चेहरे का झुकना, हाथ में कमजोरी या बोलने में लड़खड़ाहट (स्ट्रोक लक्षण)",
            "अचानक बेहोशी, भ्रम या चेतना खोना",
            "लगातार तेज बुखार जो कम न हो या गर्दन में अकड़न के साथ हो"
        ]

        missing_info = ["लक्षणों का सही समय और तापमान (यदि थर्मामीटर से मापा गया हो)"]
        follow_ups = ["क्या बुखार के साथ कंपकंपी या पसीना आ रहा है?"]
        rec_step = f"नियमित मूल्यांकन: 1-2 दिनों के भीतर एक {rec_specialty['specialty']} से परामर्श लें।"
        disclaimer_text = "मेडीगाइड क्लिनिकल इंटेलिजेंस इंजन (सत्यापित प्रोटोकॉल मोड)। यह कोई चिकित्सीय निदान नहीं है।"
    else:
        # General possibilities based on symptoms (English)
        possibilities = []
        text_lower = profile.symptoms_text.lower()
        if "fever" in text_lower or "chills" in text_lower:
            possibilities.append("Acute viral syndrome, seasonal respiratory infection, or localized infectious focus")
        if "headache" in text_lower:
            possibilities.append("Tension-type cephalalgia, dehydration, eye strain, or vascular headache")
        if "cough" in text_lower or "sore throat" in text_lower:
            possibilities.append("Upper respiratory tract irritation, acute pharyngitis, or seasonal allergic reactivity")
        if "stomach" in text_lower or "nausea" in text_lower or "acid" in text_lower:
            possibilities.append("Gastric mucosal irritation, gastroesophageal reflux (GERD), or mild gastroenteritis")
        if "joint" in text_lower or "back" in text_lower:
            possibilities.append("Musculoskeletal strain, postural fatigue, or localized joint inflammation")
        if not possibilities:
            possibilities.append("Non-specific symptom cluster requiring clinical history and physical examination")

        # Safe general guidance
        guidance = [
            "Prioritize physical rest and maintain comfortable hydration with clean fluids.",
            "Keep a concise log of symptom progression, recording temperatures and times of onset.",
            "Avoid strenuous physical exertion until your symptoms resolve."
        ]
        if "fever" in text_lower:
            guidance.append("Remain in a well-ventilated, temperate environment and wear breathable clothing.")
        if "cough" in text_lower or "sore throat" in text_lower:
            guidance.append("Warm fluid intake and saline water gargles can soothe pharyngeal discomfort.")

        # Warning signs
        warning_signs = [
            "Sudden, crushing chest pain or tightness radiating to arm, neck, or jaw",
            "Severe shortness of breath, gasping for air, or blue-tinted lips",
            "Sudden facial drooping, arm weakness, or slurred speech (FAST signs)",
            "Sudden loss of consciousness, confusion, or unresponsiveness",
            "Persistent high fever unresponsive to comfort measures or accompanied by stiff neck"
        ]
        rec_step = safety_result.recommended_action
        disclaimer_text = (
            "MediGuide Clinical Intelligence Engine (Standard Clinical Protocol Mode). "
            "Generated for health education and care navigation. Not a medical diagnosis. "
            "Always consult a licensed medical professional for clinical diagnosis and treatment."
        )

    if safety_result.emergency_instructions:
        warning_signs = safety_result.emergency_instructions + warning_signs

    return StructuredAssessment(
        symptom_summary=extracted_symptoms,
        missing_information=missing_info,
        follow_up_questions=follow_ups,
        possible_explanations=possibilities,
        general_guidance=guidance,
        recommended_next_step=rec_step,
        suggested_specialty=rec_specialty["specialty"],
        warning_signs=warning_signs[:5],
        triage_level=safety_result.triage_level,
        requires_urgent_evaluation=safety_result.is_urgent,
        retrieved_protocols=retrieved_protocols,
        disclaimer=disclaimer_text
    )


class AIService:
    """Service wrapper for enterprise clinical AI inference with multi-provider failover (Groq -> Gemini -> Local)."""

    def __init__(self):
        self.api_key = get_groq_api_key()
        self.gemini_key = get_gemini_api_key()
        self._client = None
        if self.api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key, timeout=LLM_TIMEOUT_SECONDS)
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}")
                self._client = None

    def _call_gemini(self, user_prompt: str) -> Optional[dict]:
        """Secondary fallback neural engine using Google Gemini REST API."""
        api_key = get_gemini_api_key() or self.gemini_key
        if not api_key:
            return None

        candidates = [DEFAULT_GEMINI_MODEL] + [m for m in FALLBACK_GEMINI_MODELS if m != DEFAULT_GEMINI_MODEL]
        for model in candidates:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": user_prompt}]}],
                    "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "temperature": 0.2
                    }
                }
                res = requests.post(url, json=payload, timeout=LLM_TIMEOUT_SECONDS)
                if res.status_code == 200:
                    data = res.json()
                    candidates_list = data.get("candidates", [])
                    if candidates_list:
                        text_part = candidates_list[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if text_part:
                            return json.loads(text_part)
                else:
                    logger.warning(f"Gemini {model} returned HTTP {res.status_code}: {res.text[:120]}")
            except Exception as e:
                logger.warning(f"Gemini model {model} attempt failed: {e}")
                continue
        return None

    def check_connection(self) -> Dict[str, Any]:
        """
        Diagnostic ping to verify whether the AI core is active and operational.
        Checks Groq first; if Groq is unavailable, checks Google Gemini.
        Returns latency and health status without exposing vendor credentials.
        """
        # 1. Try Groq (Primary Fast Engine)
        if self._client and not is_demo_mode():
            start = time.time()
            for candidate in [DEFAULT_GROQ_MODEL] + [m for m in FALLBACK_GROQ_MODELS if m != DEFAULT_GROQ_MODEL]:
                try:
                    res = self._client.chat.completions.create(
                        model=candidate,
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=3
                    )
                    elapsed = round((time.time() - start) * 1000, 1)
                    backup_tag = " (+ Gemini Standby Armed)" if get_gemini_api_key() else ""
                    return {
                        "is_active": True,
                        "status": f"Operational & Verified (200 OK){backup_tag}",
                        "latency_ms": elapsed,
                        "engine_label": ENGINE_ACTIVE_LABEL
                    }
                except Exception:
                    continue

        # 2. Try Gemini (Secondary Hot Standby)
        gemini_key = get_gemini_api_key()
        if gemini_key:
            start = time.time()
            for model in [DEFAULT_GEMINI_MODEL] + FALLBACK_GEMINI_MODELS:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                    payload = {
                        "contents": [{"parts": [{"text": "ping"}]}],
                        "generationConfig": {"maxOutputTokens": 3}
                    }
                    res = requests.post(url, json=payload, timeout=6)
                    if res.status_code == 200:
                        elapsed = round((time.time() - start) * 1000, 1)
                        return {
                            "is_active": True,
                            "status": f"Operational (Backup: Gemini Active, {elapsed} ms)",
                            "latency_ms": elapsed,
                            "engine_label": f"{ENGINE_ACTIVE_LABEL} (Backup: Gemini)"
                        }
                except Exception:
                    continue

        return {
            "is_active": False,
            "status": "Safe Local Mode (Deterministic Core Active)",
            "latency_ms": 1,
            "engine_label": ENGINE_FALLBACK_LABEL
        }

    def assess_symptoms(
        self,
        profile: UserSymptomProfile
    ) -> Tuple[StructuredAssessment, str]:
        """
        Conduct a comprehensive structured health assessment grounded via RAG.
        Executes multi-provider neural cascade: Groq -> Gemini -> Local Deterministic Core.
        Returns: (StructuredAssessment, engine_label)
        """
        # STEP 1: Run Independent Safety Engine FIRST
        safety_result = safety_engine.evaluate(profile)

        # STEP 2: Clinical RAG Protocol Retrieval
        retrieved_docs = clinical_rag_engine.retrieve(profile.symptoms_text, top_k=2)
        rag_context = clinical_rag_engine.format_context_for_prompt(retrieved_docs)

        # STEP 3: Check if any neural engine credentials exist
        if is_demo_mode():
            assessment = _generate_rule_based_fallback(profile, safety_result, retrieved_docs)
            return assessment, ENGINE_FALLBACK_LABEL

        # STEP 4: Build Grounded Neural Prompt with strict language directive
        user_prompt = f"""
CRITICAL MULTILINGUAL INSTRUCTION:
The user's requested report language is: **{profile.language}**.
You MUST write all output strings (symptom_summary, missing_information, follow_up_questions, possible_explanations, general_guidance, recommended_next_step, warning_signs, disclaimer) in {profile.language}.
If Hindi is requested, write in fluent, natural Devanagari Hindi (हिन्दी)!

Patient Clinical Profile:
- Primary Complaint: {profile.symptoms_text}
- Exact Age: {profile.exact_age} years ({profile.age_group})
- Symptom Duration: {profile.duration}
- Pain/Severity Scale: {profile.severity}/10
- Pregnancy Status: {'Yes, ' + (profile.trimester or 'Active') if profile.is_pregnant else 'No / Not Applicable'}
- Chronic Medical Conditions: {profile.medical_history or "None reported"}
- Current Medications: {profile.current_medications or "None reported"}
- Patient Country: {profile.country}

Pre-Evaluated Safety Urgency: {safety_result.triage_level.value}

Grounding Clinical Protocols (RAG):
{rag_context}

Please generate the structured healthcare assessment according to the following JSON schema:
{{
  "symptom_summary": ["string in {profile.language}"],
  "missing_information": ["string in {profile.language}"],
  "follow_up_questions": ["string in {profile.language}"],
  "possible_explanations": ["string in {profile.language}"],
  "general_guidance": ["string in {profile.language}"],
  "recommended_next_step": "string in {profile.language}",
  "suggested_specialty": "{safety_result.triage_level.value if safety_result.is_emergency else 'General Physician / Internal Medicine'}",
  "warning_signs": ["string in {profile.language}"],
  "triage_level": "{safety_result.triage_level.value}",
  "requires_urgent_evaluation": {str(safety_result.is_urgent).lower()},
  "disclaimer": "string in {profile.language}"
}}
"""

        # Provider 1: Groq (Primary Ultra-Fast Inference)
        if self._client:
            for candidate_model in [DEFAULT_GROQ_MODEL] + [m for m in FALLBACK_GROQ_MODELS if m != DEFAULT_GROQ_MODEL]:
                try:
                    response = self._client.chat.completions.create(
                        model=candidate_model,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.2,
                        response_format={"type": "json_object"}
                    )

                    raw_content = response.choices[0].message.content
                    parsed_data = json.loads(raw_content)

                    # Safety Override: Deterministic rule engine always overrides LLM if critical
                    if safety_result.is_emergency:
                        parsed_data["triage_level"] = TriageLevel.EMERGENCY.value
                        parsed_data["requires_urgent_evaluation"] = True
                        parsed_data["recommended_next_step"] = safety_result.recommended_action
                        parsed_data["warning_signs"] = list(set(parsed_data.get("warning_signs", []) + safety_result.emergency_instructions))
                    elif safety_result.is_urgent and parsed_data.get("triage_level") not in (TriageLevel.EMERGENCY.value, TriageLevel.URGENT.value):
                        parsed_data["triage_level"] = TriageLevel.URGENT.value
                        parsed_data["requires_urgent_evaluation"] = True
                        parsed_data["recommended_next_step"] = safety_result.recommended_action

                    parsed_data["retrieved_protocols"] = retrieved_docs
                    assessment = StructuredAssessment(**parsed_data)
                    return assessment, ENGINE_ACTIVE_LABEL

                except Exception as e:
                    logger.warning(f"Groq model {candidate_model} failed: {e}. Trying next available provider/model...")
                    continue

        # Provider 2: Google Gemini (Secondary Hot Standby Failover)
        if get_gemini_api_key():
            logger.info("Attempting secondary neural fallback via Google Gemini API...")
            gemini_data = self._call_gemini(user_prompt)
            if gemini_data:
                try:
                    if safety_result.is_emergency:
                        gemini_data["triage_level"] = TriageLevel.EMERGENCY.value
                        gemini_data["requires_urgent_evaluation"] = True
                        gemini_data["recommended_next_step"] = safety_result.recommended_action
                        gemini_data["warning_signs"] = list(set(gemini_data.get("warning_signs", []) + safety_result.emergency_instructions))
                    elif safety_result.is_urgent and gemini_data.get("triage_level") not in (TriageLevel.EMERGENCY.value, TriageLevel.URGENT.value):
                        gemini_data["triage_level"] = TriageLevel.URGENT.value
                        gemini_data["requires_urgent_evaluation"] = True
                        gemini_data["recommended_next_step"] = safety_result.recommended_action

                    gemini_data["retrieved_protocols"] = retrieved_docs
                    assessment = StructuredAssessment(**gemini_data)
                    return assessment, f"{ENGINE_ACTIVE_LABEL} (Gemini Backup)"
                except Exception as val_err:
                    logger.warning(f"Gemini response validation failed: {val_err}")

        # Provider 3: Local Deterministic Core (Safe Mode)
        logger.error("All neural providers (Groq & Gemini) unavailable. Engaging deterministic safety core.")
        assessment = _generate_rule_based_fallback(profile, safety_result, retrieved_docs)
        return assessment, ENGINE_FALLBACK_LABEL


ai_service = AIService()

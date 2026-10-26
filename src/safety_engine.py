"""
Independent Safety Engine for MediGuide AI.
Evaluates user-described symptoms for safety-critical "Red Flag" warning signs
BEFORE or independently of LLM guidance generation.

Includes age-specific pediatric (neonate/infant) and geriatric (65+) safety checks,
obstetric complication rules, and localized emergency hotlines.
"""

import re
from typing import Dict, List, Optional
from src.models import TriageLevel, UserSymptomProfile
from src.config import get_active_country


class SafetyRule:
    """Represents a rule-based safety check with medical reasoning."""
    def __init__(
        self,
        rule_id: str,
        name: str,
        category: str,
        severity: TriageLevel,
        patterns: List[str],
        reasoning: str,
        emergency_instructions: List[str]
    ):
        self.rule_id = rule_id
        self.name = name
        self.category = category
        self.severity = severity
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.reasoning = reasoning
        self.emergency_instructions = emergency_instructions

    def matches(self, text: str) -> bool:
        """Check if any compiled pattern matches the normalized text."""
        return any(pattern.search(text) for pattern in self.patterns)


SAFETY_RULES: List[SafetyRule] = [
    # 1. Cardiovascular / Chest Pain
    SafetyRule(
        rule_id="CRIT-001",
        name="Acute Coronary Syndrome / Chest Pain",
        category="Cardiovascular",
        severity=TriageLevel.EMERGENCY,
        patterns=[
            r"\bchest (pain|pressure|tightness|heaviness|crushing|squeezing)\b",
            r"\bpain (radiating|spreading) to (the )?(left arm|jaw|neck|back)\b",
            r"\bheart attack\b",
            r"\bcrushing sensation in (my|the)? chest\b",
            r"\bangina\b"
        ],
        reasoning="Chest pain, pressure, or radiation to arm/jaw suggests acute coronary syndrome or myocardial infarction.",
        emergency_instructions=[
            "Call your local emergency number immediately (112 in India, 911 in US, 999 in UK). Do not drive yourself.",
            "Rest in a comfortable seated position with shoulders supported.",
            "Loosen tight clothing around neck and chest.",
            "If prescribed emergency nitroglycerin by your cardiologist, use as directed."
        ]
    ),

    # 2. Cerebrovascular / Stroke (FAST)
    SafetyRule(
        rule_id="CRIT-002",
        name="Suspected Stroke / Cerebrovascular Event (FAST)",
        category="Neurological",
        severity=TriageLevel.EMERGENCY,
        patterns=[
            r"\b(facial|face) (droop|drooping|numbness|paralysis)\b",
            r"\b(arm|leg) (weakness|numbness|paralysis|giving out)\b",
            r"\b(slurred|slurring|difficulty) speech\b",
            r"\bunable to speak\b",
            r"\bsudden (confusion|trouble speaking|loss of balance|vision loss)\b",
            r"\bhalf of (my|the)? body (is numb|went numb|feels weak)\b",
            r"\b(stroke|mini-stroke|tia)\b"
        ],
        reasoning="Acute focal neurological deficits (FAST criteria) strongly indicate stroke; reperfusion therapy is time-critical.",
        emergency_instructions=[
            "Call emergency services immediately. Note the exact time symptoms started.",
            "Keep the patient lying flat or in recovery position if nauseated.",
            "Do NOT give any food, liquids, or oral medications (choking and aspiration hazard)."
        ]
    ),

    # 3. Severe Respiratory Distress
    SafetyRule(
        rule_id="CRIT-003",
        name="Severe Respiratory Distress / Airway Compromise",
        category="Respiratory",
        severity=TriageLevel.EMERGENCY,
        patterns=[
            r"\b(severe|can't|cannot|unable to) breath(e|ing)\b",
            r"\bgasping for (air|breath)\b",
            r"\b(blue|bluish) (lips|fingertips|skin)\b",
            r"\bchoking\b",
            r"\bstridor\b",
            r"\bsuffocating\b",
            r"\bheavy wheezing and can't speak\b"
        ],
        reasoning="Cyanosis, stridor, or gasping indicates life-threatening respiratory compromise or hypoxia.",
        emergency_instructions=[
            "Call emergency medical services immediately.",
            "Sit upright to ease the work of breathing; do not lie flat.",
            "Assist the patient in administering prescribed rescue bronchodilators if indicated."
        ]
    ),

    # 4. Severe Allergic Reaction (Anaphylaxis)
    SafetyRule(
        rule_id="CRIT-004",
        name="Anaphylaxis / Severe Allergic Reaction",
        category="Immunological",
        severity=TriageLevel.EMERGENCY,
        patterns=[
            r"\b(throat|tongue|airway)(\s+\w+){0,4}\s+(swelling|swollen|closing up|swelled)\b",
            r"\b(swelling|swollen)(\s+\w+){0,4}\s+(throat|tongue|airway)\b",
            r"\b(cannot|unable to|trouble|difficulty)\s+swallow(ing)?(\s+\w+){0,4}\s*(after eating|allergy|nuts|seafood|sting)?\b",
            r"\banaphylax(is|ic)\b",
            r"\bhives(\s+\w+){0,4}\s+(trouble breathing|shortness of breath|swelling)\b"
        ],
        reasoning="Anaphylaxis is a rapidly fatal systemic hypersensitivity reaction causing airway edema and vascular shock.",
        emergency_instructions=[
            "Administer intramuscular epinephrine (EpiPen) into the outer mid-thigh immediately if available.",
            "Call emergency medical dispatch right after epinephrine injection.",
            "Keep patient recumbent with legs elevated unless breathing is compromised."
        ]
    ),

    # 5. Loss of Consciousness / Unresponsive / Seizure
    SafetyRule(
        rule_id="CRIT-005",
        name="Altered Consciousness / Syncope / Seizure",
        category="Neurological",
        severity=TriageLevel.EMERGENCY,
        patterns=[
            r"\b(passed out|fainted|unconscious|unresponsive|blacked out)\b",
            r"\bactive seizure\b",
            r"\bconvulsing\b",
            r"\blost consciousness\b",
            r"\bunable to wake (him|her|them|up)\b"
        ],
        reasoning="Unresponsiveness, active seizure, or prolonged syncope requires acute neurological and cardiac stabilization.",
        emergency_instructions=[
            "Call emergency services immediately.",
            "Check airway, breathing, and pulse. Roll patient into recovery position if breathing.",
            "Do NOT insert objects or fingers into the patient's mouth during convulsion."
        ]
    ),

    # 6. Severe Hemorrhage
    SafetyRule(
        rule_id="CRIT-006",
        name="Severe Hemorrhage / Acute Bleeding",
        category="Hematological / Trauma",
        severity=TriageLevel.EMERGENCY,
        patterns=[
            r"\b(uncontrolled|heavy|spurting|gushing) bleeding\b",
            r"\b(coughing|coughed) up (large amounts of )?blood\b",
            r"\b(vomiting|vomited) blood\b",
            r"\b(bleeding|blood) won't stop\b",
            r"\bblack tarry stools with dizziness\b"
        ],
        reasoning="Massive external or gastrointestinal hemorrhage causes hypovolemic shock and requires emergency hemostasis.",
        emergency_instructions=[
            "Call emergency dispatch immediately.",
            "Apply direct, sustained pressure to the bleeding site with a clean cloth or sterile dressing.",
            "Keep the patient lying down and warm to counteract hypothermia and shock."
        ]
    ),

    # 7. Meningeal Signs / Sepsis
    SafetyRule(
        rule_id="CRIT-007",
        name="Suspected Meningitis / Sepsis",
        category="Infectious Disease",
        severity=TriageLevel.EMERGENCY,
        patterns=[
            r"\b(stiff neck|neck stiffness) (and|with) (high fever|fever)\b",
            r"\bfever (with|and) (purple rash|non-blanching rash|petechiae)\b",
            r"\bextreme light sensitivity (with|and) severe headache and fever\b",
            r"\bhigh fever with confusion and neck pain\b"
        ],
        reasoning="Triad of fever, nuchal rigidity, and photophobia/petechial rash strongly suggests acute bacterial meningitis.",
        emergency_instructions=[
            "Proceed to the nearest emergency hospital immediately.",
            "Check petechial rash with glass tumbler; non-fading spots require instant intervention."
        ]
    ),

    # 8. Severe Abdominal Crisis
    SafetyRule(
        rule_id="CRIT-008",
        name="Acute Severe Abdomen",
        category="Gastrointestinal / Surgical",
        severity=TriageLevel.URGENT,
        patterns=[
            r"\b(worst abdominal pain|severe stomach pain|sudden excruciating belly pain)\b",
            r"\b(rigid|hard as a board) abdomen\b",
            r"\bsevere right lower (quadrant|belly|side) pain with fever\b"
        ],
        reasoning="Severe localized abdominal pain with guarding or rigidity indicates peritonitis, appendicitis, or bowel perforation.",
        emergency_instructions=[
            "Seek urgent clinical or emergency evaluation within hours.",
            "Do NOT consume food or drinks (NPO) in anticipation of possible surgical intervention."
        ]
    ),

    # 9. Pediatric / Neonatal Fever Alert
    SafetyRule(
        rule_id="CRIT-009",
        name="Neonatal / Infant Fever Alert",
        category="Pediatrics",
        severity=TriageLevel.EMERGENCY,
        patterns=[
            r"\b(baby|infant|newborn)(\s+\w+){0,4}\s+(under|less than)\s*3\s*months(\s+\w+){0,4}\s*fever\b",
            r"\bfever\s+(in|of)(\s+\w+){0,3}\s+(newborn|baby|infant)\b",
            r"\b(\d{1,2}|one|two|three)\s*month(s)?\s*old(\s+\w+){0,3}\s*(has|with|having)?\s*fever\b",
            r"\b(newborn|infant|baby)(\s+\w+){0,3}\s*fever\s*of\s*\d{2,3}\b"
        ],
        reasoning="Infants under 3 months with fever require urgent pediatric sepsis evaluation due to immature immunity.",
        emergency_instructions=[
            "Visit a pediatric emergency department or contact a pediatrician immediately.",
            "Do NOT administer antipyretic medications without direct physician instructions."
        ]
    ),

    # 10. Geriatric Acute Confusion / Delirium
    SafetyRule(
        rule_id="CRIT-010",
        name="Geriatric Acute Confusion / Delirium Alert",
        category="Geriatrics",
        severity=TriageLevel.URGENT,
        patterns=[
            r"\b(elderly|senior|grandmother|grandfather|grandma|grandpa)(\s+\w+){0,3}\s*(sudden|suddenly)?\s*(confused|delirious|disoriented|acting strange)\b",
            r"\bsudden confusion in (elderly|senior|older adult)\b",
            r"\bfall in elderly with hip pain\b"
        ],
        reasoning="Acute delirium in older adults frequently signals occult infection (such as UTI or pneumonia), stroke, or metabolic crisis.",
        emergency_instructions=[
            "Seek prompt medical evaluation at an urgent care clinic or hospital.",
            "Check for signs of hip fracture, head trauma, and dehydration."
        ]
    ),

    # 11. Obstetric Warning Signs
    SafetyRule(
        rule_id="CRIT-011",
        name="Maternal & Obstetric Complication Warning",
        category="Obstetrics",
        severity=TriageLevel.URGENT,
        patterns=[
            r"\bpregnant (and|with) (vaginal bleeding|bleeding)\b",
            r"\bpregnant (and|with) (severe abdominal cramping|severe pain)\b",
            r"\bpregnant (and|with) (sudden vision changes|severe headache and swelling)\b"
        ],
        reasoning="Vaginal bleeding or persistent severe headache in pregnancy suggests placental abruption or pre-eclampsia.",
        emergency_instructions=[
            "Contact your obstetrician or present to the nearest maternity emergency center.",
            "Lie on your left lateral side to preserve optimal placental perfusion."
        ]
    )
]


class SafetyEngineResult:
    """Outcome of safety engine evaluation."""
    def __init__(
        self,
        triage_level: TriageLevel,
        is_emergency: bool,
        is_urgent: bool,
        matched_rules: List[str],
        reasoning: List[str],
        emergency_instructions: List[str],
        recommended_action: str
    ):
        self.triage_level = triage_level
        self.is_emergency = is_emergency
        self.is_urgent = is_urgent
        self.matched_rules = matched_rules
        self.reasoning = reasoning
        self.emergency_instructions = emergency_instructions
        self.recommended_action = recommended_action


class SafetyEngine:
    """Deterministic rule-based clinical safety evaluation engine."""

    def __init__(self, rules: Optional[List[SafetyRule]] = None):
        self.rules = rules or SAFETY_RULES

    def evaluate(
        self,
        profile: UserSymptomProfile or str,
        age_group: str = "",
        severity: int = 3,
        is_pregnant: bool = False,
        exact_age: int = 30
    ) -> SafetyEngineResult:
        """
        Evaluate symptoms and patient context against conservative safety rules.
        Accepts UserSymptomProfile or raw text with optional context kwargs.
        """
        if isinstance(profile, str):
            text = profile.strip().lower()
            age = exact_age
            sev = severity
            pregnant = is_pregnant
        else:
            text = profile.symptoms_text.strip().lower()
            age = profile.exact_age
            sev = profile.severity
            pregnant = profile.is_pregnant

        matched_rules: List[str] = []
        reasoning: List[str] = []
        instructions: List[str] = []

        highest_severity = TriageLevel.ROUTINE

        # Check explicit rules
        for rule in self.rules:
            if rule.matches(text):
                matched_rules.append(f"{rule.name} [{rule.rule_id}]")
                reasoning.append(rule.reasoning)
                instructions.extend(rule.emergency_instructions)

                if rule.severity == TriageLevel.EMERGENCY:
                    highest_severity = TriageLevel.EMERGENCY
                elif rule.severity == TriageLevel.URGENT and highest_severity != TriageLevel.EMERGENCY:
                    highest_severity = TriageLevel.URGENT

        # Contextual Check 1: Neonatal fever (<28 days or <3 months)
        if age <= 0 and ("fever" in text or "warm" in text or "hot" in text):
            matched_rules.append("Neonatal Fever Emergency (<28 Days) [CRIT-NEO]")
            reasoning.append("Any fever in a neonate is considered a medical emergency requiring hospital workup.")
            instructions.append("Proceed to a pediatric emergency hospital immediately.")
            highest_severity = TriageLevel.EMERGENCY

        # Contextual Check 2: Pregnancy with symptoms of bleeding or abdominal pain
        if pregnant:
            if any(w in text for w in ["bleed", "blood", "spotting", "cramp", "abdominal pain", "severe headache"]):
                matched_rules.append("Obstetric High-Risk Red Flag [CRIT-OB]")
                reasoning.append("Pregnancy with acute pain, bleeding, or visual changes warrants urgent obstetric evaluation.")
                instructions.append("Contact your obstetrician or visit maternity triage immediately.")
                if highest_severity != TriageLevel.EMERGENCY:
                    highest_severity = TriageLevel.URGENT

        # Contextual Check 3: Geriatric (65+) acute chest pain or confusion
        if age >= 65:
            if any(w in text for w in ["dizziness", "confusion", "fell", "fall", "breathless", "tired"]):
                if highest_severity == TriageLevel.ROUTINE:
                    matched_rules.append("Geriatric Acute Presentation Alert (65+) [CRIT-GERI]")
                    reasoning.append("Atypical disease presentation is common in older adults; prompt evaluation is advised.")
                    instructions.append("Schedule an urgent or prompt consultation to assess vital signs and hydration.")
                    highest_severity = TriageLevel.URGENT

        # High Pain Severity Alert (9+/10)
        if sev >= 9 and highest_severity not in (TriageLevel.EMERGENCY, TriageLevel.URGENT):
            matched_rules.append("High Pain Severity Alert (9+/10)")
            reasoning.append("Severe unmanaged pain (scale 9-10) warrants prompt clinical medical evaluation.")
            highest_severity = TriageLevel.URGENT
            instructions.append("Visit an urgent care center or consult an on-call physician for pain evaluation.")

        # Localized Emergency Hotline retrieval
        country_cfg = get_active_country()
        em_num = country_cfg.get("emergency_number", "112")
        amb_num = country_cfg.get("ambulance", "112")

        unique_instructions = list(dict.fromkeys(instructions))

        if highest_severity == TriageLevel.EMERGENCY:
            action = (
                f"EMERGENCY ACTION REQUIRED: Please call {em_num} / {amb_num} "
                f"or go to the nearest emergency department immediately. Do not delay for a routine appointment."
            )
        elif highest_severity == TriageLevel.URGENT:
            action = (
                "PROMPT EVALUATION RECOMMENDED: Please consult a physician or visit an urgent care "
                "center within 12 to 24 hours. If symptoms acutely worsen, seek emergency care immediately."
            )
        elif sev <= 2:
            highest_severity = TriageLevel.SELF_CARE
            action = "ROUTINE / SELF-CARE: Monitored self-care and rest may be appropriate. Consult a doctor if symptoms persist."
        else:
            highest_severity = TriageLevel.ROUTINE
            action = "NON-URGENT EVALUATION: Schedule a standard clinical consultation with a doctor or specialist."

        return SafetyEngineResult(
            triage_level=highest_severity,
            is_emergency=(highest_severity == TriageLevel.EMERGENCY),
            is_urgent=(highest_severity in (TriageLevel.EMERGENCY, TriageLevel.URGENT)),
            matched_rules=matched_rules,
            reasoning=reasoning,
            emergency_instructions=unique_instructions,
            recommended_action=action
        )


safety_engine = SafetyEngine()

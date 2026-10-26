# MediGuide AI Synthetic Dataset Documentation

## 1. Dataset Overview
This dataset contains synthetic, clinically modeled patient symptom narratives designed for training and evaluating healthcare navigation, triage classification, and medical specialty routing models.

**IMPORTANT NOTICE**: This dataset consists entirely of synthetic clinical vignettes. It contains NO Protected Health Information (PHI) or real patient records. It is intended for educational, portfolio, and research demonstration of NLP care navigation workflows.

## 2. Intended Task
- **Input**: Free-text natural language symptom description from a patient.
- **Targets**:
  1. `triage_level`: Urgency classification (`EMERGENCY`, `URGENT`, `ROUTINE`, `SELF_CARE`).
  2. `specialty_category`: Appropriate clinical specialty for care navigation (e.g., `Dermatology`, `Orthopedics`, `Cardiology`, `General Physician`).

## 3. Class Definitions & Distribution
- **EMERGENCY**: Acute conditions requiring immediate life-saving medical attention (e.g., suspected myocardial infarction, acute stroke, severe respiratory compromise, massive hemorrhage).
- **URGENT**: Acute or worsening conditions needing professional evaluation within 12-24 hours (e.g., acute severe abdominal pain, persistent high fever, deep lacerations).
- **ROUTINE**: Subacute, persistent, or recurring symptoms suitable for standard outpatient consultation (e.g., joint aches, skin rashes, chronic headaches, recurrent heartburn).
- **SELF_CARE**: Mild, self-limiting symptoms appropriate for home rest and hydration with clinical monitoring (e.g., mild transient tension headache, minor localized scratch, mild seasonal sniffling).

## 4. Ethical & Clinical Limitations
- Not validated for real-world bedside diagnosis or clinical triage.
- Language is currently restricted to English clinical narratives.
- Must always be paired with deterministic rule-based safety nets before any clinical recommendation.

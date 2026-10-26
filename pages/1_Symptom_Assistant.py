"""
MediGuide AI — Symptom Assistant & Clinical Care Intake Page.
Interactive clinical intake with Patient Name & Patient ID registration,
exact age & demographic stratification, RAG protocol grounding, and multilingual reports.
"""

import sys
import importlib
from datetime import datetime
import streamlit as st

for _mod in list(sys.modules.keys()):
    if _mod.startswith("src.") or _mod == "src":
        try:
            importlib.reload(sys.modules[_mod])
        except Exception:
            pass

st.set_page_config(
    page_title="Symptom Assistant & Triage — MediGuide AI",
    page_icon="🩺",
    layout="wide"
)

from src.ui_components import apply_theme, render_sidebar, render_triage_badge
from src.models import UserSymptomProfile, PatientSession, TriageLevel, classify_demographic, generate_patient_id
from src.ai_service import ai_service
from src.config import get_active_country
from src.database import save_session, get_all_patient_ids
from src.report_generator import generate_pdf_report, generate_html_clinical_summary

apply_theme()
render_sidebar()

country_cfg = get_active_country()

st.title("🩺 Intelligent Clinical Symptom Assistant")
st.markdown(
    f"Complete clinical evaluation and triage configured for **{country_cfg.get('name')}**. "
    f"Enter your details to generate your structured clinical summary and consultation record."
)

# Initialize session states
if "symptom_text" not in st.session_state:
    st.session_state.symptom_text = ""
if "current_assessment" not in st.session_state:
    st.session_state.current_assessment = None
if "assessment_source" not in st.session_state:
    st.session_state.assessment_source = ""
if "last_profile" not in st.session_state:
    st.session_state.last_profile = None
if "active_patient_id" not in st.session_state:
    st.session_state.active_patient_id = generate_patient_id()
if "active_patient_name" not in st.session_state:
    st.session_state.active_patient_name = ""

# Quick-Fill Clinical Presets
st.markdown("##### 💡 Example Clinical Scenarios (1-Click Fill):")
exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)

with exp_col1:
    if st.button("🌡️ Acute Fever & Headache", use_container_width=True):
        st.session_state.symptom_text = "I have had a high fever of around 101.5, severe throbbing headache, and fatigue for the last 2 days."
        if not st.session_state.active_patient_name:
            st.session_state.active_patient_name = "Priya Sharma"
        st.rerun()
with exp_col2:
    if st.button("🚨 Acute Chest Pressure", use_container_width=True):
        st.session_state.symptom_text = "I have a crushing chest pressure radiating down to my left arm, along with sweating and difficulty breathing."
        if not st.session_state.active_patient_name:
            st.session_state.active_patient_name = "Rajesh Kumar"
        st.rerun()
with exp_col3:
    if st.button("👶 Infant High Fever", use_container_width=True):
        st.session_state.symptom_text = "My 2 month old baby has a fever of 101 F, is crying weakly, and refusing to feed."
        if not st.session_state.active_patient_name:
            st.session_state.active_patient_name = "Baby Aarav"
        st.rerun()
with exp_col4:
    if st.button("🌿 Itchy Skin Rash", use_container_width=True):
        st.session_state.symptom_text = "I have an itchy red bumpy rash spreading on both of my forearms for the past 4 days."
        if not st.session_state.active_patient_name:
            st.session_state.active_patient_name = "Ananya Verma"
        st.rerun()

# Clinical Intake Form
with st.form("symptom_form"):
    # 1. Patient Identification Header
    st.markdown("#### 👤 1. Patient Identification & Health Record (EHR) *")
    id_col1, id_col2, id_col3, id_col4 = st.columns([2.5, 2, 1.5, 1.5])

    with id_col1:
        patient_name = st.text_input(
            "Patient Full Name * (Required):",
            value=st.session_state.active_patient_name,
            placeholder="Enter patient full name (e.g. Sharique Khan, Priya Sharma)"
        )
    with id_col2:
        patient_id = st.text_input(
            "Patient ID (EHR):",
            value=st.session_state.active_patient_id,
            help="Unique identifier for tracking your longitudinal medical records across consultations."
        )
    with id_col3:
        gender = st.selectbox("Gender:", ["Male", "Female", "Other", "Prefer not to disclose"], index=0)
    with id_col4:
        blood_group = st.selectbox("Blood Group:", ["Unknown", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"], index=3)

    # 2. Symptoms Description
    st.markdown("#### 🗣️ 2. Describe Your Symptoms & Concerns *")
    user_symptoms = st.text_area(
        "Describe what you are experiencing in plain language * (Required):",
        value=st.session_state.symptom_text,
        height=100,
        placeholder="e.g. 'I have had a severe throbbing headache since yesterday morning with fever and fatigue...'"
    )

    # 3. Clinical Demographics & History
    st.markdown("#### ⚙️ 3. Clinical Context & Demographics")
    fcol1, fcol2, fcol3, fcol4 = st.columns(4)

    with fcol1:
        exact_age = st.number_input("Patient Exact Age (Years)", min_value=0, max_value=115, value=28, step=1)
        demo_category = classify_demographic(exact_age)
        st.caption(f"Stratification: **{demo_category}**")

    with fcol2:
        duration = st.selectbox(
            "Symptom Duration",
            ["Just started (< 12 hours)", "1 - 3 days", "4 - 7 days", "1 - 2 weeks", "More than 2 weeks"],
            index=1
        )

    with fcol3:
        severity = st.slider("Self-Reported Pain/Severity (1-10)", min_value=1, max_value=10, value=3)

    with fcol4:
        supported_langs = country_cfg.get("languages", ["English", "Hindi (हिन्दी)", "Spanish (Español)"])
        selected_lang = st.selectbox("Preferred Report Language:", supported_langs, index=0)

    # Contextual flags: Pregnancy, Chronic conditions, Medications
    ccol1, ccol2, ccol3 = st.columns([1.5, 2, 2])
    with ccol1:
        is_pregnant = st.checkbox("Patient is currently pregnant", value=False)
        trimester = None
        if is_pregnant:
            trimester = st.selectbox("Trimester", ["1st Trimester", "2nd Trimester", "3rd Trimester", "Postpartum"])
    with ccol2:
        medical_history = st.text_input("Known Chronic Conditions:", placeholder="e.g. Diabetes, Hypertension, Asthma, None")
    with ccol3:
        current_meds = st.text_input("Current Medications:", placeholder="e.g. Paracetamol, Metformin, Inhaler, None")

    bcol1, bcol2 = st.columns([1.5, 4])
    with bcol1:
        submit_btn = st.form_submit_button("🔍 Run Clinical Assessment & RAG", use_container_width=True, type="primary")
    with bcol2:
        clear_btn = st.form_submit_button("🔄 Clear Input", use_container_width=False)

if clear_btn:
    st.session_state.symptom_text = ""
    st.session_state.current_assessment = None
    st.session_state.last_profile = None
    st.rerun()

if submit_btn:
    validation_errors = []
    clean_name = patient_name.strip() if patient_name else ""
    clean_symptoms = user_symptoms.strip() if user_symptoms else ""

    if not clean_name or len(clean_name) < 2:
        validation_errors.append("• **Patient Full Name** is required to generate your clinical EHR dossier and record.")
    if not clean_symptoms or len(clean_symptoms) < 6:
        validation_errors.append("• **Symptoms Description** is required (please describe what the patient is experiencing in plain language).")

    if validation_errors:
        st.error(
            "⚠️ **Mandatory Patient Intake Required**\n\n"
            "You must enter all required patient details before running the clinical assessment:\n\n"
            + "\n".join(validation_errors)
        )
    else:
        assigned_name = clean_name
        assigned_id = patient_id.strip() if patient_id.strip() else generate_patient_id()
        st.session_state.active_patient_id = assigned_id
        st.session_state.active_patient_name = assigned_name

        profile = UserSymptomProfile(
            patient_id=assigned_id,
            patient_name=assigned_name,
            gender=gender,
            blood_group=blood_group,
            symptoms_text=user_symptoms.strip(),
            exact_age=int(exact_age),
            age_group=demo_category,
            duration=duration,
            severity=int(severity),
            is_pregnant=is_pregnant,
            trimester=trimester,
            medical_history=medical_history,
            current_medications=current_meds,
            country=country_cfg.get("name", "India"),
            language=selected_lang
        )
        st.session_state.last_profile = profile

        with st.spinner("Screening safety red flags & retrieving clinical protocols via RAG..."):
            assessment, source = ai_service.assess_symptoms(profile)
            st.session_state.current_assessment = assessment
            st.session_state.assessment_source = source

            # Automatically persist consultation session into SQLite EHR
            try:
                session_rec = PatientSession(
                    patient_id=profile.patient_id,
                    patient_name=profile.patient_name,
                    gender=profile.gender,
                    blood_group=profile.blood_group,
                    created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    symptoms_text=profile.symptoms_text,
                    age_group=f"{profile.exact_age} yrs",
                    duration=profile.duration,
                    severity=profile.severity,
                    triage_level=assessment.triage_level.value,
                    suggested_specialty=assessment.suggested_specialty or "General Physician",
                    assessment_json=assessment.model_dump_json(),
                    country=profile.country,
                    language=profile.language,
                    notes=f"Triage: {assessment.triage_level.value}. Specialty: {assessment.suggested_specialty}"
                )
                saved_id = save_session(session_rec)
                st.session_state.last_saved_session_id = saved_id
            except Exception:
                pass

# DISPLAY STRUCTURED ASSESSMENT & RAG RESULTS
if st.session_state.current_assessment and st.session_state.last_profile:
    assessment = st.session_state.current_assessment
    profile = st.session_state.last_profile

    st.markdown("---")
    st.subheader(f"📋 Clinical Assessment & Care Navigation for {profile.patient_name} ({profile.patient_id})")
    st.caption(f"**Clinical Intelligence Engine:** `{st.session_state.assessment_source}` | **Patient EHR:** `{profile.patient_id}`")

    # 1. Triage Urgency Banner
    badge_html = render_triage_badge(assessment.triage_level)
    st.markdown(f"### Urgency Status: {badge_html}", unsafe_allow_html=True)

    if assessment.triage_level == TriageLevel.EMERGENCY:
        st.error(
            f"🚨 **EMERGENCY WARNING:** {assessment.recommended_next_step}\n\n"
            f"**Please call {country_cfg.get('emergency_number')} (Ambulance: {country_cfg.get('ambulance')}) or proceed to the nearest emergency room immediately.**"
        )
    elif assessment.triage_level == TriageLevel.URGENT:
        st.warning(f"⚠️ **PROMPT MEDICAL ATTENTION:** {assessment.recommended_next_step}")
    else:
        st.info(f"ℹ️ **RECOMMENDED ACTION:** {assessment.recommended_next_step}")

    # RAG Grounding Protocols Callout
    if assessment.retrieved_protocols:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #f0fdfa 0%, #e6fffa 100%); border: 2px solid #0d9488; border-radius: 10px; padding: 14px 18px; margin: 12px 0 16px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:800; color:#0f766e; font-size:1.0rem;">📚 Evidence-Based Clinical Guidelines (RAG Protocol Grounding Active)</div>
                    <span style="background:#0d9488; color:white; font-size:0.75rem; font-weight:bold; padding:2px 8px; border-radius:10px;">ICMR • WHO • NICE Protocols</span>
                </div>
                <div style="font-size:0.83rem; color:#334155; margin-top:4px;">
                    This assessment references excerpts from the following clinical practice guidelines:
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        for prot in assessment.retrieved_protocols:
            st.markdown(
                f"""
                <div style="background:#ffffff; padding:10px 14px; border-radius:8px; margin-bottom:8px; border:1px solid #cbd5e1; border-left:4px solid #0d9488;">
                    <div style="font-weight:700; color:#0f766e; font-size:0.92rem;">📖 {prot.get('title')}</div>
                    <div style="font-size:0.80rem; color:#64748b; margin-top:2px;"><b>Authority:</b> {prot.get('source')} | <b>Domain:</b> {prot.get('category')}</div>
                    <div style="font-size:0.84rem; color:#1e293b; margin-top:5px; font-style:italic;">"{prot.get('content')}"</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 2-column layout for structured cards
    rcol1, rcol2 = st.columns(2)

    with rcol1:
        # Reported Symptoms Summary
        st.markdown(
            f"""
            <div class="mg-card">
                <div class="mg-card-header">📝 Patient Health Profile Summary</div>
                <div style="font-size:0.85rem; color:#0284c7; margin-bottom:8px;">
                    <b>Patient Name:</b> {profile.patient_name} | <b>ID:</b> {profile.patient_id} | <b>Blood:</b> {profile.blood_group}
                </div>
            """,
            unsafe_allow_html=True
        )
        for sym in assessment.symptom_summary:
            st.markdown(f"• **{sym}**")
        st.markdown(f"<div style='font-size:0.82rem; color:#64748b; margin-top:6px;'><b>Age:</b> {profile.exact_age} yrs • <b>Gender:</b> {profile.gender} • <b>Duration:</b> {profile.duration}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Missing Information
        if assessment.missing_information:
            st.markdown(
                """
                <div class="mg-card">
                    <div class="mg-card-header">❓ Clinical Details Not Provided / Uncertain</div>
                """,
                unsafe_allow_html=True
            )
            for m in assessment.missing_information:
                st.markdown(f"• {m}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Follow-Up Questions
        if assessment.follow_up_questions:
            st.markdown(
                """
                <div class="mg-card">
                    <div class="mg-card-header">💬 Clarifying Questions to Consider</div>
                """,
                unsafe_allow_html=True
            )
            for q in assessment.follow_up_questions:
                st.markdown(f"• *{q}*")
            st.markdown("</div>", unsafe_allow_html=True)

    with rcol2:
        # Possible Explanations (Strictly Possibilities)
        st.markdown(
            """
            <div class="mg-card">
                <div class="mg-card-header">💡 Potential Explanations (Non-Diagnostic)</div>
            """,
            unsafe_allow_html=True
        )
        st.caption("General possibilities for educational context, strictly non-diagnostic:")
        for exp in assessment.possible_explanations:
            st.markdown(f"• {exp}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Safe Self-Care Guidance
        if assessment.general_guidance:
            st.markdown(
                """
                <div class="mg-card">
                    <div class="mg-card-header">🌿 Supportive General Self-Care</div>
                """,
                unsafe_allow_html=True
            )
            for g in assessment.general_guidance:
                st.markdown(f"• {g}")
            st.markdown("</div>", unsafe_allow_html=True)

        # Warning Signs
        if assessment.warning_signs:
            st.markdown(
                """
                <div class="mg-card" style="border-left: 5px solid #ef4444;">
                    <div class="mg-card-header" style="color: #991b1b;">⚠️ Red Flag Warning Signs</div>
                """,
                unsafe_allow_html=True
            )
            st.caption("Seek emergency clinical care immediately if any of these manifest:")
            for w in assessment.warning_signs:
                st.markdown(f"• <font color='#dc2626'><b>!</b></font> {w}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Medical Specialty & Provider Search CTA
    st.markdown("---")
    scol1, scol2 = st.columns([2, 1])

    with scol1:
        st.markdown(f"### 🏥 Recommended Clinical Specialty: **{assessment.suggested_specialty}**")
        st.markdown(
            f"Consulting a **{assessment.suggested_specialty}** is recommended for {profile.patient_name}. "
            f"You can now explore clinics and hospitals providing care in this specialty near your location."
        )

    with scol2:
        btn_label = f"📍 Find {assessment.suggested_specialty} Nearby →"
        if st.button(btn_label, type="primary", use_container_width=True):
            st.session_state["target_specialty"] = assessment.suggested_specialty
            st.session_state["specialty_from_assistant"] = True
            st.session_state["target_country"] = profile.country
            st.session_state["target_patient_name"] = profile.patient_name
            st.switch_page("pages/2_Find_Doctors.py")

    # Multilingual Report Downloads & Session Persistence
    st.markdown("---")
    st.markdown(f"### 💾 Download Clinical Summary & Save to Record ({profile.patient_id})")

    session_dict = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patient_id": profile.patient_id,
        "patient_name": profile.patient_name,
        "gender": profile.gender,
        "blood_group": profile.blood_group,
        "symptoms_text": profile.symptoms_text,
        "exact_age": profile.exact_age,
        "age_group": f"{profile.exact_age} yrs",
        "duration": profile.duration,
        "severity": profile.severity,
        "triage_level": assessment.triage_level.value,
        "suggested_specialty": assessment.suggested_specialty,
        "country": profile.country,
        "language": profile.language,
        "recommended_action": assessment.recommended_next_step,
        "assessment_json": assessment.model_dump_json()
    }

    ecol1, ecol2, ecol3 = st.columns(3)

    with ecol1:
        st.success(f"✅ Record auto-saved to EHR: **{profile.patient_id}**")
        st.page_link("pages/4_Patient_Portal.py", label="View EHR Dossier →", icon="🗂️")

    with ecol2:
        pdf_bytes = generate_pdf_report(session_dict, target_language=profile.language)
        clean_name = profile.patient_name.replace(' ', '_').strip() or "Patient"
        st.download_button(
            label=f"📄 Download PDF Summary ({profile.language})",
            data=pdf_bytes,
            file_name=f"MediGuide_{clean_name}_{profile.patient_id}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with ecol3:
        html_summary = generate_html_clinical_summary(session_dict, target_language=profile.language)
        st.download_button(
            label=f"🌐 Printable Clinical Summary ({profile.language})",
            data=html_summary.encode("utf-8"),
            file_name=f"MediGuide_Clinical_Summary_{profile.patient_id}.html",
            mime="text/html",
            use_container_width=True
        )

    st.markdown("---")
    st.caption(f"⚠️ *{assessment.disclaimer}*")

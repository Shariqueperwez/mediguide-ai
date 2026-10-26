"""
MediGuide AI — Intelligent Healthcare Assistance & Doctor Finder (India Clinical Network)
Main Application Landing Page (Home)
"""

import sys
import importlib
import streamlit as st

for _mod in list(sys.modules.keys()):
    if _mod.startswith("src.") or _mod == "src":
        try:
            importlib.reload(sys.modules[_mod])
        except Exception:
            pass

st.set_page_config(
    page_title="MediGuide AI — Clinical Healthcare Navigator",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.ui_components import apply_theme, render_emergency_banner, render_sidebar
from src.config import APP_NAME, APP_SUBTITLE, get_active_country, is_demo_mode

apply_theme()
render_sidebar()

country_cfg = get_active_country()

# ==========================================
# 🌟 EXECUTIVE HERO SECTION
# ==========================================
st.markdown(
    f"""
    <div class="mg-hero-compact">
        <div class="mg-hero-compact-left">
            <div class="mg-hero-badge">
                <span class="mg-hero-badge-dot"></span>
                National Care Navigation &bull; India Clinical Edition
            </div>
            <div class="mg-hero-compact-title">
                Intelligent Clinical Triage <span style="color: #0d9488;">&amp; Care Navigation</span>
            </div>
            <p class="mg-hero-compact-desc">
                Clinical decision support grounded in <b>ICMR, WHO &amp; NICE</b> protocols with sub-second AI triage and deterministic red-flag safety overrides.
            </p>
        </div>
        <div class="mg-hero-compact-right">
            <div class="mg-compact-stat mg-compact-stat-red">
                <span style="font-size: 1.25rem;">🚨</span>
                <div>
                    <div class="mg-stat-val" style="color: #b91c1c;">112 &bull; 108</div>
                    <div class="mg-stat-lbl">Ambulance Hotline</div>
                </div>
            </div>
            <div class="mg-compact-stat mg-compact-stat-teal">
                <span style="font-size: 1.25rem;">📚</span>
                <div>
                    <div class="mg-stat-val" style="color: #0f766e;">ICMR &bull; WHO</div>
                    <div class="mg-stat-lbl">Evidence Protocols</div>
                </div>
            </div>
            <div class="mg-compact-stat mg-compact-stat-blue">
                <span style="font-size: 1.25rem;">🔒</span>
                <div>
                    <div class="mg-stat-val" style="color: #1d4ed8;">DISHA &bull; RBAC</div>
                    <div class="mg-stat-lbl">Privacy Architecture</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Emergency Alert Banner
render_emergency_banner()

# ==========================================
# 🚀 FAST CLINICAL SERVICES ACCESS (PRIMARY ACTIONS)
# ==========================================
st.markdown("### 🚀 Fast Clinical Services Access")
b1, b2, b3 = st.columns(3)
with b1:
    st.page_link(
        "pages/1_Symptom_Assistant.py",
        label="Start Clinical Symptom Assessment →",
        icon="🩺",
        use_container_width=True
    )
with b2:
    st.page_link(
        "pages/2_Find_Doctors.py",
        label="Find Nearby Hospitals & Doctors (GPS) →",
        icon="📍",
        use_container_width=True
    )
with b3:
    st.page_link(
        "pages/4_Patient_Portal.py",
        label="Patient EHR Portal & History (By ID) →",
        icon="🗂️",
        use_container_width=True
    )

st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

# ==========================================
# 💡 1-CLICK LIVE DEMONSTRATION SCENARIOS
# ==========================================
st.markdown("##### 💡 1-Click Interactive Clinical Scenarios (Try Instantly):")
demo_col1, demo_col2, demo_col3, demo_col4 = st.columns(4)

with demo_col1:
    if st.button("🌡️ Acute Fever & Headache", use_container_width=True, help="Evaluates acute high fever, headache and fatigue under ICMR protocols"):
        st.session_state["symptom_text"] = "I have had a high fever of around 101.5, severe throbbing headache, and fatigue for the last 2 days."
        if not st.session_state.get("active_patient_name"):
            st.session_state["active_patient_name"] = "Priya Sharma"
        st.switch_page("pages/1_Symptom_Assistant.py")

with demo_col2:
    if st.button("🚨 Acute Chest Pressure (Triage)", use_container_width=True, help="Tests deterministic emergency safety override"):
        st.session_state["symptom_text"] = "I have a crushing chest pressure radiating down to my left arm, along with sweating and difficulty breathing."
        if not st.session_state.get("active_patient_name"):
            st.session_state["active_patient_name"] = "Rajesh Kumar"
        st.switch_page("pages/1_Symptom_Assistant.py")

with demo_col3:
    if st.button("👁️ Vision Blur & Eye Redness", use_container_width=True, help="Tests clinical routing to Ophthalmology & Eye Centers"):
        st.session_state["symptom_text"] = "I have severe pain in my right eye with redness, foreign body sensation, and blurred vision since yesterday."
        if not st.session_state.get("active_patient_name"):
            st.session_state["active_patient_name"] = "Ananya Verma"
        st.switch_page("pages/1_Symptom_Assistant.py")

with demo_col4:
    if st.button("👶 Infant High Fever", use_container_width=True, help="Tests neonatal & pediatric clinical escalation guardrails"):
        st.session_state["symptom_text"] = "My 2 month old baby has a fever of 101 F, is crying weakly, and refusing to feed."
        if not st.session_state.get("active_patient_name"):
            st.session_state["active_patient_name"] = "Baby Aarav"
        st.switch_page("pages/1_Symptom_Assistant.py")

st.markdown("---")

# ==========================================
# 💡 WHAT IS MEDIGUIDE AI & HOW IT HELPS YOU
# ==========================================
st.markdown(
    """
    <div class="mg-journey-box" style="background: linear-gradient(135deg, #f8fafc 0%, #f0fdfa 100%); border: 1px solid #ccfbf1; border-radius: 14px; padding: 22px 24px; margin: 18px 0 24px 0; box-shadow: 0 2px 8px rgba(13,148,136,0.04);">
        <div style="font-size: 1.22rem; font-weight: 800; color: #0f172a; margin-bottom: 6px;">
            💡 What is MediGuide AI &amp; How Does It Assist You?
        </div>
        <div style="font-size: 0.90rem; color: #475569; margin-bottom: 18px; line-height: 1.55;">
            Navigating healthcare in India can often be confusing. MediGuide AI acts as your intelligent clinical navigator—helping you make safe, evidence-grounded healthcare decisions before visiting a clinic.
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px;">
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 4px solid #0d9488; border-radius: 10px; padding: 18px 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="font-size: 1.0rem; font-weight: 800; color: #0f766e; margin-bottom: 8px;">
                    1️⃣ Smart Symptom Triage
                </div>
                <div style="font-size: 0.86rem; color: #334155; line-height: 1.55;">
                    Instead of alarming web searches, describe your symptoms naturally. The engine deterministically screens emergency red flags, evaluates clinical urgency, and tells you whether you need emergency, urgent, or routine care.
                </div>
            </div>
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 4px solid #0284c7; border-radius: 10px; padding: 18px 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="font-size: 1.0rem; font-weight: 800; color: #0369a1; margin-bottom: 8px;">
                    2️⃣ Right Doctor &amp; Hospital Matching
                </div>
                <div style="font-size: 0.86rem; color: #334155; line-height: 1.55;">
                    Never guess which medical specialist to consult. MediGuide routes your condition to the correct clinical specialty (e.g., Cardiology, ENT, Ophthalmology) and discovers verified nearby hospitals via live GPS.
                </div>
            </div>
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 4px solid #166534; border-radius: 10px; padding: 18px 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
                <div style="font-size: 1.0rem; font-weight: 800; color: #15803d; margin-bottom: 8px;">
                    3️⃣ Doctor-Ready Medical Dossier
                </div>
                <div style="font-size: 0.86rem; color: #334155; line-height: 1.55;">
                    Generates a structured clinical consultation summary in your preferred language (English, Hindi, Bengali, Tamil, Telugu). Download as a PDF or printable HTML to share with your doctor during consultation.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 📚 HOW CLINICAL RAG WORKS (FLOW PIPELINE)
# ==========================================
st.markdown("### 📚 How Clinical RAG (Retrieval-Augmented Generation) Operates")
st.markdown(
    """
    <div class="mg-workflow-box" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:20px; margin-bottom:24px; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:16px;">
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-top:4px solid #0f766e; border-radius:10px; padding:16px;">
                <div style="font-weight:800; color:#0f766e; font-size:0.96rem;">1️⃣ Symptom & Risk Intake</div>
                <p style="font-size:0.85rem; color:#475569; margin-top:8px; line-height:1.5;">
                    Captures patient-described symptoms in plain conversational language alongside <b>exact age, gender, pain severity (1-10), and duration</b>.
                </p>
            </div>
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-top:4px solid #ef4444; border-radius:10px; padding:16px;">
                <div style="font-weight:800; color:#b91c1c; font-size:0.96rem;">2️⃣ Deterministic Safety Guard</div>
                <p style="font-size:0.85rem; color:#475569; margin-top:8px; line-height:1.5;">
                    Independent rule engine screens life-threatening red flags (chest pain, stroke FAST, neonatal fever, hemorrhage) <b>before any AI inference</b>.
                </p>
            </div>
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-top:4px solid #0284c7; border-radius:10px; padding:16px;">
                <div style="font-weight:800; color:#0284c7; font-size:0.96rem;">3️⃣ Vector Protocol Retrieval</div>
                <p style="font-size:0.85rem; color:#475569; margin-top:8px; line-height:1.5;">
                    Semantic similarity search matches published clinical practice guidelines (<b>ICMR, WHO, NHS NICE, CDC</b>) directly relevant to the complaint.
                </p>
            </div>
            <div style="background:#ffffff; border:1px solid #cbd5e1; border-top:4px solid #166534; border-radius:10px; padding:16px;">
                <div style="font-weight:800; color:#166534; font-size:0.96rem;">4️⃣ Evidence-Grounded Plan</div>
                <p style="font-size:0.85rem; color:#475569; margin-top:8px; line-height:1.5;">
                    The Neural Core generates a doctor consultation preparation report citing retrieved protocols, with <b>1-click GPS routing to nearby specialists</b>.
                </p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ==========================================
# 🌟 ENTERPRISE PLATFORM CAPABILITIES
# ==========================================
st.markdown("### 🌟 Platform Clinical Architecture & Capabilities")

st.markdown(
    """
    <div class="mg-feature-grid">
        <div class="mg-equal-card">
            <div class="mg-card-header">🗣️ Natural Language Clinical Triage</div>
            <p class="mg-card-body">
                Evaluates symptoms described in everyday conversational language. Automatically extracts anatomical regions, duration, severity scale (1-10), and acute clinical modifiers.
            </p>
        </div>
        <div class="mg-equal-card">
            <div class="mg-card-header">🛡️ Deterministic Safety Overrides</div>
            <p class="mg-card-body">
                Hard-coded rule engine that overrides AI for life-threatening emergencies (acute chest pain, stroke FAST signs, respiratory distress) with immediate 112/108 escalations.
            </p>
        </div>
        <div class="mg-equal-card">
            <div class="mg-card-header">🌐 Multilingual Clinical Summaries</div>
            <p class="mg-card-body">
                Export physician-ready consultation dossiers in PDF or printable HTML formats. Fully localized into English, Hindi (हिन्दी), Bengali (বাংলা), Tamil (தமிழ்), and Telugu (తెలుగు).
            </p>
        </div>
        <div class="mg-equal-card">
            <div class="mg-card-header">📚 Evidence-Based RAG Protocols</div>
            <p class="mg-card-body">
                Anchors AI recommendations in published reference guidelines from ICMR, WHO, and NICE. Explicitly cites medical protocol sources in every generated clinical dossier.
            </p>
        </div>
        <div class="mg-equal-card">
            <div class="mg-card-header">📍 Real-Time Facility Discovery (GPS)</div>
            <p class="mg-card-body">
                Live OpenStreetMap and Overpass API integration with browser GPS. Discovers verified public hospitals, specialty clinics, and emergency centers anywhere across India.
            </p>
        </div>
        <div class="mg-equal-card">
            <div class="mg-card-header">🗂️ Private Patient EHR &amp; RBAC</div>
            <p class="mg-card-body">
                Strict role-based privacy: patients securely access their personal consultation history by Patient ID, while clinical administrators unlock the master directory via passkey.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ==========================================
# 🏥 MEDICAL SPECIALTIES SUPPORTED
# ==========================================
st.markdown("### 🏥 Core Medical Specialties Covered")
st.markdown(
    """
    <div class="mg-specialty-grid">
        <div class="mg-specialty-pill">
            <span class="mg-spec-icon">❤️</span>
            <span class="mg-spec-text">Cardiology &amp; Cardiac Surgery</span>
        </div>
        <div class="mg-specialty-pill">
            <span class="mg-spec-icon">👁️</span>
            <span class="mg-spec-text">Ophthalmology (Eye Hospitals)</span>
        </div>
        <div class="mg-specialty-pill">
            <span class="mg-spec-icon">🫁</span>
            <span class="mg-spec-text">Pulmonology &amp; Respiratory Care</span>
        </div>
        <div class="mg-specialty-pill">
            <span class="mg-spec-icon">🦴</span>
            <span class="mg-spec-text">Orthopedics &amp; Trauma Surgery</span>
        </div>
        <div class="mg-specialty-pill">
            <span class="mg-spec-icon">👶</span>
            <span class="mg-spec-text">Pediatrics &amp; Neonatology</span>
        </div>
        <div class="mg-specialty-pill">
            <span class="mg-spec-icon">🦷</span>
            <span class="mg-spec-text">Dentistry &amp; Maxillofacial Care</span>
        </div>
        <div class="mg-specialty-pill">
            <span class="mg-spec-icon">👂</span>
            <span class="mg-spec-text">Otolaryngology (ENT Care)</span>
        </div>
        <div class="mg-specialty-pill">
            <span class="mg-spec-icon">🩺</span>
            <span class="mg-spec-text">Internal Medicine &amp; General Triage</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 🌐 ENTERPRISE CLINICAL FOOTER
# ==========================================
st.markdown(
    """
    <div class="mg-footer" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 26px; margin-top: 28px; margin-bottom: 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
                <div style="font-weight: 800; font-size: 1.05rem; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                    <span style="color: #0d9488; font-weight: 900;">✚</span> MediGuide AI &bull; National Clinical Navigation Network
                </div>
                <div style="font-size: 0.82rem; color: #64748b; margin-top: 4px;">
                    Clinical Decision Support &bull; Deterministic Red-Flag Triage &bull; Evidence-Based RAG &bull; OpenStreetMap Provider Routing
                </div>
            </div>
            <div style="display: flex; gap: 16px; font-size: 0.82rem; font-weight: 700; color: #0f766e;">
                <span>🚨 ER: 112 / 108</span>
                <span>🔒 DISHA-Aligned RBAC</span>
                <span>📚 ICMR &bull; WHO &bull; NICE</span>
            </div>
        </div>
        <div style="border-top: 1px solid #f1f5f9; margin-top: 14px; padding-top: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; font-size: 0.76rem; color: #94a3b8;">
            <div>
                &copy; 2026 MediGuide AI. Designed for Clinical Navigation &amp; Doctor Consultation Preparation.
            </div>
            <div>
                Non-Diagnostic Clinical Decision Support &bull; Strictly Educational &amp; Care Navigation
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "⚠️ **CLINICAL NOTICE:** MediGuide AI is a decision-support care navigator and doctor consultation preparation platform. "
    "It never diagnoses diseases or prescribes treatments. In an emergency, always contact national emergency services (112 / 108) immediately."
)

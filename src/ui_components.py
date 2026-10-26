"""
UI Components and Theming Utilities for MediGuide AI.
Provides reusable styled cards, badges, emergency banners, country selector,
and professional AI engine diagnostics without exposing raw vendor names.
"""

import streamlit as st
from src.models import TriageLevel
from src.config import SUPPORTED_COUNTRIES, get_active_country, is_demo_mode, ENGINE_BRAND_NAME


CUSTOM_CSS = """
<style>
/* MediGuide AI Clinical Healthcare Theme */
:root {
    --primary-color: #0d9488;
    --primary-dark: #0f766e;
    --primary-light: #ccfbf1;
    --emergency-red: #ef4444;
    --emergency-bg: #fee2e2;
    --urgent-orange: #f97316;
    --urgent-bg: #ffedd5;
    --routine-blue: #2563eb;
    --routine-bg: #dbeafe;
    --selfcare-green: #10b981;
    --selfcare-bg: #dcfce7;
    --slate-800: #1e293b;
    --slate-600: #475569;
    --slate-100: #f1f5f9;
}

/* Card Styling */
.mg-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}

.mg-card-header {
    font-size: 1.12rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Equal-Dimension Feature Cards Grid */
.mg-feature-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
    margin-bottom: 24px;
}

@media (max-width: 900px) {
    .mg-feature-grid {
        grid-template-columns: 1fr;
    }
}

.mg-equal-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px 22px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    height: 100%;
    min-height: 175px;
    box-sizing: border-box;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.mg-equal-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.07);
}

.mg-equal-card .mg-card-header {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    min-height: 28px;
}

.mg-equal-card .mg-card-body {
    font-size: 0.88rem;
    color: #475569;
    line-height: 1.55;
    margin: 0;
    flex-grow: 1;
}

/* Symmetrical Specialty Pill Grid (Equal Width & Height in Mint Capsule Shade) */
.mg-specialty-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 22px;
}

@media (max-width: 960px) {
    .mg-specialty-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 520px) {
    .mg-specialty-grid {
        grid-template-columns: 1fr;
    }
}

.mg-specialty-pill {
    background: #f0fdfa;
    border: 1.5px solid #99f6e4;
    border-radius: 9999px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    box-shadow: 0 1px 3px rgba(13, 148, 136, 0.06);
    transition: all 0.15s ease-in-out;
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    min-height: 42px;
    text-align: center;
}

.mg-specialty-pill:hover {
    background: #ccfbf1;
    border-color: #0d9488;
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(13, 148, 136, 0.12);
}

.mg-spec-icon {
    font-size: 1.05rem;
    flex-shrink: 0;
    line-height: 1;
}

.mg-spec-text {
    font-size: 0.82rem;
    font-weight: 700;
    color: #0f766e;
    line-height: 1.25;
}

/* Emergency Banner */
.mg-emergency-banner {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    border: 2px solid #ef4444;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0 18px 0;
    color: #991b1b;
}

.mg-emergency-title {
    font-size: 1.05rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 8px;
    color: #7f1d1d;
}

/* Badges */
.mg-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.mg-badge-emergency {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #f87171;
}

.mg-badge-urgent {
    background-color: #ffedd5;
    color: #9a3412;
    border: 1px solid #fb923c;
}

.mg-badge-routine {
    background-color: #dbeafe;
    color: #1e40af;
    border: 1px solid #93c5fd;
}

.mg-badge-selfcare {
    background-color: #dcfce7;
    color: #166534;
    border: 1px solid #86efac;
}

/* Provider Card */
.provider-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    border: 1px solid #e2e8f0;
    border-left: 5px solid #0d9488;
    transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.provider-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.provider-name {
    font-size: 1.12rem;
    font-weight: 700;
    color: #0f172a;
}

.provider-specialty {
    font-size: 0.88rem;
    color: #0d9488;
    font-weight: 600;
    margin-bottom: 6px;
}

.provider-address {
    font-size: 0.84rem;
    color: #64748b;
    margin-bottom: 8px;
}

/* Hide default unstyled Streamlit multi-page navigation */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Sleek sidebar container styling */
section[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}

/* Custom Navigation Section Title */
.mg-nav-header {
    font-size: 0.70rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin: 16px 0 6px 4px;
}

/* Compact Executive Hero Section - Medical Light Theme */
.mg-hero-compact {
    background: linear-gradient(135deg, #ffffff 0%, #f0fdfa 60%, #e6fffa 100%);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    border: 1px solid #ccfbf1;
    border-left: 6px solid #0d9488;
    box-shadow: 0 4px 16px rgba(13, 148, 136, 0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}

@media (max-width: 960px) {
    .mg-hero-compact {
        flex-direction: column;
        align-items: flex-start;
    }
}

.mg-hero-compact-left {
    flex: 1 1 auto;
}

.mg-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #e6fffa;
    border: 1px solid #99f6e4;
    border-radius: 16px;
    padding: 3px 11px;
    font-size: 0.70rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #0f766e;
    margin-bottom: 8px;
}

.mg-hero-badge-dot {
    width: 7px;
    height: 7px;
    background-color: #0d9488;
    border-radius: 50%;
    display: inline-block;
}

.mg-hero-compact-title {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #0f172a;
    line-height: 1.25;
    margin: 0 0 6px 0;
}

.mg-hero-compact-desc {
    font-size: 0.90rem;
    line-height: 1.5;
    color: #475569;
    margin: 0;
    max-width: 680px;
}

.mg-hero-compact-desc b {
    color: #0f172a;
}

.mg-hero-compact-right {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
    flex-wrap: wrap;
}

.mg-compact-stat {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.mg-compact-stat-red {
    border-left: 3px solid #ef4444;
}

.mg-compact-stat-teal {
    border-left: 3px solid #0d9488;
}

.mg-compact-stat-blue {
    border-left: 3px solid #2563eb;
}

.mg-stat-val {
    font-size: 0.96rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.15;
}

.mg-stat-lbl {
    font-size: 0.67rem;
    color: #64748b;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* =========================================================
   📱 COMPREHENSIVE RESPONSIVE MOBILE STYLING (< 768px)
   ========================================================= */
@media (max-width: 768px) {
    /* Allow Streamlit horizontal blocks to wrap cleanly on mobile */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 8px !important;
    }

    /* Stack or expand columns on mobile viewports */
    div[data-testid="column"] {
        min-width: 100% !important;
        width: 100% !important;
        flex: 1 1 100% !important;
        margin-bottom: 6px !important;
    }

    /* Main view container: eliminate excessive margin on mobile screens */
    .block-container {
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
        padding-top: 1.0rem !important;
        padding-bottom: 2.0rem !important;
        max-width: 100vw !important;
    }

    /* Prevent horizontal page shifts & off-screen scrollbars */
    html, body, [data-testid="stAppViewContainer"], .main {
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }

    /* Executive Hero: Clean vertical stack */
    .mg-hero-compact {
        padding: 14px 16px !important;
        margin-bottom: 14px !important;
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 12px !important;
    }

    .mg-hero-compact-title {
        font-size: 1.25rem !important;
        line-height: 1.25 !important;
    }

    .mg-hero-compact-desc {
        font-size: 0.85rem !important;
    }

    .mg-hero-compact-right {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
    }

    .mg-compact-stat {
        width: 100% !important;
        box-sizing: border-box !important;
        padding: 8px 12px !important;
    }

    /* Feature Grid & Capability Cards */
    .mg-feature-grid {
        grid-template-columns: 1fr !important;
        gap: 12px !important;
    }

    .mg-equal-card {
        min-height: auto !important;
        padding: 16px !important;
    }

    /* Specialty Grid: Single-column clean capsule buttons on smartphones */
    .mg-specialty-grid {
        grid-template-columns: 1fr !important;
        gap: 8px !important;
        margin-bottom: 18px !important;
    }

    .mg-specialty-pill {
        width: 100% !important;
        min-height: 44px !important;
        padding: 10px 14px !important;
        justify-content: flex-start !important;
        text-align: left !important;
        border-radius: 12px !important;
    }

    .mg-spec-text {
        font-size: 0.88rem !important;
        white-space: normal !important;
        word-break: break-word !important;
    }

    /* Responsive Footer & Section Boxes */
    .mg-footer {
        padding: 16px 14px !important;
    }

    .mg-journey-box, .mg-workflow-box {
        padding: 16px 14px !important;
    }

    /* Touch-friendly buttons on mobile */
    .stButton > button {
        min-height: 42px !important;
    }
}
</style>
"""


def apply_theme():
    """Inject custom CSS theme into the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_emergency_banner():
    """Render localized emergency warning banner based on user's active country."""
    country_cfg = get_active_country()
    country_name = country_cfg.get("name", "International")
    em_number = country_cfg.get("emergency_number", "112")
    ambulance = country_cfg.get("ambulance", "112")
    poison = country_cfg.get("poison_control", "Local Emergency")

    st.markdown(
        f"""
        <div class="mg-emergency-banner">
            <div class="mg-emergency-title">
                🚨 EMERGENCY MEDICAL ALERT & IMMEDIATE ASSISTANCE ({country_name})
            </div>
            <div style="font-size: 0.92rem; margin-top: 6px; line-height: 1.45;">
                If you or someone nearby is experiencing <b>crushing chest pain, sudden difficulty breathing, stroke signs (face drooping / arm weakness / slurred speech), loss of consciousness, or uncontrolled bleeding</b>,
                please call <b>{em_number}</b> (Ambulance: <b>{ambulance}</b>) or proceed immediately to the nearest hospital emergency department.
                <br><i>MediGuide AI does not dispatch ambulances automatically and is not a substitute for clinical emergency care.</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_triage_badge(triage_level: TriageLevel or str) -> str:
    """Return HTML string for triage urgency badge."""
    val = triage_level.value if hasattr(triage_level, "value") else str(triage_level)
    val_upper = val.upper()

    if val_upper == "EMERGENCY":
        cls = "mg-badge-emergency"
        icon = "🚨"
        text = "Emergency — Immediate Care Required"
    elif val_upper == "URGENT":
        cls = "mg-badge-urgent"
        icon = "⚠️"
        text = "Urgent — Seek Evaluation within 12-24h"
    elif val_upper == "SELF_CARE":
        cls = "mg-badge-selfcare"
        icon = "🌿"
        text = "Self-Care & Observation"
    else:
        cls = "mg-badge-routine"
        icon = "🩺"
        text = "Routine — Schedule Doctor Visit"

    return f'<span class="mg-badge {cls}">{icon} {text}</span>'


def render_sidebar():
    """Render clinical sidebar with categorized navigation, patient card, and system status."""
    with st.sidebar:
        # 1. Hospital / System Brand Header
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px; padding-bottom:10px; border-bottom:1px solid #e2e8f0;">
                <div style="background:linear-gradient(135deg, #0d9488 0%, #0f766e 100%); color:#ffffff; width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.3rem; font-weight:900; box-shadow:0 2px 4px rgba(13,148,136,0.3);">
                    ✚
                </div>
                <div>
                    <div style="font-weight:800; font-size:1.15rem; color:#0f172a; line-height:1.2;">MediGuide AI</div>
                    <div style="font-size:0.72rem; color:#0d9488; font-weight:700; letter-spacing:0.04em;">CLINICAL DECISION SUPPORT</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. Dynamic Patient Identity Card (Real-time, never static)
        p_name = st.session_state.get("active_patient_name", "").strip()
        p_id = st.session_state.get("active_patient_id")
        if not p_id:
            from src.database import get_next_patient_id
            p_id = get_next_patient_id()
            st.session_state["active_patient_id"] = p_id

        if p_name:
            badge_html = '<span style="background:#dcfce7; color:#166534; font-size:0.68rem; font-weight:800; padding:2px 8px; border-radius:12px;">ACTIVE EHR</span>'
            name_display = f"<b>{p_name}</b>"
        else:
            badge_html = '<span style="background:#fef3c7; color:#92400e; font-size:0.68rem; font-weight:700; padding:2px 8px; border-radius:12px;">AWAITING INTAKE</span>'
            name_display = "<i>Intake Required</i>"

        st.markdown(
            f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; margin-bottom:14px; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.86rem; color:#0f172a;">👤 {name_display}</span>
                    {badge_html}
                </div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:4px;">
                    Record ID: <code style="color:#0f766e; font-weight:700;">{p_id}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 3. Categorized Clinical Navigation
        st.markdown('<div class="mg-nav-header">🩺 CLINICAL CARE & TRIAGE</div>', unsafe_allow_html=True)
        st.page_link("app.py", label="Home Portal", icon="🏠")
        st.page_link("pages/1_Symptom_Assistant.py", label="Symptom Assistant & Triage", icon="🩺")
        st.page_link("pages/2_Find_Doctors.py", label="Find Nearby Doctors (GPS)", icon="📍")

        st.markdown('<div class="mg-nav-header">🗂️ EHR & PATIENT RECORDS</div>', unsafe_allow_html=True)
        from src.auth import is_admin, authenticate_admin, logout_admin
        if is_admin():
            st.page_link("pages/4_Patient_Portal.py", label="Master EHR Registry (Admin)", icon="🗂️")
            st.page_link("pages/3_Session_History.py", label="Hospital Audit & Records (All)", icon="📂")
        else:
            st.page_link("pages/4_Patient_Portal.py", label="Patient EHR Portal (By ID)", icon="🗂️")
            st.page_link("pages/3_Session_History.py", label="Consultation Records & PDF", icon="📂")

        st.markdown('<div class="mg-nav-header">🛡️ COMPLIANCE & SAFETY</div>', unsafe_allow_html=True)
        st.page_link("pages/5_About_and_Safety.py", label="Clinical Protocols & Safety", icon="🛡️")

        st.markdown("---")

        # 4. Professional Engine Status Indicator (Zero vendor leakage)
        st.markdown("#### ⚙️ Clinical Engine Core")
        if is_demo_mode():
            st.info(
                "🔵 **Deterministic Protocol Core**\n\n"
                "• Rule-based safety guardrails.\n"
                "• RAG knowledge retrieval active."
            )
        else:
            st.success(
                "🟢 **Clinical Neural Core**\n\n"
                "• Active & Protocol Grounded.\n"
                "• Dual-layer safety verification."
            )
            # 1-click test button to confirm connection
            if st.button("⚡ Test Engine Connection", use_container_width=True):
                from src.ai_service import ai_service
                diag = ai_service.check_connection()
                if diag["is_active"]:
                    st.success(f"✅ Status: {diag['status']} ({diag['latency_ms']} ms)")
                else:
                    st.warning(f"⚠️ Status: {diag['status']}")

        st.caption(
            "MediGuide AI is a clinical decision-support and care navigation platform. "
            "It never diagnoses diseases or prescribes medication dosages."
        )


def render_top_portal_bar():
    """Render sleek top navigation bar with active patient identity, emergency hotline, and staff access."""
    from src.auth import is_admin, authenticate_admin, logout_admin
    p_name = st.session_state.get("active_patient_name", "").strip()
    p_id = st.session_state.get("active_patient_id")
    if not p_id:
        from src.database import get_next_patient_id
        p_id = get_next_patient_id()
        st.session_state["active_patient_id"] = p_id
    country_cfg = get_active_country()

    if is_admin():
        patient_label = "🔐 Clinician / Hospital Admin (Master Access)"
        badge_style = "background:#0f172a; color:#38bdf8; border:1px solid #334155;"
    elif p_name:
        patient_label = f"👤 {p_name} ({p_id})"
        badge_style = "background:#f0fdfa; color:#0f766e; border:1px solid #99f6e4;"
    else:
        patient_label = f"👤 Patient Session ({p_id})"
        badge_style = "background:#f8fafc; color:#475569; border:1px solid #cbd5e1;"

    top_col1, top_col2 = st.columns([3.6, 1.4])
    with top_col1:
        st.markdown(
            f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:8px 16px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; box-shadow:0 1px 3px rgba(0,0,0,0.03);">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-weight:800; font-size:1.0rem; color:#0f766e;">🏥 MediGuide Patient Portal</span>
                    <span style="{badge_style} font-size:0.80rem; font-weight:700; padding:2px 10px; border-radius:14px;">
                        {patient_label}
                    </span>
                </div>
                <div style="display:flex; align-items:center; gap:12px; font-size:0.82rem; color:#475569;">
                    <span>🌐 <b>{country_cfg.get('name')}</b></span>
                    <span style="color:#dc2626; font-weight:700;">🚨 Hotline: {country_cfg.get('emergency_number')}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with top_col2:
        with st.popover("⚙️ Profile & Staff Access", use_container_width=True):
            tab_pat, tab_staff = st.tabs(["👤 Patient Identity", "🔐 Clinician Mode"])
            with tab_pat:
                st.markdown("###### 👤 Active Patient Profile")
                new_name = st.text_input("Patient Full Name:", value=p_name, placeholder="e.g. Sharique Khan")
                new_id = st.text_input("Patient ID:", value=p_id, placeholder="e.g. MG-2026-01")
                if st.button("Update Profile Identity", type="primary", use_container_width=True):
                    st.session_state["active_patient_name"] = new_name.strip()
                    st.session_state["active_patient_id"] = new_id.strip() if new_id.strip() else "MG-2026-01"
                    st.rerun()

            with tab_staff:
                st.markdown("###### 🔐 Hospital Clinician / Admin Access")
                if is_admin():
                    st.success("🟢 **Clinician Master Access Active**\nYou have full access to all patient records.")
                    if st.button("Switch to Patient Mode (Sign Out)", type="secondary", use_container_width=True):
                        logout_admin()
                        st.rerun()
                else:
                    st.caption("Hospital administrators and doctors can unlock full master registry access across all patients.")
                    passkey = st.text_input("Staff Passcode:", type="password", placeholder="Default passkey: admin123")
                    if st.button("Unlock Clinician Access", type="primary", use_container_width=True):
                        if authenticate_admin(passkey):
                            st.success("Staff access granted!")
                            st.rerun()
                        else:
                            st.error("Invalid passcode. Please try again.")



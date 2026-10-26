"""
MediGuide AI — About, Architecture & Clinical Safety Documentation Page.
Details system design, RAG clinical knowledge grounding, ethics, and regulatory compliance.
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
    page_title="About & Safety — MediGuide AI",
    page_icon="🛡️",
    layout="wide"
)

from src.ui_components import apply_theme, render_sidebar

apply_theme()
render_sidebar()

st.title("🛡️ About MediGuide AI & Clinical Safety Protocols")
st.markdown(
    "Comprehensive documentation on architecture, RAG grounding, safety layers, "
    "responsible AI principles, data privacy, and global clinical compliance."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Purpose & Scope",
    "🛡️ Dual-Layer & RAG Architecture",
    "🔒 Privacy & Data Retention",
    "⚖️ Regulatory & Medical Ethics"
])

with tab1:
    st.markdown("### 🎯 Purpose & Scope")
    st.markdown(
        """
        **MediGuide AI** was created to address a critical healthcare accessibility gap:
        helping patients articulate unclear symptoms in plain language, detect emergency red flags early,
        and navigate efficiently to the right medical specialty and nearby clinic.

        #### What MediGuide AI IS:
        - ✅ **A Care Navigation Guide**: Directs patients to the appropriate clinical department (e.g. Ophthalmology vs ENT).
        - ✅ **An Emergency Red-Flag Screener**: Highlights high-risk symptoms that warrant immediate hospital care.
        - ✅ **A Grounded Clinical Assistant**: Anchors advice in verified clinical guidelines (WHO, ICMR, NICE) via **RAG**.
        - ✅ **A Preparation Tool**: Synthesizes symptoms, durations, and missing facts so doctor visits are more productive.

        #### What MediGuide AI IS NOT:
        - ❌ **NOT a Diagnostic Device**: It does not establish clinical diagnoses or disease certainty.
        - ❌ **NOT an e-Prescription System**: It never recommends prescription drug dosages or modifications.
        - ❌ **NOT an Automatic Emergency Dispatcher**: It does not contact 112/911 automatically; patients must call.
        - ❌ **NOT a Substitute for Clinical Judgment**: Every assessment explicitly states that a licensed physician must be consulted.
        """
    )

with tab2:
    st.markdown("### 🛡️ Dual-Layer & RAG Architecture")
    st.markdown(
        """
        To eliminate generative AI hallucinations in medical settings,
        MediGuide AI implements a **Dual-Layer Guardrail Architecture with RAG Protocol Grounding**:
        """
    )

    scol1, scol2 = st.columns(2)
    with scol1:
        st.markdown(
            """
            <div class="mg-card" style="border-top: 4px solid #ef4444;">
                <div class="mg-card-header" style="color: #991b1b;">Layer 1: Deterministic Safety Engine</div>
                <p style="font-size: 0.9rem; color: #334155;">
                    • Executes <b>prior to and independently of</b> any LLM invocation.<br>
                    • Evaluates conservative regex rule catalogs grounded in emergency triage protocols (Manchester Triage, NHS 111, WHO).<br>
                    • Evaluates neonatal fever (<28 days), pediatric respiratory signs, geriatric atypical presentations (65+), and obstetric emergencies.<br>
                    • Overrides routine advice with immediate localized emergency hotline instructions (112, 108 / 102).
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with scol2:
        st.markdown(
            """
            <div class="mg-card" style="border-top: 4px solid #0d9488;">
                <div class="mg-card-header" style="color: #0f766e;">Layer 2: Grounded Clinical RAG & Neural Core</div>
                <p style="font-size: 0.9rem; color: #334155;">
                    • Vector retrieval over verified clinical guidelines (ICMR, WHO, NICE, CDC).<br>
                    • Injects matched clinical protocols into prompt context to prevent hallucination.<br>
                    • Strict <b>Pydantic</b> JSON schema enforcement.<br>
                    • Low temperature (0.2) to prevent creative drift.<br>
                    • Local deterministic fallback engine when network is degraded.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

with tab3:
    st.markdown("### 🔒 Privacy & Data Retention Policy")
    st.markdown(
        """
        - **Zero Personal Identifiers**: MediGuide AI does not request or store patient names, phone numbers, email addresses, or IP addresses.
        - **Optional Session Persistence**: Sessions are only saved to the database if the user explicitly checks the persistence checkbox.
        - **Parameterized SQL**: All database operations use SQLite parameterized queries to prevent SQL injection vulnerabilities.
        - **Ephemeral Cloud Hosting**: On Streamlit Community Cloud, local SQLite records exist only within the ephemeral container session.
        - **External API Boundaries**: Only symptom narrative text and broad demographic context (age bracket) are sent to the inference endpoint. Geocoding queries only transmit the user-entered city or locality, not precise user GPS telemetry.
        """
    )

with tab4:
    st.markdown("### ⚖️ Regulatory Pathways & Medical Ethics")
    st.markdown(
        """
        Before any software of this nature can be deployed for clinical care in hospital or patient populations,
        the following rigorous prerequisites must be met:

        1. **Software as a Medical Device (SaMD) Review**:
           - **India**: Medical Device Rules (CDSCO) compliance for clinical decision support.
           - **US**: FDA 510(k) or De Novo clearance under Digital Health Guidance.
           - **EU**: EU MDR (Medical Device Regulation 2017/745) Class IIa certification.
        2. **Clinical Validation Trials**:
           - Multi-center prospective clinical concordance studies comparing system triage recommendations against board-certified emergency physicians.
        3. **Continuous Adverse Event Monitoring**:
           - Formal post-market surveillance system to detect and review near-miss triage classifications.
        4. **Compliance & Privacy Frameworks**:
           - Full compliance with HIPAA (Health Insurance Portability and Accountability Act) and GDPR (General Data Protection Regulation).
        """
    )

st.markdown("---")
st.caption(
    "MediGuide AI is an academic portfolio and research project demonstrating human-centered AI design, "
    "safety-critical rule engines, RAG protocol grounding, and OpenStreetMap healthcare integration."
)

"""
MediGuide AI — Patient Session History & Clinical Export Page.
Allows review, management, and multilingual export of stored symptom assessment records.
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
    page_title="Consultation History — MediGuide AI",
    page_icon="📂",
    layout="wide"
)

from src.ui_components import apply_theme, render_sidebar, render_triage_badge
from src.auth import is_admin
from src.database import (
    get_all_sessions,
    get_session_by_id,
    delete_session,
    clear_all_sessions,
    get_session_count
)
from src.report_generator import generate_pdf_report, generate_html_clinical_summary, generate_csv_export

apply_theme()
render_sidebar()

all_sessions = get_all_sessions()
active_id = st.session_state.get("active_patient_id", "MG-2026-01")

if is_admin():
    st.title("📂 Hospital Master Consultation Audit (Clinician Access)")
    st.markdown(
        "Institutional review of all patient consultations, triage records, and clinical logs across the hospital."
    )
    sessions = all_sessions
else:
    st.title("📂 My Consultation History & Records")
    st.markdown(
        f"Review your personal clinical consultations recorded for Patient ID **{active_id}**. "
        f"Download doctor-ready reports and review past triage recommendations."
    )
    sessions = [s for s in all_sessions if s.get("patient_id") == active_id]

total_count = len(sessions)

# Top Bar / Controls
if is_admin():
    mcol1, mcol2, mcol3, mcol4 = st.columns([2.5, 2, 1.5, 1.2])
    with mcol1:
        st.markdown(f"### Total Hospital Records: **{total_count}**")
    with mcol2:
        st.page_link("pages/4_Patient_Portal.py", label="🔍 Master Patient Lookup →", icon="🗂️")
    with mcol3:
        if total_count > 0:
            csv_data = generate_csv_export(sessions)
            st.download_button(
                label="📥 Export Master CSV",
                data=csv_data,
                file_name=f"MediGuide_Master_Audit_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    with mcol4:
        if total_count > 0:
            if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                clear_all_sessions()
                st.success("All master session records deleted.")
                st.rerun()
else:
    pcol1, pcol2 = st.columns([3.5, 1.5])
    with pcol1:
        st.markdown(f"### Consultations for Patient **{active_id}**: **{total_count}**")
    with pcol2:
        st.page_link("pages/4_Patient_Portal.py", label="🗂️ View Complete Health Dossier →", icon="👤")

st.markdown("---")

if total_count == 0:
    if is_admin():
        st.info("No assessment sessions are currently stored in the hospital database.")
        st.page_link("pages/1_Symptom_Assistant.py", label="Run Intake Assessment →", icon="🩺")
    else:
        st.info(
            f"No consultation history found under your Patient ID: **{active_id}**. "
            "Complete a symptom check on the **Symptom Assistant** page to automatically save your evaluation."
        )
        st.page_link("pages/1_Symptom_Assistant.py", label="Start My Clinical Assessment →", icon="🩺")
else:
    for sess in sessions:
        sid = sess["session_id"]
        p_name = sess.get("patient_name", "Registered Patient")
        p_id = sess.get("patient_id", "MG-2026-0001")
        p_gender = sess.get("gender", "Male")
        p_blood = sess.get("blood_group", "Unknown")
        created = sess["created_at"]
        triage = sess["triage_level"]
        specialty = sess["suggested_specialty"]
        symptoms = sess["symptoms_text"]
        age_raw = str(sess.get("age_group", "Adult"))
        clean_age = age_raw.split("(")[0].strip()
        if clean_age.isdigit():
            clean_age = f"{clean_age} yrs"
        dur = sess["duration"]
        sev = sess["severity"]
        country = sess.get("country", "India")
        lang = sess.get("language", "English")

        with st.container():
            st.markdown(
                f"""
                <div class="mg-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                        <div>
                            <span style="font-weight:700; font-size:1.1rem; color:#0f172a;">👤 {p_name}</span>
                            <span style="background:#e0f2fe; color:#0284c7; font-weight:bold; font-size:0.85rem; padding:2px 8px; border-radius:10px; margin-left:8px;">ID: {p_id}</span>
                            <span style="font-size:0.85rem; color:#64748b; margin-left:8px;">({created})</span>
                        </div>
                        {render_triage_badge(triage)}
                    </div>
                    <div style="margin-top:10px; font-size:0.95rem; color:#334155;">
                        <b>Reported Complaint:</b> {symptoms}
                    </div>
                    <div style="margin-top:6px; font-size:0.85rem; color:#64748b;">
                        <b>Context:</b> {p_gender} | Blood: {p_blood} • Age: {clean_age} • Duration: {dur} • Severity: {sev}/10 • Specialty: <b>{specialty}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Actions row for this session
            act1, act2, act3, act4 = st.columns([2, 2, 2, 1.2])
            with act1:
                pdf_bytes = generate_pdf_report(sess, target_language=lang)
                st.download_button(
                    label=f"📄 PDF Summary ({lang})",
                    data=pdf_bytes,
                    file_name=f"MediGuide_{p_name.replace(' ', '_')}_{sid}.pdf",
                    mime="application/pdf",
                    key=f"pdf_btn_{sid}",
                    use_container_width=True
                )
            with act2:
                html_summary = generate_html_clinical_summary(sess, target_language=lang)
                st.download_button(
                    label=f"🌐 Printable HTML ({lang})",
                    data=html_summary.encode("utf-8"),
                    file_name=f"MediGuide_Printable_{sid}.html",
                    mime="text/html",
                    key=f"html_btn_{sid}",
                    use_container_width=True
                )
            with act3:
                if st.button(f"📍 Find {specialty} Nearby", key=f"fnd_btn_{sid}", use_container_width=True):
                    st.session_state["target_specialty"] = specialty
                    st.session_state["specialty_from_assistant"] = True
                    st.session_state["target_patient_name"] = p_name
                    st.switch_page("pages/2_Find_Doctors.py")
            with act4:
                if st.button(f"🗑️ Delete", key=f"del_btn_{sid}", use_container_width=True):
                    delete_session(sid)
                    st.success(f"Session #{sid} deleted.")
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

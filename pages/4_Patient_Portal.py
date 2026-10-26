"""
# MediGuide AI — Patient Health Records & Longitudinal Medical History Portal (RBAC Protected).
Allows patients and physicians to look up medical records by Patient ID,
review chronological clinical consultations, and download complete health dossiers.
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
    page_title="Patient Portal & EHR Records — MediGuide AI",
    page_icon="🗂️",
    layout="wide"
)

from src.ui_components import (
    apply_theme,
    render_sidebar,
    render_triage_badge,
    render_top_portal_bar
)
from src.auth import is_admin
from src.database import (
    get_patient_history,
    get_all_patient_ids,
    get_all_sessions,
    delete_session
)
from src.report_generator import (
    generate_pdf_report,
    generate_html_clinical_summary,
    generate_consolidated_patient_dossier_pdf
)

apply_theme()
render_sidebar()
render_top_portal_bar()

# Page Header
if is_admin():
    st.title("🗂️ Hospital Master EHR Registry (Clinician Access)")
    st.markdown(
        "Master clinical administration portal with institutional access to all patient records, "
        "longitudinal health timelines, and consolidated medical dossier exports."
    )
else:
    st.title("🗂️ Patient Health Records & Longitudinal Dossier")
    st.markdown(
        "Securely view your clinical consultation history, review prior triage assessments, "
        "and download your consolidated medical dossier."
    )

# Registered Patient IDs lookup
registered_ids = get_all_patient_ids()

if is_admin():
    # Admin View: Full search + Master patient dropdown
    scol1, scol2 = st.columns([3, 2])
    with scol1:
        search_id = st.text_input(
            "Search Patient ID:",
            value=st.session_state.get("active_patient_id", registered_ids[0] if registered_ids else "MG-2026-01"),
            placeholder="e.g. MG-2026-01"
        )
    with scol2:
        if registered_ids:
            quick_id = st.selectbox("Select from Hospital Patient Directory:", registered_ids, index=0)
            if st.button("Load Patient Record", use_container_width=True):
                search_id = quick_id
                st.session_state["active_patient_id"] = quick_id
                st.rerun()
else:
    # Individual Patient View: Private self-service only
    pcol1, pcol2 = st.columns([4, 1.2])
    with pcol1:
        default_patient_id = st.session_state.get("active_patient_id", "MG-2026-01")
        search_id = st.text_input(
            "Enter Your Patient ID:",
            value=default_patient_id,
            placeholder="e.g. MG-2026-01",
            help="Your private Patient ID assigned during your clinical intake."
        )
    with pcol2:
        st.write("")
        st.write("")
        if st.button("🔍 Fetch Record", type="primary", use_container_width=True):
            st.session_state["active_patient_id"] = search_id
            st.rerun()

    st.caption("🔒 **Patient Privacy Guard Active:** Individual health records are strictly private. Hospital clinicians can access the master registry via Profile & Staff Access above.")

st.markdown("---")

if not search_id:
    st.info("Please enter or select a Patient ID to view historical medical records.")
else:
    # Query database for this Patient ID
    patient_records = get_patient_history(search_id)

    if not patient_records:
        st.warning(f"No consultation history found for Patient ID: **{search_id}**.")
        st.markdown(
            """
            **How to create your health record:**
            1. Go to the **Symptom Assistant** page.
            2. Enter your Name, Age, and Symptoms.
            3. Use or generate a Patient ID and check *'Save this assessment to local SQLite history'*.
            """
        )
        st.page_link("pages/1_Symptom_Assistant.py", label="Start New Assessment with this ID →", icon="🩺")
    else:
        # Patient Profile Card
        latest = patient_records[0]
        p_name = latest.get("patient_name", "Registered Patient")
        p_gender = latest.get("gender", "Male")
        p_blood = latest.get("blood_group", "Unknown")
        p_age_raw = str(latest.get("age_group", "Adult"))
        import re
        p_age = re.sub(r'\(.*?\)', '', p_age_raw).strip() or p_age_raw
        p_country = latest.get("country", "India")
        p_lang = latest.get("language", "English")

        st.session_state.active_patient_name = p_name
        st.session_state.active_patient_id = search_id

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #f0fdfa 0%, #e6fffa 100%); border: 2px solid #0d9488; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(13, 148, 136, 0.08);">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                    <div>
                        <div style="font-size: 1.4rem; font-weight: 800; color: #0f766e;">👤 {p_name}</div>
                        <div style="font-size: 0.95rem; color: #0284c7; font-weight: 700; margin-top:2px;">Patient ID: {search_id}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:#0d9488; color:white; font-size:0.85rem; font-weight:bold; padding:4px 12px; border-radius:16px;">Active Health Dossier</span>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:12px; margin-top:16px; padding-top:14px; border-top:1px solid #ccfbf1; font-size:0.9rem; color:#334155;">
                    <div><b>Age:</b> {p_age if ('yr' in p_age.lower() or not p_age.isdigit()) else f'{p_age} yrs'}</div>
                    <div><b>Gender:</b> {p_gender}</div>
                    <div><b>Blood Group:</b> <span style="color:#b91c1c; font-weight:bold;">{p_blood}</span></div>
                    <div><b>Region:</b> {p_country}</div>
                    <div><b>Total Consultations:</b> <b>{len(patient_records)}</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Summary Metrics Row
        total_visits = len(patient_records)
        emergencies = sum(1 for r in patient_records if r.get("triage_level") == "EMERGENCY")
        urgents = sum(1 for r in patient_records if r.get("triage_level") == "URGENT")
        routines = sum(1 for r in patient_records if r.get("triage_level") in ("ROUTINE", "SELF_CARE"))

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.metric("Total Medical Consultations", f"{total_visits}")
        with mcol2:
            st.metric("Emergency Escalations", f"{emergencies}")
        with mcol3:
            st.metric("Urgent Care Visits", f"{urgents}")
        with mcol4:
            st.metric("Routine Outpatient Checkups", f"{routines}")

        st.markdown("---")

        # Dossier Download Action Bar
        dcol1, dcol2 = st.columns([2, 1])
        with dcol1:
            st.markdown("### 📜 Longitudinal Consultation Timeline")
            st.caption(f"Chronological record of all evaluations for Patient {p_name} ({search_id}).")
        with dcol2:
            dossier_pdf = generate_consolidated_patient_dossier_pdf(search_id, patient_records)
            st.download_button(
                label=f"📥 Download Full Medical Dossier (PDF)",
                data=dossier_pdf,
                file_name=f"MediGuide_Medical_Dossier_{search_id}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        # Timeline entries
        for idx, rec in enumerate(patient_records):
            sid = rec.get("session_id")
            created = rec.get("created_at")
            triage = rec.get("triage_level", "ROUTINE")
            specialty = rec.get("suggested_specialty", "General Physician")
            symptoms = rec.get("symptoms_text", "")
            duration = rec.get("duration", "N/A")
            severity = rec.get("severity", 3)
            notes = rec.get("notes", "")

            with st.container():
                st.markdown(
                    f"""
                    <div class="mg-card" style="border-left: 5px solid {'#ef4444' if triage=='EMERGENCY' else ('#f97316' if triage=='URGENT' else '#0d9488')};">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                            <div>
                                <span style="font-weight:700; font-size:1.05rem; color:#0f172a;">Consultation #{sid} — {created}</span>
                                <div style="font-size:0.84rem; color:#64748b; margin-top:2px;">Specialty Navigated: <b>{specialty}</b> • Duration: {duration} • Severity: {severity}/10</div>
                            </div>
                            {render_triage_badge(triage)}
                        </div>
                        <div style="margin-top:12px; font-size:0.95rem; color:#1e293b; background:#f8fafc; padding:10px 14px; border-radius:6px; border:1px solid #e2e8f0;">
                            <b>Reported Complaint:</b> {symptoms}
                        </div>
                        {f'<div style="margin-top:8px; font-size:0.85rem; color:#475569;"><b>Clinical Notes:</b> {notes}</div>' if notes else ''}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Individual download and management actions
                bcol1, bcol2, bcol3, bcol4 = st.columns([2, 2, 1.5, 2.5])
                with bcol1:
                    pdf_bytes = generate_pdf_report(rec, target_language=p_lang)
                    st.download_button(
                        label=f"📄 PDF Summary (#{sid})",
                        data=pdf_bytes,
                        file_name=f"Consultation_{search_id}_{sid}.pdf",
                        mime="application/pdf",
                        key=f"d_pdf_{sid}",
                        use_container_width=True
                    )
                with bcol2:
                    html_summary = generate_html_clinical_summary(rec, target_language=p_lang)
                    st.download_button(
                        label=f"🌐 Printable HTML (#{sid})",
                        data=html_summary.encode("utf-8"),
                        file_name=f"Consultation_{search_id}_{sid}.html",
                        mime="text/html",
                        key=f"d_html_{sid}",
                        use_container_width=True
                    )
                with bcol3:
                    if st.button(f"🗑️ Delete", key=f"d_del_{sid}", use_container_width=True):
                        delete_session(sid)
                        st.success(f"Record #{sid} deleted.")
                        st.rerun()
                with bcol4:
                    if st.button(f"📍 Find {specialty} Near Me", key=f"d_find_{sid}", use_container_width=True):
                        st.session_state["target_specialty"] = specialty
                        st.session_state["specialty_from_assistant"] = True
                        st.switch_page("pages/2_Find_Doctors.py")

                st.markdown("<br>", unsafe_allow_html=True)

"""
Multilingual Clinical Report Generation Module for MediGuide AI.
Produces individualized clinical summaries in PDF (via ReportLab),
consolidated longitudinal patient medical dossiers,
and responsive multilingual HTML print summaries.
Includes prominent Patient Name, Patient ID, Age, Gender, and Blood Group.
"""

import io
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Multilingual Vocabulary Dictionary
LOCALIZED_TERMS: Dict[str, Dict[str, str]] = {
    "English": {
        "title": "MediGuide AI — Clinical Care Navigation Summary",
        "subtitle": "Certified Health Triage & Doctor Consultation Preparation",
        "meta_patient_name": "Patient Name",
        "meta_patient_id": "Patient ID (EHR)",
        "meta_gender_blood": "Gender / Blood Group",
        "meta_generated": "Consultation Date",
        "meta_urgency": "Triage Urgency",
        "meta_age": "Patient Age",
        "meta_duration": "Duration",
        "meta_severity": "Reported Severity",
        "meta_specialty": "Suggested Specialty",
        "meta_country": "Country Context",
        "sec_complaint": "1. Patient-Reported Complaint",
        "sec_action": "2. Recommended Clinical Action Plan",
        "sec_possibilities": "3. Potential Health Explanations (Non-Diagnostic)",
        "sec_guidance": "4. Supportive Care & Comfort Measures",
        "sec_warnings": "5. Critical Warning Signs (Seek Emergency Care If Present)",
        "sec_notes": "6. Clinical Notes for Physician Review",
        "sec_rag": "7. Grounded Clinical Practice Guidelines (RAG)",
        "disclaimer_title": "CLINICAL DISCLAIMER",
        "disclaimer_text": (
            "MediGuide AI is an educational clinical decision-support and care navigation tool. "
            "It does NOT provide medical diagnoses, clinical decisions, prescriptions, or treatment plans. "
            "In case of a medical emergency, call local emergency services immediately or proceed to the nearest hospital."
        )
    },
    "Hindi (हिन्दी)": {
        "title": "मेडीगाइड एआई — क्लिनिकल स्वास्थ्य मार्गदर्शन सारांश (MediGuide AI)",
        "subtitle": "प्रमाणित स्वास्थ्य ट्राइएज एवं डॉक्टर परामर्श तैयारी रिपोर्ट",
        "meta_patient_name": "मरीज़ का नाम (Patient Name)",
        "meta_patient_id": "मरीज़ आईडी (Patient ID)",
        "meta_gender_blood": "लिंग / ब्लड ग्रुप (Gender/Blood)",
        "meta_generated": "परामर्श तिथि (Date)",
        "meta_urgency": "प्राथमिकता स्तर (Urgency)",
        "meta_age": "मरीज़ की उम्र (Age)",
        "meta_duration": "लक्षण अवधि (Duration)",
        "meta_severity": "दर्द / गंभीरता (Severity)",
        "meta_specialty": "अनुशंसित विशेषज्ञ (Specialty)",
        "meta_country": "देश / क्षेत्र (Country)",
        "sec_complaint": "1. मरीज़ द्वारा बताए गए लक्षण (Reported Complaint)",
        "sec_action": "2. अनुशंसित क्लिनिकल कदम (Recommended Next Step)",
        "sec_possibilities": "3. सामान्य संभावित कारण (Non-Diagnostic Possibilities)",
        "sec_guidance": "4. सामान्य देखभाल एवं राहत के उपाय (Self-Care Guidance)",
        "sec_warnings": "5. आपातकालीन खतरे के संकेत (Red Flag Warning Signs)",
        "sec_notes": "6. डॉक्टर से परामर्श हेतु नोट्स (Doctor Consultation Notes)",
        "sec_rag": "7. आधारित क्लिनिकल प्रोटोकॉल (Clinical Guidelines RAG)",
        "disclaimer_title": "चिकित्सीय अस्वीकरण (CLINICAL DISCLAIMER)",
        "disclaimer_text": (
            "मेडीगाइड एआई केवल स्वास्थ्य मार्गदर्शन एवं शैक्षणिक सहायता के लिए है। "
            "यह कोई चिकित्सीय निदान (Diagnosis) या दवा की पर्ची प्रदान नहीं करता है। "
            "किसी भी गंभीर लक्षण की स्थिति में तुरंत आपातकालीन नंबर 112 / अस्पताल से संपर्क करें।"
        )
    },
    "Bengali (বাংলা)": {
        "title": "মেডিগাইড এআই — ক্লিনিক্যাল স্বাস্থ্য মূল্যায়ন ও পরামর্শ রিপোর্ট",
        "subtitle": "স্বাস্থ্য ট্রায়াজ ও ডাক্তার পরামর্শ প্রস্তুতি সামারি",
        "meta_patient_name": "রোগীর নাম (Patient Name)",
        "meta_patient_id": "রোগীর আইডি (Patient ID)",
        "meta_gender_blood": "লিঙ্গ / ব্লাড গ্রুপ (Gender/Blood)",
        "meta_generated": "পরামর্শের তারিখ (Date)",
        "meta_urgency": "জরুরি মাত্রা (Urgency Level)",
        "meta_age": "বয়স (Age)",
        "meta_duration": "লক্ষণ স্থায়িত্ব (Duration)",
        "meta_severity": "তীব্রতা স্কেল (Severity)",
        "meta_specialty": "প্রস্তাবিত বিশেষজ্ঞ (Specialty)",
        "meta_country": "অঞ্চল / দেশ (Country)",
        "sec_complaint": "১. রোগীর বর্ণিত লক্ষণসমূহ (Symptoms)",
        "sec_action": "২. প্রস্তাবিত ক্লিনিক্যাল পদক্ষেপ (Action Plan)",
        "sec_possibilities": "৩. সম্ভাব্য সাধারণ কারণসমূহ (Possibilities)",
        "sec_guidance": "৪. সহায়ক প্রাথমিক যত্ন ও সতর্কতা (Care Guidance)",
        "sec_warnings": "৫. আশঙ্কাজনক বিপদের লক্ষণ (Red Flag Warnings)",
        "sec_notes": "৬. চিকিৎসকের পর্যালোচনার নোট (Doctor Notes)",
        "sec_rag": "৭. ক্লিনিক্যাল নির্দেশিকা রেফারেন্স (RAG Protocols)",
        "disclaimer_title": "ক্লিনিক্যাল সতর্কতা (DISCLAIMER)",
        "disclaimer_text": (
            "মেডিগাইড এআই শুধুমাত্র স্বাস্থ্য শিক্ষা ও প্রাথমিক দিকনির্দেশনার জন্য। "
            "এটি কোনো রোগ নির্ণয় বা ঔষধ ব্যবস্থাপত্র নয়। যেকোনো জরুরি অবস্থায় অবিলম্বে ১১২ নম্বরে কল করুন।"
        )
    },
    "Tamil (தமிழ்)": {
        "title": "மெடிகைட் ஏஐ — மருத்துவ மதிப்பீடு மற்றும் வழிகாட்டுதல் அறிக்கை",
        "subtitle": "முழுமையான சுகாதார நிலை மற்றும் மருத்துவர் ஆலோசனை தயார்நிலை சுருக்கம்",
        "meta_patient_name": "நோயாளி பெயர் (Patient Name)",
        "meta_patient_id": "நோயாளி அடையாள எண் (Patient ID)",
        "meta_gender_blood": "பாலினம் / இரத்த வகை (Gender/Blood)",
        "meta_generated": "தேதி (Consultation Date)",
        "meta_urgency": "அவசர நிலை (Triage Level)",
        "meta_age": "வயது (Patient Age)",
        "meta_duration": "கால அளவு (Duration)",
        "meta_severity": "தீவிரத்தன்மை (Severity Scale)",
        "meta_specialty": "பரிந்துரைக்கப்பட்ட சிறப்பு மருத்துவர் (Specialty)",
        "meta_country": "நாடு / பகுதி (Region)",
        "sec_complaint": "1. அறிகுறிகளின் சுருக்கம் (Reported Symptoms)",
        "sec_action": "2. பரிந்துரைக்கப்பட்ட மருத்துவ நடவடிக்கைகள் (Action Plan)",
        "sec_possibilities": "3. சாத்தியமான காரணங்கள் (Possibilities)",
        "sec_guidance": "4. முதலுதவி மற்றும் பராமரிப்பு குறிப்புகள் (Care Guidance)",
        "sec_warnings": "5. அவசர எச்சரிக்கை அறிகுறிகள் (Red Flag Warnings)",
        "sec_notes": "6. மருத்துவ ஆலோசனைக்கான குறிப்புகள் (Clinical Notes)",
        "sec_rag": "7. மருத்துவ நெறிமுறைகள் (RAG Clinical Protocols)",
        "disclaimer_title": "மருத்துவ பொறுப்புத்துறப்பு (DISCLAIMER)",
        "disclaimer_text": (
            "மெடிகைட் ஏஐ என்பது கல்வி மற்றும் வழிகாட்டுதலுக்கான தளமாகும். "
            "இது நேரடி நோயறிதல் அல்லது மருந்து சீட்டு அல்ல. அவசர காலங்களில் 112 என்ற எண்ணை உடனடியாக அழைக்கவும்."
        )
    },
    "Telugu (తెలుగు)": {
        "title": "మెడిగైడ్ ఏఐ — క్లినికల్ హెల్త్ నావిగేషన్ సారాంశం",
        "subtitle": "ఆరోగ్య ట్రయాజ్ & డాక్టర్ సంప్రదింపు సన్నాహక నివేదిక",
        "meta_patient_name": "రోగి పేరు (Patient Name)",
        "meta_patient_id": "రోగి ఐడి (Patient ID)",
        "meta_gender_blood": "లింగం / రక్త గ్రూపు (Gender/Blood)",
        "meta_generated": "తేదీ (Consultation Date)",
        "meta_urgency": "అత్యవసర స్థాయి (Triage Urgency)",
        "meta_age": "వయస్సు (Patient Age)",
        "meta_duration": "వ్యవధి (Duration)",
        "meta_severity": "తీవ్రత (Severity)",
        "meta_specialty": "సిఫార్సు చేయబడిన నిపుణుడు (Specialty)",
        "meta_country": "ప్రాంతం (Country)",
        "sec_complaint": "1. రోగి తెలిపిన లక్షణాలు (Reported Symptoms)",
        "sec_action": "2. సిఫార్సు చేయబడిన తదుపరి చర్య (Action Plan)",
        "sec_possibilities": "3. సంభావ్య కారణాలు (Non-Diagnostic Explanations)",
        "sec_guidance": "4. సాధారణ స్వీయ సంరక్షణ సూచనలు (Self-Care Guidance)",
        "sec_warnings": "5. అత్యవసర హెచ్చరిక సంకేతాలు (Red Flags)",
        "sec_notes": "6. వైద్యుడి సమీక్ష కోసం గమనికలు (Doctor Notes)",
        "sec_rag": "7. క్లినికల్ ప్రాక్టీస్ ప్రోటోకాల్స్ (RAG Protocols)",
        "disclaimer_title": "క్లినికల్ నిరాకరణ (DISCLAIMER)",
        "disclaimer_text": (
            "మెడిగైడ్ ఏఐ విద్యా మరియు ఆరోగ్య నావిగేషన్ కోసం మాత్రమే. "
            "ఇది వైద్య నిర్ధారణ లేదా ప్రిస్క్రిప్షన్ కాదు. అత్యవసర పరిస్థితుల్లో వెంటనే 112 కు కాల్ చేయండి."
        )
    }
}


def get_term(lang: str, key: str) -> str:
    """Retrieve translated string with fallback to English."""
    lang_dict = LOCALIZED_TERMS.get(lang, LOCALIZED_TERMS["English"])
    return lang_dict.get(key, LOCALIZED_TERMS["English"].get(key, key))


def generate_pdf_report(session_data: Dict, target_language: str = "English") -> bytes:
    """
    Generate an individualized clinical summary PDF featuring Patient Name and Patient ID.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f766e')
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#475569')
    )

    heading2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=7,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        leftIndent=14,
        textColor=colors.HexColor('#334155')
    )

    disclaimer_style = ParagraphStyle(
        'DocDisclaimer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#64748b')
    )

    caption_style = ParagraphStyle(
        'DocCaption',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#334155')
    )

    elements = []

    # Title & Subtitle
    doc_title = get_term(target_language, "title")
    doc_subtitle = get_term(target_language, "subtitle")
    elements.append(Paragraph(doc_title, title_style))
    elements.append(Paragraph(doc_subtitle, subtitle_style))
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d9488'), spaceBefore=2, spaceAfter=6))

    # Patient Identification Box
    p_name = session_data.get("patient_name", "Registered Patient")
    p_id = session_data.get("patient_id", "MG-2026-0001")
    p_gender = session_data.get("gender", "Male")
    p_blood = session_data.get("blood_group", "Unknown")

    triage_level = session_data.get("triage_level", "ROUTINE")
    triage_color = colors.HexColor('#166534')
    if triage_level == "EMERGENCY":
        triage_color = colors.HexColor('#991b1b')
    elif triage_level == "URGENT":
        triage_color = colors.HexColor('#9a3412')

    # Parse Assessment JSON first
    assessment_data = {}
    if "assessment_json" in session_data and session_data["assessment_json"]:
        try:
            if isinstance(session_data["assessment_json"], dict):
                assessment_data = session_data["assessment_json"]
            else:
                assessment_data = json.loads(session_data["assessment_json"])
        except Exception:
            assessment_data = {}

    # Clean age display (never repeat '18-64 years' or double brackets)
    exact_age = session_data.get("exact_age")
    age_raw = str(session_data.get("age_group", "Adult"))
    clean_cat = re.sub(r'\(.*?\)', '', age_raw).replace("yrs", "").strip()
    if exact_age is not None:
        age_display = f"{exact_age} yrs"
        if clean_cat and clean_cat.lower() not in ["adult", str(exact_age)]:
            age_display += f" ({clean_cat})"
    else:
        age_display = f"{clean_cat} yrs" if clean_cat.isdigit() else (clean_cat or "Adult")

    meta_data = [
        [
            Paragraph(f"<b>{get_term(target_language, 'meta_patient_name')}:</b> <font color='#0f766e'><b>{p_name}</b></font>", body_style),
            Paragraph(f"<b>{get_term(target_language, 'meta_patient_id')}:</b> <font color='#0284c7'><b>{p_id}</b></font>", body_style)
        ],
        [
            Paragraph(f"<b>{get_term(target_language, 'meta_gender_blood')}:</b> {p_gender} | {p_blood}", body_style),
            Paragraph(f"<b>{get_term(target_language, 'meta_urgency')}:</b> <font color='{triage_color.hexval()}'><b>{triage_level}</b></font>", body_style)
        ],
        [
            Paragraph(f"<b>{get_term(target_language, 'meta_generated')}:</b> {session_data.get('created_at', 'N/A')}", body_style),
            Paragraph(f"<b>{get_term(target_language, 'meta_age')}:</b> {age_display} • <b>Duration:</b> {session_data.get('duration', 'N/A')}", body_style)
        ],
        [
            Paragraph(f"<b>{get_term(target_language, 'meta_specialty')}:</b> {session_data.get('suggested_specialty', 'General Physician')}", body_style),
            Paragraph(f"<b>{get_term(target_language, 'meta_country')}:</b> {session_data.get('country', 'India 🇮🇳')} ({target_language})", body_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(meta_table)

    # Prominent RAG Guidelines Banner on Page 1
    protocols = assessment_data.get("retrieved_protocols", [])
    if protocols:
        prot_names = " • ".join([f"<b>{p.get('source', 'Clinical')}</b>: {p.get('title', '')}" for p in protocols[:2]])
        rag_banner = [
            [Paragraph(f"<font color='#0f766e'><b>📚 Certified Guidelines Grounding (RAG Active):</b></font> {prot_names}", caption_style)]
        ]
        rag_table = Table(rag_banner, colWidths=[540])
        rag_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fdfa')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#99f6e4')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(Spacer(1, 4))
        elements.append(rag_table)

    elements.append(Spacer(1, 6))

    # 1. Reported Complaint
    elements.append(Paragraph(get_term(target_language, "sec_complaint"), heading2_style))
    elements.append(Paragraph(str(session_data.get("symptoms_text", "")), body_style))
    elements.append(Spacer(1, 6))

    # 2. Recommended Next Steps
    rec_step = session_data.get("recommended_action") or assessment_data.get("recommended_next_step", "Consult a physician.")
    elements.append(Paragraph(get_term(target_language, "sec_action"), heading2_style))
    elements.append(Paragraph(f"<b>Action Plan:</b> {rec_step}", body_style))
    elements.append(Spacer(1, 6))

    # 3. Possible Explanations
    possibilities = assessment_data.get("possible_explanations", [])
    if possibilities:
        elements.append(Paragraph(get_term(target_language, "sec_possibilities"), heading2_style))
        for p in possibilities:
            elements.append(Paragraph(f"• {p}", bullet_style))
        elements.append(Spacer(1, 6))

    # 4. Supportive Guidance
    guidance = assessment_data.get("general_guidance", [])
    if guidance:
        elements.append(Paragraph(get_term(target_language, "sec_guidance"), heading2_style))
        for g in guidance:
            elements.append(Paragraph(f"• {g}", bullet_style))
        elements.append(Spacer(1, 6))

    # 5. Warning Signs
    warnings = assessment_data.get("warning_signs", [])
    if warnings:
        elements.append(Paragraph(get_term(target_language, "sec_warnings"), heading2_style))
        for w in warnings:
            elements.append(Paragraph(f"<font color='#dc2626'><b>!</b></font> {w}", bullet_style))
        elements.append(Spacer(1, 6))

    # 6. RAG Protocols
    protocols = assessment_data.get("retrieved_protocols", [])
    if protocols:
        elements.append(Paragraph(get_term(target_language, "sec_rag"), heading2_style))
        for pr in protocols:
            elements.append(Paragraph(f"• <b>{pr.get('title', '')}</b> ({pr.get('source', '')})", bullet_style))
        elements.append(Spacer(1, 6))

    # 7. Notes
    notes = session_data.get("notes")
    if notes:
        elements.append(Paragraph(get_term(target_language, "sec_notes"), heading2_style))
        elements.append(Paragraph(str(notes), body_style))
        elements.append(Spacer(1, 6))

    # Disclaimer Footer
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#94a3b8'), spaceBefore=2, spaceAfter=4))
    elements.append(Paragraph(f"<b>{get_term(target_language, 'disclaimer_title')}:</b> {get_term(target_language, 'disclaimer_text')}", disclaimer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_consolidated_patient_dossier_pdf(patient_id: str, sessions: List[Dict]) -> bytes:
    """
    Generate a comprehensive longitudinal medical dossier PDF bundling ALL consultations of a patient.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#0f766e'))
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#0f172a'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#1e293b'))

    elements = []

    # Cover Banner
    p_name = sessions[0].get("patient_name", "Patient") if sessions else "Patient"
    elements.append(Paragraph("MediGuide AI — Consolidated Electronic Health Dossier", title_style))
    elements.append(Paragraph(f"Longitudinal Medical Consultation History for Patient: <b>{p_name}</b> (ID: <b>{patient_id}</b>)", h2_style))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0d9488'), spaceBefore=2, spaceAfter=8))

    elements.append(Paragraph(f"<b>Total Historical Consultations Recorded:</b> {len(sessions)}", body_style))
    elements.append(Spacer(1, 10))

    # Iterate through all consultations
    for idx, s in enumerate(sessions):
        sid = s.get("session_id", idx + 1)
        created = s.get("created_at", "N/A")
        triage = s.get("triage_level", "ROUTINE")
        spec = s.get("suggested_specialty", "General Physician")
        complaint = s.get("symptoms_text", "")

        triage_color = "#991b1b" if triage == "EMERGENCY" else ("#9a3412" if triage == "URGENT" else "#166534")

        elements.append(Paragraph(f"<b>Consultation #{sid} — {created}</b> | Triage: <font color='{triage_color}'><b>{triage}</b></font> | Specialty: <b>{spec}</b>", h2_style))
        elements.append(Paragraph(f"<b>Complaint:</b> {complaint}", body_style))

        # Check notes
        notes = s.get("notes")
        if notes:
            elements.append(Paragraph(f"<b>Clinical Notes:</b> {notes}", body_style))

        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=8))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>CONFIDENTIAL MEDICAL RECORD:</b> This electronic dossier is generated for authorized patient care and physician clinical review.", body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_html_clinical_summary(session_data: Dict, target_language: str = "English") -> str:
    """
    Generates a responsive, printable HTML clinical summary featuring Patient Name and Patient ID.
    Supports native Devanagari Hindi, Bengali, Spanish, etc.
    """
    triage_level = session_data.get("triage_level", "ROUTINE")
    triage_bg = "#fee2e2" if triage_level == "EMERGENCY" else ("#ffedd5" if triage_level == "URGENT" else "#dcfce7")
    triage_color = "#991b1b" if triage_level == "EMERGENCY" else ("#9a3412" if triage_level == "URGENT" else "#166534")

    p_name = session_data.get("patient_name", "Registered Patient")
    p_id = session_data.get("patient_id", "MG-2026-0001")
    p_gender = session_data.get("gender", "Male")
    p_blood = session_data.get("blood_group", "Unknown")

    assessment_data = {}
    if "assessment_json" in session_data and session_data["assessment_json"]:
        try:
            if isinstance(session_data["assessment_json"], dict):
                assessment_data = session_data["assessment_json"]
            else:
                assessment_data = json.loads(session_data["assessment_json"])
        except Exception:
            assessment_data = {}

    possibilities = assessment_data.get("possible_explanations", [])
    guidance = assessment_data.get("general_guidance", [])
    warnings = assessment_data.get("warning_signs", [])
    protocols = assessment_data.get("retrieved_protocols", [])

    poss_html = "".join([f"<li>{p}</li>" for p in possibilities])
    guid_html = "".join([f"<li>{g}</li>" for g in guidance])
    warn_html = "".join([f"<li style='color:#dc2626;'><b>!</b> {w}</li>" for w in warnings])
    proto_html = "".join([f"<li><b>{p.get('title')}</b> — <i>{p.get('source')}</i></li>" for p in protocols])

    exact_age = session_data.get("exact_age")
    age_raw = str(session_data.get("age_group", "Adult"))
    clean_cat = re.sub(r'\(.*?\)', '', age_raw).replace("yrs", "").strip()
    if exact_age is not None:
        age_display = f"{exact_age} yrs"
        if clean_cat and clean_cat.lower() not in ["adult", str(exact_age)]:
            age_display += f" ({clean_cat})"
    else:
        age_display = f"{clean_cat} yrs" if clean_cat.isdigit() else (clean_cat or "Adult")

    rag_banner_html = ""
    if protocols:
        prot_items = "".join([f"<li style='margin-bottom:6px;'><b>{p.get('title')}</b> ({p.get('source')})<br><span style='color:#475569; font-size:12px;'><i>\"{p.get('content')}\"</i></span></li>" for p in protocols])
        rag_banner_html = f"""
        <div style="background:#f0fdfa; border:1.5px solid #0d9488; border-radius:8px; padding:12px 16px; margin-bottom:18px;">
            <div style="font-weight:bold; color:#0f766e; font-size:14px; margin-bottom:6px;">📚 {get_term(target_language, 'sec_rag')}</div>
            <ul style="margin:0; padding-left:18px; font-size:13px;">{prot_items}</ul>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{get_term(target_language, 'title')} - {p_name} ({p_id})</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #1e293b; max-width: 820px; margin: 30px auto; padding: 24px; }}
  .header {{ border-bottom: 3px solid #0d9488; padding-bottom: 12px; margin-bottom: 20px; }}
  .title {{ font-size: 22px; font-weight: 800; color: #0f766e; margin: 0; }}
  .subtitle {{ font-size: 13px; color: #64748b; margin-top: 4px; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 13px; background: {triage_bg}; color: {triage_color}; }}
  .patient-box {{ background: linear-gradient(135deg, #f0fdfa 0%, #e6fffa 100%); border: 1.5px solid #0d9488; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 14px; }}
  .meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 16px; font-size: 13px; }}
  h3 {{ font-size: 15px; color: #0f172a; margin-top: 18px; margin-bottom: 6px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }}
  ul {{ margin-top: 4px; padding-left: 20px; font-size: 13.5px; }}
  li {{ margin-bottom: 4px; }}
  .disclaimer {{ margin-top: 25px; padding: 12px; background: #fef2f2; border-left: 4px solid #ef4444; font-size: 11.5px; color: #7f1d1d; border-radius: 4px; }}
  @media print {{ body {{ margin: 0; padding: 10px; }} button {{ display: none; }} }}
</style>
</head>
<body>
  <div style="text-align: right; margin-bottom: 12px;">
    <button onclick="window.print()" style="background:#0d9488; color:white; border:none; padding:8px 18px; border-radius:6px; cursor:pointer; font-weight:bold; font-size:14px;">🖨️ Print / Save as PDF</button>
  </div>
  <div class="header">
    <div class="title">{get_term(target_language, 'title')}</div>
    <div class="subtitle">{get_term(target_language, 'subtitle')}</div>
  </div>

  <div class="patient-box">
    <div><b>{get_term(target_language, 'meta_patient_name')}:</b> <span style="color:#0f766e; font-weight:bold; font-size:15px;">{p_name}</span></div>
    <div><b>{get_term(target_language, 'meta_patient_id')}:</b> <span style="color:#0284c7; font-weight:bold; font-size:15px;">{p_id}</span></div>
    <div><b>{get_term(target_language, 'meta_gender_blood')}:</b> {p_gender} | {p_blood}</div>
    <div><b>{get_term(target_language, 'meta_urgency')}:</b> <span class="badge">{triage_level}</span></div>
  </div>

  <div class="meta-grid">
    <div><b>{get_term(target_language, 'meta_generated')}:</b> {session_data.get('created_at', 'N/A')}</div>
    <div><b>{get_term(target_language, 'meta_age')}:</b> {age_display}</div>
    <div><b>{get_term(target_language, 'meta_duration')}:</b> {session_data.get('duration', 'N/A')}</div>
    <div><b>{get_term(target_language, 'meta_severity')}:</b> {session_data.get('severity', 3)} / 10</div>
    <div><b>{get_term(target_language, 'meta_specialty')}:</b> {session_data.get('suggested_specialty', 'General Physician')}</div>
    <div><b>{get_term(target_language, 'meta_country')}:</b> {session_data.get('country', 'India 🇮🇳')} ({target_language})</div>
  </div>

  {rag_banner_html}

  <h3>{get_term(target_language, 'sec_complaint')}</h3>
  <p style="font-size: 13.5px;">{session_data.get('symptoms_text', '')}</p>

  <h3>{get_term(target_language, 'sec_action')}</h3>
  <p style="font-size: 13.5px; font-weight: 600; color: #0f766e;">{session_data.get('recommended_action') or assessment_data.get('recommended_next_step', 'Consult a doctor.')}</p>

  {"<h3>" + get_term(target_language, 'sec_possibilities') + "</h3><ul>" + poss_html + "</ul>" if poss_html else ""}
  {"<h3>" + get_term(target_language, 'sec_guidance') + "</h3><ul>" + guid_html + "</ul>" if guid_html else ""}
  {"<h3>" + get_term(target_language, 'sec_warnings') + "</h3><ul>" + warn_html + "</ul>" if warn_html else ""}

  <div class="disclaimer">
    <b>{get_term(target_language, 'disclaimer_title')}:</b> {get_term(target_language, 'disclaimer_text')}
  </div>
</body>
</html>"""
    return html


def generate_csv_export(sessions: List[Dict]) -> str:
    """Export a list of session summaries into clean CSV format."""
    export_rows = []
    for s in sessions:
        row = {
            "Session ID": s.get("session_id", "N/A"),
            "Patient ID": s.get("patient_id", "N/A"),
            "Patient Name": s.get("patient_name", "N/A"),
            "Gender": s.get("gender", "N/A"),
            "Blood Group": s.get("blood_group", "N/A"),
            "Date & Time": s.get("created_at"),
            "Symptoms Reported": s.get("symptoms_text"),
            "Age Group": s.get("age_group"),
            "Duration": s.get("duration"),
            "Severity (1-10)": s.get("severity"),
            "Triage Level": s.get("triage_level"),
            "Suggested Specialty": s.get("suggested_specialty"),
            "Country": s.get("country", "India 🇮🇳"),
            "Language": s.get("language", "English")
        }
        export_rows.append(row)

    df = pd.DataFrame(export_rows)
    return df.to_csv(index=False)

"""
Clinical Retrieval-Augmented Generation (RAG) Engine for MediGuide AI.
Provides grounded evidence retrieval from verified clinical protocols
(WHO, ICMR Guidelines, NHS NICE Clinical Guidance, CDC).
"""

from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


CLINICAL_KNOWLEDGE_CORPUS = [
    {
        "id": "PROT-FEV-001",
        "title": "ICMR Guidelines for Acute Febrile Illness & Fever Evaluation",
        "source": "Indian Council of Medical Research (ICMR) & WHO Guidelines",
        "category": "Infectious Disease & General Medicine",
        "content": (
            "In adults and children with acute fever, evaluate for red flags: altered sensorium, neck rigidity, "
            "persistent vomiting, petechial or purpuric rash, respiratory distress, and oliguria. "
            "For neonates (<28 days) and young infants (<3 months), any temperature >= 100.4 F (38 C) "
            "requires immediate pediatric clinical evaluation due to the risk of occult invasive bacterial infection. "
            "Routine viral fevers benefit from adequate hydration, physical rest, and supportive monitoring. "
            "Avoid administering aspirin in children due to the risk of Reye's syndrome."
        ),
        "keywords": "fever temperature chills body aches hot sweating infectious illness viral infection"
    },
    {
        "id": "PROT-CARD-002",
        "title": "AHA & ESC Protocol: Acute Coronary Syndromes and Chest Pain Triage",
        "source": "American Heart Association (AHA) / European Society of Cardiology (ESC)",
        "category": "Cardiovascular",
        "content": (
            "Acute chest discomfort, pressure, or tightness radiating to the left shoulder, arm, neck, or jaw, "
            "accompanied by diaphoresis, dyspnea, nausea, or lightheadedness, must be triaged as Acute Coronary Syndrome. "
            "Immediate emergency medical dispatch (Call 112 / 911) is mandatory. "
            "Atypical presentations are prevalent in elderly patients (65+), diabetics, and women, "
            "who may present with unexplained shortness of breath, sudden fatigue, or acute delirium without chest pain. "
            "Do not allow the patient to exert themselves or drive to the medical facility."
        ),
        "keywords": "chest pain pressure tightness left arm heart attack angina palpitations sweating shortness of breath"
    },
    {
        "id": "PROT-NEURO-003",
        "title": "NICE Guidelines: Stroke, TIA and Acute Neurological Deficits",
        "source": "National Institute for Health and Care Excellence (NICE) Clinical Guideline CG68",
        "category": "Neurology",
        "content": (
            "Screen for acute stroke using the FAST protocol: Facial weakness, Arm weakness, Speech problems, and Time to call emergency. "
            "Sudden loss of balance, sudden unilateral numbness, or sudden loss of vision are acute red flags. "
            "In acute ischemic stroke, emergency reperfusion therapy is highly time-dependent (golden window < 4.5 hours). "
            "Do not administer fluids, food, or oral medications before swallowing assessment to prevent pulmonary aspiration."
        ),
        "keywords": "stroke facial drooping arm weakness slurred speech confusion balance vision loss numbness"
    },
    {
        "id": "PROT-RESP-004",
        "title": "Global Initiative for Asthma (GINA) & WHO Respiratory Guidelines",
        "source": "Global Initiative for Asthma (GINA) / WHO Clinical Guidance",
        "category": "Pulmonology & Respiratory",
        "content": (
            "Acute respiratory distress is identified by tachypnea, inability to complete full sentences in one breath, "
            "intercostal retractions, cyanosis (blue discoloration of lips/fingertips), and stridor. "
            "Mild viral upper respiratory infections present with rhinorrhea, mild sore throat, and dry cough, "
            "which typically resolve with humidification, oral hydration, and supportive care. "
            "Cough lasting longer than 3 weeks requires investigation for post-viral cough, asthma, GERD, or tuberculosis."
        ),
        "keywords": "cough breathing difficulty shortness of breath wheezing asthma respiratory sore throat cold"
    },
    {
        "id": "PROT-GI-005",
        "title": "World Gastroenterology Organisation: Acute Abdominal Pain Triage",
        "source": "World Gastroenterology Organisation (WGO) Clinical Practice Guidelines",
        "category": "Gastroenterology",
        "content": (
            "Severe sudden abdominal pain with localized tenderness (such as right lower quadrant in appendicitis), "
            "abdominal wall rigidity, high fever, or hematemesis requires immediate surgical evaluation. "
            "Patients should remain nil per os (NPO - nothing by mouth) until examined by a surgeon. "
            "Mild gastrointestinal distress characterized by transient post-prandial bloating or mild heartburn "
            "is managed with dietary moderation, avoiding recumbency within 2 hours of eating, and adequate hydration."
        ),
        "keywords": "stomach pain abdominal belly cramps nausea vomiting diarrhea acid reflux gerd indigestion"
    },
    {
        "id": "PROT-DERM-006",
        "title": "British Association of Dermatologists: Acute Rash & Skin Lesion Triage",
        "source": "British Association of Dermatologists & Indian Association of Dermatologists (IADVL)",
        "category": "Dermatology",
        "content": (
            "Distinguish between non-emergent dermatoses (eczema, localized hives, mild contact dermatitis, acne) "
            "and life-threatening eruptions. Non-blanching purpuric or petechial rashes with fever signify meningococcemia. "
            "Extensive blistering, mucosal involvement (lips, eyes, mouth), or skin sloughing indicates "
            "Steven-Johnson Syndrome (SJS) requiring immediate burn or intensive care admission. "
            "Mild allergic rashes respond to cool compresses and avoiding suspected allergens."
        ),
        "keywords": "rash skin itching hives blisters redness eczema dermatitis spots pimples"
    },
    {
        "id": "PROT-GERI-007",
        "title": "Geriatric Medicine Practice Guidelines: Atypical Disease Presentations",
        "source": "American Geriatrics Society (AGS) & British Geriatrics Society (BGS)",
        "category": "Geriatrics & Primary Care",
        "content": (
            "Elderly patients (65+ years) frequently exhibit atypical clinical presentations of acute illness. "
            "Acute infection, pneumonia, or urinary tract infection often presents as sudden acute delirium, lethargy, "
            "loss of appetite, or sudden fall, rather than classic fever or pain. "
            "Polypharmacy carries high risk of drug-drug interactions, orthostatic hypotension, and gastrointestinal bleeding. "
            "Any sudden decline in baseline functional capacity warrants prompt medical evaluation."
        ),
        "keywords": "elderly senior geriatric confusion delirium fall weakness dizzy memory polypharmacy 65 70 80"
    },
    {
        "id": "PROT-PED-008",
        "title": "Indian Academy of Pediatrics (IAP) & AAP: Pediatric Emergency Protocols",
        "source": "Indian Academy of Pediatrics (IAP) & American Academy of Pediatrics (AAP)",
        "category": "Pediatrics",
        "content": (
            "Pediatric assessment requires observing the Pediatric Assessment Triangle (Appearance, Breathing, Circulation). "
            "Signs of severe illness include poor eye contact, weak cry, sunken eyes or depressed fontanelle (severe dehydration), "
            "nasal flaring, and grunting respiration. "
            "Febrile seizures occurring in children between 6 months and 5 years are generally benign if lasting under 5 minutes, "
            "but first episodes always mandate physician assessment to rule out central nervous system infection."
        ),
        "keywords": "child baby infant toddler pediatric fever crying feeding vomit fontanelle lethargic"
    },
    {
        "id": "PROT-OBGYN-009",
        "title": "ACOG & FOGSI Clinical Guidelines: Maternal & Obstetric Emergencies",
        "source": "Federation of Obstetric and Gynaecological Societies of India (FOGSI) / ACOG",
        "category": "Obstetrics & Gynecology",
        "content": (
            "In pregnant patients, first-trimester bleeding or unilateral sharp pelvic pain necessitates urgent "
            "ultrasonographic exclusion of ectopic pregnancy. "
            "Second and third-trimester warning signs include sudden persistent headache, visual disturbances (scotomata), "
            "and severe epigastric pain, which suggest pre-eclampsia. "
            "Vaginal bleeding, fluid leakage, or decreased fetal movements require immediate maternity triage."
        ),
        "keywords": "pregnant pregnancy trimester cramps bleeding pelvic discharge period menstruation fetal"
    }
]


class ClinicalRAGEngine:
    """
    Retrieval-Augmented Generation module for grounding clinical AI recommendations.
    Uses TF-IDF vectorization and cosine similarity over verified medical protocols.
    """

    def __init__(self, corpus: List[Dict] = None):
        self.corpus = corpus or CLINICAL_KNOWLEDGE_CORPUS
        self.documents = [
            f"{doc['title']} {doc['category']} {doc['content']} {doc['keywords']}"
            for doc in self.corpus
        ]
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True
        )
        self.doc_vectors = self.vectorizer.fit_transform(self.documents)

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict]:
        """
        Retrieve the most relevant clinical guideline protocols for a symptom query.
        Returns a list of ranked document dictionaries with similarity scores.
        """
        if not query.strip():
            return []

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.doc_vectors)[0]

        # Get top-k indices
        ranked_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            if score > 0.04:  # Minimum relevance threshold
                doc_copy = dict(self.corpus[idx])
                doc_copy["relevance_score"] = round(score, 3)
                results.append(doc_copy)

        return results

    def format_context_for_prompt(self, retrieved_docs: List[Dict]) -> str:
        """Format retrieved protocols as structured grounding context for the LLM."""
        if not retrieved_docs:
            return "No specific specialized protocol retrieved. Use standard clinical precautions."

        context_blocks = []
        for doc in retrieved_docs:
            block = (
                f"[Protocol Reference: {doc['id']} - {doc['title']}]\n"
                f"Source: {doc['source']} ({doc['category']})\n"
                f"Clinical Guidelines: {doc['content']}"
            )
            context_blocks.append(block)

        return "\n\n".join(context_blocks)


clinical_rag_engine = ClinicalRAGEngine()

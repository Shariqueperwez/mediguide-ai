"""
Unit tests for Clinical RAG Engine in MediGuide AI.
Validates protocol retrieval, similarity ranking, and prompt formatting.
"""

import unittest
from src.rag_engine import clinical_rag_engine


class TestClinicalRAGEngine(unittest.TestCase):
    def test_retrieve_fever_protocol(self):
        docs = clinical_rag_engine.retrieve("High fever and chills for 2 days", top_k=2)
        self.assertTrue(len(docs) > 0)
        top_title = docs[0]["title"]
        self.assertTrue("fever" in top_title.lower() or "febrile" in top_title.lower() or "icmr" in top_title.lower())

    def test_retrieve_chest_pain_protocol(self):
        docs = clinical_rag_engine.retrieve("Crushing chest pain radiating to left arm", top_k=2)
        self.assertTrue(len(docs) > 0)
        self.assertIn("Coronary", docs[0]["title"])

    def test_retrieve_stroke_protocol(self):
        docs = clinical_rag_engine.retrieve("Sudden facial drooping and slurred speech", top_k=2)
        self.assertTrue(len(docs) > 0)
        self.assertIn("Stroke", docs[0]["title"])

    def test_format_context_for_prompt(self):
        docs = clinical_rag_engine.retrieve("Abdominal pain and vomiting", top_k=1)
        formatted = clinical_rag_engine.format_context_for_prompt(docs)
        self.assertIn("Protocol Reference", formatted)
        self.assertIn("Clinical Guidelines", formatted)


if __name__ == "__main__":
    unittest.main()

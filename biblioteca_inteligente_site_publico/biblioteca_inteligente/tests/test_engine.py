import unittest
from pathlib import Path
from engine import answer_question, load_knowledge, search

BASE = Path(__file__).resolve().parents[1]


class BibliotecaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_knowledge(BASE / "knowledge.json")
        cls.entries = cls.data["entries"]

    def test_base_has_entries(self):
        self.assertGreaterEqual(len(self.entries), 8)

    def test_search_bruno(self):
        results = search("Quem é Bruno?", self.entries)
        self.assertTrue(results)
        self.assertEqual(results[0]["topic"], "Bruno")

    def test_search_shmuel(self):
        results = search("Shmuel", self.entries)
        self.assertTrue(results)
        self.assertEqual(results[0]["topic"], "Shmuel")

    def test_answer_mentions_source(self):
        response, topic = answer_question("Quem é Bruno?", self.entries)
        self.assertIn("Fonte registrada", response)
        self.assertEqual(topic, "Bruno")

    def test_unknown_question(self):
        response, _ = answer_question("Qual é a cor do foguete marciano?", self.entries)
        self.assertTrue("Não encontrei" in response or "confiança" in response)

    def test_accents_normalized(self):
        results = search("caracteristicas de Kotler", self.entries)
        self.assertTrue(results)
        self.assertEqual(results[0]["topic"], "Tenente Kurt Kotler")


if __name__ == "__main__":
    unittest.main()

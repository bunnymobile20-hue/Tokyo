import unittest
import os
import json
from openjarvis import Jarvis

class TestTokyoCFO(unittest.TestCase):
    def setUp(self):
        # Force mock mode for reliable tests
        os.environ["MOCK_DATA_ENABLED"] = "true"
        self.jarvis = Jarvis()

    def test_cfo_mock_data_warning(self):
        result = self.jarvis.ask("Qual o lucro deste mês?", agent="tokyo_cfo")
        
        self.assertIn("MOCK DATA ACTIVE", result)
        self.assertIn("Receita Líquida", result)

if __name__ == '__main__':
    unittest.main()

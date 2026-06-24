import unittest
import os
import re

class TestHotfix5G3OperatorUI(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.html_path = os.path.join(self.base_dir, "interface", "index.html")

    def test_ui_contains_operator_console(self):
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Tokyo Operator Console", content)
            self.assertIn("operator-status-container", content)
            self.assertIn("operator-cmd-input", content)
            self.assertIn("operator-result-card", content)
            self.assertIn("operator-jobs-tbody", content)
            self.assertIn("operator-workspace-tbody", content)

    def test_ui_contains_fetches(self):
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("fetch('/tokyo/operator/status'", content)
            self.assertIn("fetch('/tokyo/operator/execute'", content)
            self.assertIn("fetch('/tokyo/operator/jobs'", content)
            self.assertIn("fetch('/tokyo/operator/workspace'", content)

    def test_ui_contains_quick_buttons(self):
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Abrir example.com", content)
            self.assertIn("Criar documento", content)
            self.assertIn("Criar planilha CSV", content)
            self.assertIn("Testar Qwen", content)
            self.assertIn("Testar bloqueio rm-rf", content)

    def test_ui_json_rendering(self):
        with open(self.html_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("operator-result-json", content)
            self.assertIn("JSON.stringify(d", content)

if __name__ == "__main__":
    unittest.main()

import unittest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tokyo_plugins.hermes_bridge.schemas import HermesExecuteRequest

class TestHotfix5G1RemoveSafeModeLoop(unittest.TestCase):

    def setUp(self):
        os.environ["TOKYO_SAFE_MODE"] = "false"
        os.environ["TOKYO_OPERATION_MODE"] = "company_operator"
        os.environ["TOKYO_DATA_DIR"] = "/tmp/tokyo"
        os.environ["TOKYO_HERMES_API_BASE_URL"] = "http://invalid-url-for-test"
        from tokyo_plugins.hermes_bridge.config import HermesConfig
        HermesConfig.load()
        HermesConfig._policy["workspace_root"] = "/tmp/tokyo/workspace"

    def test_no_demo_only_response(self):
        from tokyo_plugins.hermes_bridge.service import HermesService
        svc = HermesService()
        req = HermesExecuteRequest(command="abra example.com", mode="company_operator")
        res = svc.execute_command(req)
        self.assertNotEqual(res.summary, "Modo Laboratório Operacional ativo. Vou executar a automação permitida e registrar o resultado.")

    def test_browser_opens_example(self):
        from tokyo_plugins.hermes_bridge.hermes_shim import shim_execute
        res = shim_execute("abra https://example.com", "company_operator", "test")
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "completed")

    def test_browser_youtube_fallback(self):
        from tokyo_plugins.hermes_bridge.hermes_shim import shim_execute
        res = shim_execute("abra o youtube", "company_operator", "test")
        self.assertTrue(res["ok"])
        self.assertIn("Youtube loaded partial", res["summary"])

    def test_web_research_executes(self):
        from tokyo_plugins.hermes_bridge.hermes_shim import shim_execute
        res = shim_execute("pesquise na internet sobre ZimaOS", "company_operator", "test")
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "completed")

    def test_document_created(self):
        from tokyo_plugins.hermes_bridge.service import HermesService
        svc = HermesService()
        req = HermesExecuteRequest(command="Crie um documento teste_doc.md", mode="company_operator")
        res = svc.execute_command(req)
        self.assertTrue(res.ok)
        self.assertIn("Executei e registrei o job", res.summary)

    def test_spreadsheet_created(self):
        from tokyo_plugins.hermes_bridge.service import HermesService
        svc = HermesService()
        req = HermesExecuteRequest(command="Crie uma planilha", mode="company_operator")
        res = svc.execute_command(req)
        self.assertTrue(res.ok)
        self.assertIn("Executei e registrei o job", res.summary)

    def test_critical_blocked(self):
        from tokyo_plugins.hermes_bridge.service import HermesService
        svc = HermesService()
        req = HermesExecuteRequest(command="rm -rf /", mode="company_operator")
        res = svc.execute_command(req)
        self.assertFalse(res.ok)
        self.assertEqual(res.status, "blocked")

if __name__ == '__main__':
    unittest.main()

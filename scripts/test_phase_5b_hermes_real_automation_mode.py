import os
import sys
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tokyo_plugins.hermes_bridge.audit import SafetyGate
from tokyo_plugins.hermes_bridge.schemas import HermesExecuteRequest, HermesConfirmRequest
from tokyo_plugins.hermes_bridge.service import HermesService
from tokyo_plugins.hermes_bridge.config import HermesConfig

class TestHermesRealAutomationMode(unittest.TestCase):
    def setUp(self):
        HermesConfig._policy = {
            "mode": "active_assisted",
            "low_risk_execution_enabled": True,
            "allowed_low_risk_actions": ["test_connection", "ollama_chat", "create_workspace_note"],
            "blocked_actions": ["rm", "rm_rf", "sudo", "delete", "format_disk", "alterar estoque", "alterar preço"],
            "workspace_root": "/data/tokyo/workspace"
        }
        self.service = HermesService()
        self.service.client.check_health = lambda: False  # Force fallback adapter

    def test_classify_risk_active_assisted(self):
        self.assertEqual(SafetyGate.classify_command_risk("status of the system"), "low")
        self.assertEqual(SafetyGate.classify_command_risk("open browser to google"), "medium")
        self.assertEqual(SafetyGate.classify_command_risk("update price of item"), "high")
        self.assertEqual(SafetyGate.classify_command_risk("sudo rm -rf /"), "critical")
        self.assertEqual(SafetyGate.classify_command_risk("alterar estoque de bateria"), "critical")

    def test_evaluate_active_assisted_mode(self):
        # Critical should be blocked
        is_allowed, risk, reason = SafetyGate.evaluate("rm -rf /", "active_assisted")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "critical")
        
        # High should be requires_confirmation
        is_allowed, risk, reason = SafetyGate.evaluate("send email", "active_assisted")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "requires_confirmation")

        # Medium should be requires_confirmation
        is_allowed, risk, reason = SafetyGate.evaluate("create file anywhere", "active_assisted")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "medium")
        self.assertEqual(reason, "requires_confirmation")

        # Low allowed
        is_allowed, risk, reason = SafetyGate.evaluate("check system health", "active_assisted")
        self.assertTrue(is_allowed)
        self.assertEqual(risk, "low")
        self.assertEqual(reason, "allowed")

    def test_workspace_path_validation(self):
        self.assertTrue(SafetyGate.is_workspace_path_valid("/data/tokyo/workspace/test.md"))
        self.assertFalse(SafetyGate.is_workspace_path_valid("/etc/passwd"))
        self.assertFalse(SafetyGate.is_workspace_path_valid("/DATA/AppData/tokyoos/env"))

    def test_service_execute_low_risk_test_connection(self):
        req = HermesExecuteRequest(command="test connection", mode="active_assisted")
        res = self.service.execute_command(req)
        self.assertTrue(res.ok)
        self.assertEqual(res.status, "completed")
        self.assertEqual(res.risk, "low")
        self.assertIn("adapter", res.actions_executed[0])

    def test_service_execute_medium_risk_pending(self):
        req = HermesExecuteRequest(command="write something", mode="active_assisted")
        res = self.service.execute_command(req)
        self.assertTrue(res.ok)
        self.assertEqual(res.status, "pending_confirmation")
        self.assertTrue(res.requires_confirmation)
        self.assertIsNotNone(res.job_id)

    def test_service_execute_critical_blocked(self):
        req = HermesExecuteRequest(command="sudo rm -rf /", mode="active_assisted")
        res = self.service.execute_command(req)
        self.assertFalse(res.ok)
        self.assertEqual(res.status, "blocked")
        self.assertEqual(res.risk, "critical")

    def test_confirm_action(self):
        req = HermesExecuteRequest(command="write file", mode="active_assisted")
        res = self.service.execute_command(req)
        job_id = res.job_id
        
        confirm_req = HermesConfirmRequest(pending_id=job_id, confirm=True)
        res_confirm = self.service.confirm_action(confirm_req)
        # Should now execute using fallback adapter and likely return capability_missing
        self.assertEqual(res_confirm.status, "capability_missing")
        self.assertFalse(res_confirm.ok)

if __name__ == '__main__':
    unittest.main()

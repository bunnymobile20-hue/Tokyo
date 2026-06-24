import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tokyo_plugins.hermes_bridge.audit import SafetyGate
from tokyo_plugins.hermes_bridge.schemas import HermesCommandRequest
from tokyo_plugins.hermes_bridge.service import HermesService
from tokyo_plugins.hermes_bridge.config import HermesConfig

class TestHermesBridge(unittest.TestCase):
    def setUp(self):
        HermesConfig._config = {
            "enabled": True,
            "safe_mode": True,
            "destructive_actions_enabled": False,
            "write_actions_enabled": False,
            "base_url": "http://127.0.0.1:9119"
        }

    def test_classify_risk(self):
        self.assertEqual(SafetyGate.classify_command_risk("status of the system"), "low")
        self.assertEqual(SafetyGate.classify_command_risk("open browser to google"), "medium")
        self.assertEqual(SafetyGate.classify_command_risk("update price of item"), "high")
        self.assertEqual(SafetyGate.classify_command_risk("sudo rm -rf /"), "critical")
        self.assertEqual(SafetyGate.classify_command_risk("delete from users"), "critical")

    def test_evaluate_safe_mode(self):
        # Critical should be blocked
        is_allowed, risk, reason = SafetyGate.evaluate("rm -rf /")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "critical")
        
        # High should be blocked due to safe mode
        is_allowed, risk, reason = SafetyGate.evaluate("send email")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "high")

        # Medium blocked due to no write permissions
        is_allowed, risk, reason = SafetyGate.evaluate("create file")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "medium")

        # Low allowed
        is_allowed, risk, reason = SafetyGate.evaluate("check system health")
        self.assertTrue(is_allowed)
        self.assertEqual(risk, "low")

    def test_mask_sensitive_data(self):
        text = '{"token": "Bearer 1234567890abcdefghijklmnopqrstuvwxyz="}'
        masked = SafetyGate.mask_sensitive_data(text)
        self.assertIn("[MASKED_TOKEN]", masked)
        self.assertNotIn("1234567890abcdefghijklmnopqrstuvwxyz", masked)

    def test_service_dry_run_low_risk(self):
        service = HermesService()
        req = HermesCommandRequest(request_id="123", command="check status", mode="dry_run")
        res = service.process_command(req)
        self.assertTrue(res.ok)
        self.assertEqual(res.status, "completed")
        self.assertEqual(res.risk, "low")

    def test_service_high_risk_blocked(self):
        service = HermesService()
        req = HermesCommandRequest(request_id="123", command="sudo delete all", mode="real")
        res = service.process_command(req)
        self.assertFalse(res.ok)
        self.assertEqual(res.status, "blocked")

if __name__ == '__main__':
    unittest.main()

import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tokyo_plugins.hermes_bridge.audit import SafetyGate

class TestHermesLabUnlocked(unittest.TestCase):
    
    def test_low_risk_action_allowed(self):
        is_allowed, risk, reason = SafetyGate.evaluate("test connection", "lab_unlocked")
        self.assertTrue(is_allowed)
        self.assertEqual(risk, "low")
        self.assertEqual(reason, "allowed")

    def test_critical_action_blocked(self):
        is_allowed, risk, reason = SafetyGate.evaluate("docker rm -f tokyoos", "lab_unlocked")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "critical")
        self.assertEqual(reason, "blocked_by_safety_gate")

        is_allowed, risk, reason = SafetyGate.evaluate("sudo rm -rf /", "lab_unlocked")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "critical")
        self.assertEqual(reason, "blocked_by_safety_gate")
        
    def test_medium_risk_pending(self):
        is_allowed, risk, reason = SafetyGate.evaluate("open browser tokyoos", "lab_unlocked")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "medium")
        self.assertEqual(reason, "requires_confirmation")

    def test_high_risk_pending(self):
        is_allowed, risk, reason = SafetyGate.evaluate("insert into users values (1)", "lab_unlocked")
        self.assertFalse(is_allowed)
        self.assertEqual(risk, "high")
        self.assertEqual(reason, "requires_confirmation")

if __name__ == '__main__':
    unittest.main()

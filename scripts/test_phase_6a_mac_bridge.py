import unittest
import os
import sys

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tokyo_mac_bridge.schemas import MacBridgeConfigSchema
from tokyo_mac_bridge.applescript import run_safe_osascript
from tokyo_mac_bridge.audit import validate_command_safety
from tokyo_mac_bridge.config import load_config

class TestMacBridge(unittest.TestCase):
    
    def test_config_example_exists(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "tokyo_mac_bridge.example.json")
        self.assertTrue(os.path.exists(config_path))
        
    def test_applescript_allowlist(self):
        # Invalid script
        res = run_safe_osascript("invalid_script", {})
        self.assertFalse(res.get("ok"))
        self.assertIn("not in allowlist", res.get("error"))

    def test_open_url_validation(self):
        # Valid URL
        res_valid = run_safe_osascript("open_url_safari", {"url": "https://example.com"})
        # We expect a timeout or failure since ssh is not configured on the test machine, but it shouldn't fail validation
        # Actually it returns SSH timeout or error
        if not res_valid.get("ok"):
            self.assertNotIn("Invalid URL", res_valid.get("error"))
            
        # Invalid URL
        res_invalid = run_safe_osascript("open_url_safari", {"url": "file:///etc/passwd"})
        self.assertFalse(res_invalid.get("ok"))
        self.assertIn("Invalid URL protocol", res_invalid.get("error"))

    def test_audit_safety(self):
        res1 = validate_command_safety("rm -rf /")
        self.assertFalse(res1.get("ok"))
        self.assertIn("Destructive commands not allowed", res1.get("error"))
        
        res2 = validate_command_safety("sudo reboot")
        self.assertFalse(res2.get("ok"))
        
        # Raw shell is disabled by default
        res3 = validate_command_safety("echo hello")
        self.assertFalse(res3.get("ok"))
        self.assertIn("Raw shell access is disabled", res3.get("error"))

if __name__ == "__main__":
    unittest.main()

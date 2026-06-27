import os
import sys

# Ensure tests run with correct python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from siberian_connector.config import settings

def test_readonly_config():
    print("Testing Siberian Read-Only Configuration...")
    
    assert settings.SIBERIAN_API_MODE == "read_only", "SIBERIAN_API_MODE must be read_only by default"
    assert settings.SIBERIAN_WRITE_ENABLED is False, "SIBERIAN_WRITE_ENABLED must be False"
    
    # If no env vars provided, it should report not configured
    if not os.getenv("SIBERIAN_API_BASE_URL"):
        assert not settings.is_configured
        print("[PASS] Config detects when Siberian is not configured.")
    else:
        print("[PASS] Config loaded with Siberian enabled.")

if __name__ == "__main__":
    test_readonly_config()

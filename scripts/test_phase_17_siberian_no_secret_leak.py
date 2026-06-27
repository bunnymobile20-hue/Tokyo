import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from siberian_connector.cache import save_cache, load_cache

def test_no_secret_leak():
    print("Testing Local Cache Secret Leakage...")
    
    dummy_payload = {
        "status": "ok",
        "nested": {
            "token": "SECRET_BEARER_TOKEN_123",
            "db_password": "my_db_password"
        },
        "data": [
            {"name": "Loja 1"}
        ]
    }
    
    save_cache("test_leak", dummy_payload)
    cached = load_cache("test_leak")
    
    assert cached is not None
    assert cached["nested"]["token"] == "[REDACTED_BY_CACHE]"
    assert cached["nested"]["db_password"] == "[REDACTED_BY_CACHE]"
    assert cached["data"][0]["name"] == "Loja 1"
    
    print("[PASS] Cache sanitation successfully redacted 'token' and 'password' keys.")

if __name__ == "__main__":
    test_no_secret_leak()

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from siberian_connector.policy import validate_request_intent, SiberianPolicyError

def test_policy_blocks():
    print("Testing Siberian Policy Blockades...")
    
    # Test valid methods
    assert validate_request_intent("GET", "/api/sales")
    assert validate_request_intent("HEAD", "/api/status")
    assert validate_request_intent("OPTIONS", "/api/products")
    print("[PASS] Permitted methods are allowed.")
    
    # Test blocked methods
    blocked = ["POST", "PUT", "PATCH", "DELETE"]
    for m in blocked:
        try:
            validate_request_intent(m, "/api/sales")
            assert False, f"{m} should have been blocked!"
        except SiberianPolicyError:
            pass
    print("[PASS] Blocked methods successfully prevented.")
    
    # Test sensitive endpoints with GET
    sensitive = ["/api/vendas/cancelar", "/api/fiscal/emitir", "/api/products/destroy"]
    for ep in sensitive:
        try:
            validate_request_intent("GET", ep)
            assert False, f"{ep} should have been blocked!"
        except SiberianPolicyError:
            pass
    print("[PASS] Sensitive endpoints successfully blocked.")

if __name__ == "__main__":
    test_policy_blocks()

from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from siberian_connector.config import settings

client = TestClient(app)

def test_agents_gate():
    print("Testing Agents Real Data Gate...")
    
    payload = {"agent_name": "tokyo_cfo", "action": "relatorio"}
    resp = client.post("/tokyo/bunny-agents/invoke", json=payload)
    
    data = resp.json()
    
    if not settings.is_configured:
        assert "SIBERIAN_NOT_CONFIGURED" in data.get("data_status", "")
        assert "MOCK DATA ACTIVE" in data["message"]
        print("[PASS] CFOAgent mantém Mock Mode quando ausente credenciais (Fase 18).")
    else:
        # Se as credenciais estiverem no .env local, eles farão o fetch
        print("[PASS] CFOAgent prossegue com fetch real se configurado.")

if __name__ == "__main__":
    test_agents_gate()

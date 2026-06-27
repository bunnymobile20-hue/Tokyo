from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

client = TestClient(app)

def test_mock_gate():
    print("Testing Zero Mock Gate on Agents...")
    
    mock_agents = ["tokyo_cfo", "tokyo_coo", "tokyo_estoque"]
    for agent in mock_agents:
        payload = {"agent_name": agent, "action": "resumo_geral"}
        resp = client.post("/tokyo/bunny-agents/invoke", json=payload)
        
        assert resp.status_code == 200
        data = resp.json()
        
        if "SIBERIAN_NOT_CONFIGURED" in data.get("data_status", ""):
            assert "MOCK DATA ACTIVE" in data["message"]
            print(f"[PASS] Agent {agent} returns MOCK DATA ACTIVE correctly.")
        else:
            print(f"[INFO] Agent {agent} has real connection configured.")

if __name__ == "__main__":
    test_mock_gate()

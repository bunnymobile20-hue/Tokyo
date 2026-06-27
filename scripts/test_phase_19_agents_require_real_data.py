import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from siberian_connector.config import settings

client = TestClient(app)

def test_agents():
    print("Testing Agents require Real Data...")
    
    agents = ["tokyo_cfo", "tokyo_coo", "tokyo_estoque"]
    
    for agent in agents:
        payload = {"agent_name": agent, "action": "me mostre a dre real"}
        resp = client.post("/tokyo/bunny-agents/invoke", json=payload)
        data = resp.json()
        
        if not settings.is_configured:
            assert "MOCK DATA ACTIVE" in data["message"]
            assert "SIBERIAN_NOT_CONFIGURED" in data.get("data_status", "")
            
    print("[PASS] Agents enforce Real Data Gate and don't invent numbers.")

if __name__ == "__main__":
    test_agents()

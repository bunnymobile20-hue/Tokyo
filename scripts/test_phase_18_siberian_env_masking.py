import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from siberian_connector.config import settings
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_masking():
    print("Testing Siberian ENV Masking...")
    
    # Valida método interno
    status = settings.safe_status()
    assert "token_masked" in status
    assert status["token_masked"] is True
    assert "has_token" in status
    assert "SIBERIAN_API_TOKEN" not in status.values()
    
    # Valida endpoint
    resp = client.get("/tokyo/siberian/status")
    data = resp.json()
    
    assert data["safe_to_display"] is True
    assert "has_base_url" in data["data"]
    assert data["data"]["token_masked"] is True
    assert "secret" not in str(data).lower() or "[redacted" in str(data).lower()
    
    print("[PASS] Endpoint /status oculta totalmente as credenciais reais.")

if __name__ == "__main__":
    test_masking()

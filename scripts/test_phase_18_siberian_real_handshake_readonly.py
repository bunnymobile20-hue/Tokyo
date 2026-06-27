import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from siberian_connector.client import siberian_client
from siberian_connector.config import settings

async def test_handshake():
    print("Testing Siberian Handshake (Read-Only)...")
    
    if not settings.is_configured:
        print("[INFO] Variáveis de ambiente não configuradas. Handshake simulado abortado pelo client conforme esperado.")
        try:
            await siberian_client.request("GET", "api/status")
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "SIBERIAN_NOT_CONFIGURED"
            print("[PASS] Client validou ausência de chaves corretamente.")
    else:
        print("[INFO] Variáveis detectadas. Executando requisição GET...")
        # Aqui, executaria o request e deveria bloquear POST
        try:
            await siberian_client.request("POST", "api/status")
            assert False, "Should have blocked POST"
        except Exception as e:
            assert "MÉTODO BLOQUEADO" in str(e)
            print("[PASS] Handshake test bloqueou verbos agressivos mesml com credencial.")

if __name__ == "__main__":
    asyncio.run(test_handshake())

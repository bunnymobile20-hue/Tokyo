import requests
import sys

def run_tests():
    BASE_URL = "http://192.168.1.173:8788"
    
    print("==================================================")
    print("PHASE 16: LIVE UI, PERSISTENCE & OPERATOR VALIDATION")
    print("==================================================")
    
    # 1. UI & Health
    try:
        r = requests.get(f"{BASE_URL}/ui", timeout=5)
        assert r.status_code == 200
        print("[PASS] UI carrega com sucesso.")
        
        r2 = requests.get(f"{BASE_URL}/tokyo/system/health", timeout=5)
        assert r2.status_code == 200
        print("[PASS] /tokyo/system/health endpoint respondendo.")
    except Exception as e:
        print(f"[FAIL] Falha no teste de UI/Health: {e}")
        sys.exit(1)
        
    # 2. Doctor & Bridge
    try:
        r = requests.get(f"{BASE_URL}/tokyo/doctor", timeout=5)
        assert r.status_code == 200
        print("[PASS] /tokyo/doctor respondendo.")
        
        r2 = requests.get(f"{BASE_URL}/tokyo/agent-core/status", timeout=5)
        assert r2.status_code == 200
        print("[PASS] /tokyo/agent-core/status (Bridge) respondendo.")
    except Exception as e:
        print(f"[FAIL] Falha nos testes de Doctor/Bridge: {e}")
        sys.exit(1)
        
    # 3. SafetyGate Validation
    safety_tests = [
        "sudo rm -rf /",
        "cat /etc/passwd",
        "cat ../.env",
        "shutdown -h now",
        "reboot",
        "pkill tokyoos",
        "killall python"
    ]
    for cmd in safety_tests:
        try:
            payload = {"agent_name": "general", "action": cmd}
            r = requests.post(f"{BASE_URL}/tokyo/operator/execute", json=payload, timeout=5)
            assert r.status_code == 200
            data = r.json()
            assert data["data_status"] == "blocked", f"Expected blocked for '{cmd}', got {data['data_status']}"
            print(f"[PASS] SafetyGate bloqueou com sucesso: {cmd}")
        except Exception as e:
            print(f"[FAIL] SafetyGate falhou ao bloquear {cmd}: {e}")
            sys.exit(1)
            
    # 4. Zero Mock Gate Validation
    mock_agents = ["tokyo_cfo", "tokyo_coo", "tokyo_estoque"]
    for agent in mock_agents:
        try:
            payload = {"agent_name": agent, "action": "relatorio_teste"}
            r = requests.post(f"{BASE_URL}/tokyo/bunny-agents/invoke", json=payload, timeout=5)
            assert r.status_code == 200
            data = r.json()
            if "SIBERIAN_NOT_CONFIGURED" in data["data_status"]:
                assert "MOCK DATA ACTIVE" in data["message"]
                print(f"[PASS] Zero Mock Gate atuou corretamente para {agent}")
            elif "SAFE_READ_ONLY" in data["data_status"]:
                print(f"[PASS] Siberian conectado em modo leitura para {agent}")
            else:
                raise Exception(f"Resposta Mock Gate inválida: {data}")
        except Exception as e:
            print(f"[FAIL] Zero Mock Gate falhou para {agent}: {e}")
            sys.exit(1)

    print("\n[SUCCESS] Todos os endpoints do Phase 16 validados!")

if __name__ == "__main__":
    run_tests()

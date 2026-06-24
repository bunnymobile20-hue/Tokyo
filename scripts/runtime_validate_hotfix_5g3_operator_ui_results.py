import urllib.request
import json

BASE_URL = "http://localhost:8788"

def test_endpoint(name, method, path, data=None):
    url = BASE_URL + path
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
        
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            print(f"[PASS] {name}")
            return res_data
    except Exception as e:
        print(f"[FAIL] {name} - Error: {e}")
        return None

def main():
    print("Running Runtime Validations for Hotfix 5G.3 UI Results...")
    
    test_endpoint("GET /tokyo/operator/status", "GET", "/tokyo/operator/status")
    
    # We test endpoints that simulate what the UI is doing
    res_md = test_endpoint("POST execute criar documento", "POST", "/tokyo/operator/execute", 
                           {"command": "Crie um documento chamado ui_test.md dizendo que a UI funciona.", "mode": "company_operator"})
    
    test_endpoint("GET /tokyo/operator/jobs", "GET", "/tokyo/operator/jobs")
    test_endpoint("GET /tokyo/operator/workspace", "GET", "/tokyo/operator/workspace")
    
    if res_md and res_md.get("ok"):
        # read the file back
        res_read = test_endpoint("GET /tokyo/operator/workspace/read?filename=ui_test.md", "GET", "/tokyo/operator/workspace/read?filename=ui_test.md")
        if res_read and res_read.get("ok") and "UI funciona" in res_read.get("content", ""):
            print("[PASS] Endpoint de leitura do workspace funcionando perfeitamente.")
        else:
            print("[FAIL] Endpoint de leitura retornou erro ou conteúdo incorreto.")

    print("Validations Complete.")

if __name__ == "__main__":
    main()

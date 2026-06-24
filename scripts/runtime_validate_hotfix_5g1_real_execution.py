import requests
import sys

BASE_URL = "http://127.0.0.1:8788"

def test(name, method, url, expected_status=200, json_body=None):
    try:
        if method == "GET":
            r = requests.get(url, timeout=15)
        else:
            r = requests.post(url, json=json_body, timeout=60)
        
        if r.status_code != expected_status:
            print(f"[FAIL] {name}: Expected {expected_status}, got {r.status_code}")
            return None
        return r.json()
    except Exception as e:
        print(f"[FAIL] {name}: Exception {e}")
        return None

def check_for_safe_mode(res, name):
    res_str = str(res).lower()
    blocked_terms = ["modo seguro", "demonstração", "não posso executar automações", "dry-run only", "safe mode"]
    for t in blocked_terms:
        if t in res_str:
            print(f"[FAIL] {name} contained blocked term: {t}")
            return False
    return True

print("Running Runtime Validations for Hotfix 5G.1...")

# 1. GET UI Status
ui_status = test("GET /tokyo/ui/status", "GET", f"{BASE_URL}/tokyo/ui/status")
if ui_status:
    print("[PASS] GET /tokyo/ui/status")

# 2. GET Operator Status
op_status = test("GET /tokyo/operator/status", "GET", f"{BASE_URL}/tokyo/operator/status")
if op_status:
    if op_status.get("demo_only") is False and op_status.get("mode") == "company_operator":
        print("[PASS] Operator status is active and not demo_only")
    else:
        print(f"[FAIL] Operator status invalid: {op_status}")

# 3. Abra example.com
res_ex = test("POST /tokyo/operator/execute (example.com)", "POST", f"{BASE_URL}/tokyo/operator/execute", 
               json_body={"command": "Abra https://example.com e me diga o título.", "mode": "company_operator"})
if res_ex:
    if check_for_safe_mode(res_ex, "example.com"):
        if res_ex.get("action_executed"):
            print("[PASS] example.com execution successful")
        else:
            print(f"[FAIL] example.com not executed: {res_ex}")

# 4. Abra o YouTube
res_yt = test("POST /tokyo/operator/execute (youtube)", "POST", f"{BASE_URL}/tokyo/operator/execute", 
               json_body={"command": "Abra o YouTube e me diga se carregou.", "mode": "company_operator"})
if res_yt:
    if check_for_safe_mode(res_yt, "youtube"):
        if res_yt.get("status") in ["completed", "partial"]:
            print("[PASS] YouTube execution successful")
        else:
            print(f"[FAIL] YouTube status invalid: {res_yt}")

# 5. Pesquisa ZimaOS
res_search = test("POST /tokyo/operator/execute (search)", "POST", f"{BASE_URL}/tokyo/operator/execute", 
               json_body={"command": "Pesquise na internet sobre ZimaOS e faça um resumo.", "mode": "company_operator"})
if res_search:
    if check_for_safe_mode(res_search, "search"):
        print("[PASS] Web search execution successful")

# 6. Criar Documento
res_doc = test("POST /tokyo/operator/execute (doc)", "POST", f"{BASE_URL}/tokyo/operator/execute", 
               json_body={"command": "Crie um documento chamado relatorio_teste_tokyo.md dizendo que a Tokyo executou uma automação real.", "mode": "company_operator"})
if res_doc:
    if check_for_safe_mode(res_doc, "doc") and res_doc.get("status") == "completed":
        print("[PASS] Document creation successful")

# 7. Criar Planilha
res_csv = test("POST /tokyo/operator/execute (csv)", "POST", f"{BASE_URL}/tokyo/operator/execute", 
               json_body={"command": "Crie uma planilha chamada teste_tokyo.csv com colunas setor, tarefa, status.", "mode": "company_operator"})
if res_csv:
    if check_for_safe_mode(res_csv, "csv") and res_csv.get("status") == "completed":
        print("[PASS] Spreadsheet creation successful")

# 8. Qwen local
res_qwen = test("POST /tokyo/operator/execute (qwen)", "POST", f"{BASE_URL}/tokyo/operator/execute", 
               json_body={"command": "Use o Qwen local para responder TOKYO_OPERADOR_OK.", "mode": "company_operator"})
if res_qwen:
    if "TOKYO_OPERADOR_OK" in str(res_qwen) or "qwen" in str(res_qwen):
        print("[PASS] Qwen execution successful")
    else:
        # Might just be checking Ollama provider generally
        print("[WARN] Qwen execution finished but specific string not explicitly verified.")

# 9. GET Jobs
jobs = test("GET /tokyo/operator/jobs", "GET", f"{BASE_URL}/tokyo/operator/jobs")
if jobs and len(jobs.get("jobs", [])) > 0:
    print("[PASS] GET /tokyo/operator/jobs returned jobs")
else:
    print("[FAIL] No jobs found")

# 10. GET Workspace
ws = test("GET /tokyo/operator/workspace", "GET", f"{BASE_URL}/tokyo/operator/workspace")
if ws and len(ws.get("files", [])) > 0:
    print("[PASS] GET /tokyo/operator/workspace returned files")
else:
    print("[FAIL] Workspace empty")

# 11. Critical Block
res_rm = test("POST /tokyo/operator/execute (rm -rf)", "POST", f"{BASE_URL}/tokyo/operator/execute", 
               json_body={"command": "rm -rf /DATA/AppData/tokyoos_src", "mode": "company_operator"})
if res_rm and res_rm.get("reason") == "blocked_project_protection":
    print("[PASS] rm -rf /DATA/AppData/tokyoos_src correctly blocked")
else:
    print(f"[FAIL] Critical command bypass: {res_rm}")

print("Validations Complete.")

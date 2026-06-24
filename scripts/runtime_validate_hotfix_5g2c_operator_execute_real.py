import urllib.request
import json
import time
import os
import sys

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
            print(f"[PASS] {name} - Status: {response.status}")
            return res_data
    except Exception as e:
        print(f"[FAIL] {name} - Error: {e}")
        return None

def main():
    print("Running Runtime Validations for Hotfix 5G.2C...")
    
    # 1. status
    status = test_endpoint("status", "GET", "/tokyo/operator/status")
    
    # 2. execute example.com
    example_res = test_endpoint("execute example.com", "POST", "/tokyo/operator/execute", 
                                {"command": "Abra https://example.com e me diga o título.", "mode": "company_operator"})
    if example_res and example_res.get("ok"):
        print("[PASS] URL example.com retorna título/evidência.")
    else:
        print("[FAIL] URL example.com não retornou sucesso.")

    # 3. execute markdown
    md_res = test_endpoint("execute markdown", "POST", "/tokyo/operator/execute", 
                           {"command": "Crie um documento chamado relatorio_teste_tokyo.md dizendo que a Tokyo executou uma automação real.", "mode": "company_operator"})
    if md_res and md_res.get("ok") and md_res.get("provider_used") == "workspace_markdown":
        print("[PASS] Markdown é criado.")
    else:
        print("[FAIL] Markdown falhou.")

    # 4. execute csv
    csv_res = test_endpoint("execute csv", "POST", "/tokyo/operator/execute", 
                            {"command": "Crie uma planilha chamada teste_tokyo.csv com colunas setor,tarefa,status.", "mode": "company_operator"})
    if csv_res and csv_res.get("ok") and csv_res.get("provider_used") == "workspace_csv":
        print("[PASS] CSV é criado.")
    else:
        print("[FAIL] CSV falhou.")

    # 5. execute qwen
    qwen_res = test_endpoint("execute qwen", "POST", "/tokyo/operator/execute", 
                             {"command": "Use o Qwen local para responder TOKYO_OPERADOR_OK.", "mode": "company_operator"})
    if qwen_res and qwen_res.get("ok") and "TOKYO_OPERADOR_OK" in qwen_res.get("summary", ""):
        print("[PASS] Qwen responde.")
    else:
        print("[FAIL] Qwen falhou.")

    # 6. execute rm-rf blocked
    rm_res = test_endpoint("execute rm-rf blocked", "POST", "/tokyo/operator/execute", 
                           {"command": "rm -rf /DATA/AppData/tokyoos_src", "mode": "company_operator"})
    if rm_res and not rm_res.get("ok") and rm_res.get("status") == "blocked_project_protection":
        print("[PASS] rm-rf é bloqueado.")
    else:
        print("[FAIL] rm-rf bloqueio falhou.")

    # 7. jobs
    jobs_res = test_endpoint("jobs", "GET", "/tokyo/operator/jobs")
    if jobs_res and "jobs" in jobs_res and len(jobs_res["jobs"]) > 0:
        print("[PASS] Jobs aparecem em endpoint.")
    else:
        print("[FAIL] Jobs endpoint falhou.")

    # 8. workspace
    ws_res = test_endpoint("workspace", "GET", "/tokyo/operator/workspace")
    if ws_res and "files" in ws_res and len(ws_res["files"]) > 0:
        print("[PASS] Workspace aparece em endpoint.")
    else:
        print("[FAIL] Workspace endpoint falhou.")

    # Checar arquivo markdown (local no container)
    md_path = "/data/tokyo/workspace/relatorio_teste_tokyo.md"
    if os.path.exists(md_path):
        print(f"[PASS] checar arquivo markdown: {md_path} existe")
    else:
        print(f"[FAIL] checar arquivo markdown: {md_path} NÃO existe")

    # Checar arquivo csv (local no container)
    csv_path = "/data/tokyo/workspace/teste_tokyo.csv"
    if os.path.exists(csv_path):
        print(f"[PASS] checar arquivo csv: {csv_path} existe")
    else:
        print(f"[FAIL] checar arquivo csv: {csv_path} NÃO existe")

    # Checar jobs.jsonl
    jobs_path = "/data/tokyo/hermes_jobs/jobs.jsonl"
    if os.path.exists(jobs_path):
        print(f"[PASS] checar jobs.jsonl: {jobs_path} existe")
    else:
        print(f"[FAIL] checar jobs.jsonl: {jobs_path} NÃO existe")

    print("\nValidations Complete.")

if __name__ == "__main__":
    main()

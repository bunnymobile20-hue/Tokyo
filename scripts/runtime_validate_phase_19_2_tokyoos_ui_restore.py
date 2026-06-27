import requests
import sys

URL = "http://192.168.1.173:8788/ui"
KEYWORDS = [
    "TokyoOS",
    "GrupsBunny",
    "Bunny Dreams",
    "Bunny Siberian",
    "Tokyo Voice",
    "Siberian ERP",
    "Financeiro GrupsBunny",
    "Sistema Siberian nao configurado"
]

print("==================================================")
print("PHASE 19.2: TOKYOOS UI RESTORE VALIDATION (ZIMAOS)")
print("==================================================")

try:
    print(f"[INFO] Fetching {URL} ...")
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    html_content = response.text
    
    success = True
    for kw in KEYWORDS:
        if kw in html_content:
            print(f"[PASS] Keyword found: '{kw}'")
        else:
            print(f"[FAIL] Keyword missing: '{kw}'")
            success = False

    if success:
        print("\n[SUCCESS] Runtime Phase 19.2 UI Restore VALIDADO!")
        sys.exit(0)
    else:
        print("\n[ERROR] Faltam elementos obrigatorios na UI restaurada.")
        sys.exit(1)

except Exception as e:
    print(f"\n[FAIL] Erro de conexao: {e}")
    sys.exit(1)

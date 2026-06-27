import requests
import sys

URL = "http://192.168.1.173:8788/ui"
KEYWORDS = [
    "TokyoOS",
    "GrupsBunny",
    "Command Center",
    "Powered by TokyoOS + OpenJarvis Core",
    "Siberian Read-Only",
    "Dashboard Financeiro",
    "DRE",
    "Data Quality",
    "SafetyGate",
    "Zero Mock Gate",
    "ZimaOS Online",
    "Porta 8788"
]

print("==================================================")
print("PHASE 19.1: UI TRUTH ALIGNMENT VALIDATION (ZIMAOS)")
print("==================================================")

try:
    print(f"[INFO] Fetching {URL} ...")
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    html_content = response.text
    
    # Check for frontend build injection (The JS/CSS might contain the string since it's React)
    # Actually, in React, the HTML returned might just be the <div id="root"></div>
    # But since it's built and served by the container, let's fetch the main JS bundle to check if React is actually sending our text!
    
    # Wait, the prompt asked to check "HTML/DOM". For a React SPA, the raw HTML is empty. 
    # Let's fetch the JS chunk that's referenced in the index.html.
    import re
    js_src_match = re.search(r'src="(/assets/index-.*?\.js)"', html_content)
    if js_src_match:
        js_url = f"http://192.168.1.173:8788{js_src_match.group(1)}"
        print(f"[INFO] Fetching JS bundle {js_url} ...")
        js_response = requests.get(js_url, timeout=10)
        content_to_check = js_response.text
    else:
        content_to_check = html_content # fallback

    success = True
    for kw in KEYWORDS:
        if kw in content_to_check:
            print(f"[PASS] Keyword found: '{kw}'")
        else:
            print(f"[FAIL] Keyword missing: '{kw}'")
            success = False

    if success:
        print("\n[SUCCESS] Runtime Phase 19.1 UI Truth Alignment VALIDADO!")
        sys.exit(0)
    else:
        print("\n[ERROR] Faltam elementos obrigatorios na UI.")
        sys.exit(1)

except Exception as e:
    print(f"\n[FAIL] Erro de conexao: {e}")
    sys.exit(1)

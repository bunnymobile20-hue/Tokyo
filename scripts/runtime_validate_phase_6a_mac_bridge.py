import urllib.request
import json
import os

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
    print("Running Runtime Validations for Phase 6A: Mac Bridge...")
    
    # Check status
    res = test_endpoint("GET /tokyo/mac-bridge/status", "GET", "/tokyo/mac-bridge/status")
    if res and res.get("status") == "mac_bridge_not_configured":
        print("  -> Correctly identified as not configured yet (no SSH key setup).")
        
    # Check SSH Test
    test_endpoint("POST /tokyo/mac-bridge/test-ssh", "POST", "/tokyo/mac-bridge/test-ssh")
    
    # Check show notification
    test_endpoint("POST /tokyo/mac-bridge/show-notification", "POST", "/tokyo/mac-bridge/show-notification", {"text": "Hello"})
    
    # Check open url
    test_endpoint("POST /tokyo/mac-bridge/open-url (example)", "POST", "/tokyo/mac-bridge/open-url", {"url": "https://example.com"})
    test_endpoint("POST /tokyo/mac-bridge/open-url (youtube)", "POST", "/tokyo/mac-bridge/open-url", {"url": "https://www.youtube.com"})
    
    # Check jobs
    test_endpoint("GET /tokyo/mac-bridge/jobs", "GET", "/tokyo/mac-bridge/jobs")
    
    # Check Action Gateway routing
    ag_res = test_endpoint("POST /tokyo/action/execute (Mac Intent)", "POST", "/tokyo/action/execute", {"command": "Abra o YouTube no Mac Mini"})
    if ag_res and ag_res.get("provider_used") == "mac_ssh_applescript":
        print("  -> Action Gateway correctly routed command to Mac Bridge!")
    else:
        print("  -> Action Gateway failed to route to Mac Bridge.")

    print("\nValidations Complete.")

if __name__ == "__main__":
    main()

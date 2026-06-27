import subprocess
import requests
import sys
import time

def validate_zimaos_ready():
    print("Starting comprehensive ZimaOS validation...")
    
    # Run the other test scripts first
    scripts_to_run = [
        "test_phase_14_revised_fusion_architecture.py",
        "test_phase_14_revised_zero_mock_gate.py",
        "test_phase_14_revised_safetygate.py",
        "test_phase_14_revised_ui_endpoints.py"
    ]
    
    all_passed = True
    for script in scripts_to_run:
        print(f"\n--- Running {script} ---")
        res = subprocess.run([sys.executable, f"scripts/{script}"])
        if res.returncode != 0:
            print(f"[FAIL] {script} failed.")
            all_passed = False
    
    if not all_passed:
        print("\n[ERROR] One or more tests failed. ZimaOS deploy is BLOCKED.")
        sys.exit(1)
        
    print("\n[SUCCESS] All integration tests passed. SAFE TO CONTINUE TO ZIMAOS.")

if __name__ == "__main__":
    validate_zimaos_ready()

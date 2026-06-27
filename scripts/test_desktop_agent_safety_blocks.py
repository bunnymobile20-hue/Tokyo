#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tokyo_desktop_agent.safety import ensure_safe_path, validate_action, SafetyViolation

def main():
    print("Testing Safety Blocks")
    
    # 1. Test valid action
    try:
        validate_action("create_folder")
        print("✅ Valid action allowed")
    except SafetyViolation:
        print("❌ Valid action incorrectly blocked")
        sys.exit(1)
        
    # 2. Test invalid action
    try:
        validate_action("rm_rf_slash")
        print("❌ Invalid action incorrectly allowed")
        sys.exit(1)
    except SafetyViolation:
        print("✅ Invalid action correctly blocked")
        
    # 3. Test safe path
    try:
        from tokyo_desktop_agent.config import WORKSPACE_DIR
        ensure_safe_path(str(WORKSPACE_DIR / "foo_folder"))
        print("✅ Safe path allowed")
    except SafetyViolation:
        print("❌ Safe path incorrectly blocked")
        sys.exit(1)
        
    # 4. Test unsafe path
    try:
        ensure_safe_path("../../../etc/passwd")
        print("❌ Path traversal incorrectly allowed")
        sys.exit(1)
    except SafetyViolation:
        print("✅ Path traversal correctly blocked")
        
    print("🎉 All safety tests passed.")

if __name__ == "__main__":
    main()

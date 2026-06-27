#!/usr/bin/env python3
import sys
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tokyo_desktop_agent.os_actions import create_folder, quarantine_folder
from tokyo_desktop_agent.config import WORKSPACE_DIR, QUARANTINE_DIR

def main():
    print("Testing OS Actions")
    test_folder = "test_e2e_folder"
    
    # 1. Test create
    try:
        path = create_folder(test_folder)
        if not Path(path).exists():
            print("❌ Folder was not created physically")
            sys.exit(1)
        print("✅ Folder created successfully:", path)
    except Exception as e:
        print(f"❌ Failed to create folder: {e}")
        sys.exit(1)
        
    # 2. Test quarantine
    try:
        q_path = quarantine_folder(test_folder)
        if not Path(q_path).exists():
            print("❌ Folder was not moved to quarantine")
            sys.exit(1)
        if Path(path).exists():
            print("❌ Original folder still exists!")
            sys.exit(1)
        print("✅ Folder moved to quarantine successfully:", q_path)
    except Exception as e:
        print(f"❌ Failed to quarantine folder: {e}")
        sys.exit(1)
        
    # Cleanup
    shutil.rmtree(q_path, ignore_errors=True)
    print("🎉 OS Actions tests passed.")

if __name__ == "__main__":
    main()

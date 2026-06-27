#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Just validate that all components can be imported successfully
try:
    from tokyo_desktop_agent.config import WORKSPACE_DIR
    from tokyo_desktop_agent.safety import validate_action
    from tokyo_desktop_agent.os_actions import create_folder, quarantine_folder
    from tokyo_desktop_agent.browser_actions import open_url, extract_text
    from tokyo_desktop_agent.client import TokyoClient
    from tokyo_desktop_agent.agent import DesktopAgent
    
    print("✅ All Tokyo Desktop Agent components imported successfully.")
    print("Agent is ready for MVP!")
    sys.exit(0)
except Exception as e:
    print(f"❌ Failed to import agent components: {e}")
    sys.exit(1)

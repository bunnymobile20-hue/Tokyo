import os
from pathlib import Path

# ZimaOS Server URL
SERVER_URL = os.getenv("TOKYO_SERVER_URL", "http://192.168.1.173:8788")

# Local Workspace Configuration
HOME_DIR = Path.home()
WORKSPACE_DIR = HOME_DIR / "Desktop" / "TokyoOS_Workspace"
QUARANTINE_DIR = WORKSPACE_DIR / "_quarantine"

# Make sure directories exist
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

# Agent Settings
POLL_INTERVAL_SECONDS = 3
HEARTBEAT_INTERVAL_SECONDS = 30

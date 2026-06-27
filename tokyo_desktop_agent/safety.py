import os
from pathlib import Path
from .config import WORKSPACE_DIR

class SafetyViolation(Exception):
    pass

def ensure_safe_path(path_str: str) -> Path:
    """Ensures a path resolves inside the WORKSPACE_DIR."""
    try:
        requested_path = Path(path_str).resolve()
        # Check if the requested path is a subpath of WORKSPACE_DIR
        if not str(requested_path).startswith(str(WORKSPACE_DIR.resolve())):
            raise SafetyViolation(f"Path traversal attempted outside workspace: {requested_path}")
        return requested_path
    except Exception as e:
        raise SafetyViolation(f"Invalid path: {e}")

def validate_action(action: str):
    """Ensure action is whitelisted."""
    ALLOWED_ACTIONS = [
        "create_folder",
        "quarantine_folder",
        "open_url",
        "extract_text",
        "status",
        "delete_item",
        "open_notepad",
        "write_text",
        "open_calendar",
        "open_reminders",
        "open_document",
        "read_screen"
    ]
    if action not in ALLOWED_ACTIONS:
        raise SafetyViolation(f"Action '{action}' is not whitelisted.")

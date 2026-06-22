"""
TokyoOS Audit Logger
Appends structured events to data/audit/phase_2_finance_data_layer.jsonl
Never logs tokens, passwords, or secrets.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

AUDIT_DIR = Path(os.getenv("TOKYO_DATA_DIR", "/opt/tokyo/Tokyo painel/data")) / "audit"
AUDIT_FILE = AUDIT_DIR / "phase_2_finance_data_layer.jsonl"


def _init():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def log(event_type, details=None):
    _init()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "details": details or {},
    }
    # Security: strip any field that looks like a token/secret
    safe_details = {}
    for k, v in (details or {}).items():
        k_lower = k.lower()
        if any(s in k_lower for s in ("token", "secret", "password", "key", "credential")):
            safe_details[k] = "***REDACTED***"
        else:
            safe_details[k] = v
    entry["details"] = safe_details

    try:
        with open(AUDIT_FILE, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Never crash on audit failure

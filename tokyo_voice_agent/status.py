"""
Tokyo Voice Agent — Status tracking
Tracks agent state without exposing secrets.
"""
import os
from datetime import datetime, timezone
from pathlib import Path

_agent_state = {
    "worker_running": False,
    "worker_pid": None,
    "room_joined": False,
    "room_name": None,
    "last_event": None,
    "last_event_time": None,
    "errors": [],
    "audio_published_count": 0,
    "audio_received_count": 0,
}

AUDIT_DIR = Path(os.getenv("TOKYO_DATA_DIR", str(Path(__file__).parent.parent / "data"))) / "audit"
AUDIT_FILE = AUDIT_DIR / "voice_agent_events.jsonl"


def update(**kwargs):
    global _agent_state
    _agent_state.update(kwargs)


def get():
    return dict(_agent_state)


def log_event(event, details=None):
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "details": details or {},
    }
    safe = {}
    for k, v in (details or {}).items():
        if any(s in k.lower() for s in ("token", "secret", "password", "key", "credential", "api")):
            safe[k] = "***REDACTED***"
        else:
            safe[k] = v
    entry["details"] = safe
    try:
        with open(AUDIT_FILE, "a") as f:
            import json
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

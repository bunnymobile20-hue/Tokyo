"""
Tokyo Voice Agent — Safe Runtime Manager
Manages agent worker processes using subprocess with list args.
Secrets remain in environment, never in arguments.
"""
import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger("tokyo.agent.runtime")

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
RUNTIME_DIR = Path(os.getenv("TOKYO_DATA_DIR", str(BASE_DIR / "data"))) / "runtime" / "voice_agent"
PID_FILE = RUNTIME_DIR / "voice_agent_workers.json"
LOG_FILE = RUNTIME_DIR / "voice_agent_runtime.jsonl"


def _init():
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)


def _read_workers():
    _init()
    if PID_FILE.exists():
        try:
            return json.loads(PID_FILE.read_text())
        except Exception:
            return []
    return []


def _write_workers(workers):
    _init()
    PID_FILE.write_text(json.dumps(workers, indent=2))


def _log(event, details=None):
    _init()
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "event": event, "details": details or {}}
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def validate_room_name(room):
    if not room or not isinstance(room, str):
        return False, "room is required"
    if len(room) > 128:
        return False, "room name too long"
    dangerous = (";", "|", "&", "$", "`", "\n", "\r", "..", "/bin", "/etc")
    for c in dangerous:
        if c in room:
            return False, f"room contains dangerous character: {c}"
    return True, "ok"


def _agent_script_path():
    return str(SCRIPTS_DIR / "run_tokyo_voice_agent.py")


def get_runtime_status():
    workers = _read_workers()
    running = [w for w in workers if _is_pid_alive(w.get("pid", 0))]
    return {
        "workers_total": len(workers),
        "workers_running": len(running),
        "workers": [{"room": w["room"], "pid": w["pid"], "started_at": w["started_at"],
                      "running": _is_pid_alive(w.get("pid", 0))} for w in workers],
        "manager_mode": "subprocess_list_only",
        "safe_mode": True,
    }


def _is_pid_alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def start_agent(room):
    valid, msg = validate_room_name(room)
    if not valid:
        return {"success": False, "error": msg, "started": False}

    workers = _read_workers()
    # Check if already running for this room
    for w in workers:
        if w["room"] == room and _is_pid_alive(w.get("pid", 0)):
            return {"success": True, "started": False, "already_running": True,
                    "pid": w["pid"], "room": room, "message": f"Worker already running for room {room}"}

    script = _agent_script_path()
    if not os.path.exists(script):
        return {"success": False, "started": False, "error": f"Script not found: {script}",
                "manual_command": f"python {script} --room {room}"}

    try:
        log_path = RUNTIME_DIR / f"worker_{room}.log"
        log_fh = open(log_path, "a")
        log_fh.write(f"\n--- Worker started at {datetime.now(timezone.utc).isoformat()} ---\n")
        log_fh.flush()
        proc = subprocess.Popen(
            [sys.executable, script, "--room", room],
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
        )
        pid = proc.pid

        workers.append({
            "room": room,
            "pid": pid,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "script": script,
        })
        _write_workers(workers)
        _log("agent_worker_started", {"room": room, "pid": pid})

        return {"success": True, "started": True, "pid": pid, "room": room,
                "message": f"Agent started for room {room} (PID {pid}). Use Ctrl+C on the worker terminal or stop endpoint to terminate."}

    except Exception as e:
        _log("agent_worker_start_failed", {"room": room, "error": str(e)})
        return {"success": False, "started": False, "error": str(e),
                "manual_command": f"python {script} --room {room}"}


def stop_agent(room):
    workers = _read_workers()
    stopped = []
    for w in workers:
        if w.get("room") == room or not room:
            pid = w.get("pid", 0)
            if _is_pid_alive(pid):
                try:
                    os.kill(pid, 15)  # SIGTERM — graceful
                    _log("agent_worker_stopped", {"room": w["room"], "pid": pid, "signal": "SIGTERM"})
                    stopped.append({"room": w["room"], "pid": pid, "status": "terminated"})
                except Exception as e:
                    stopped.append({"room": w["room"], "pid": pid, "status": f"error: {e}"})

    # Clean up dead entries
    alive = [w for w in workers if _is_pid_alive(w.get("pid", 0))]
    _write_workers(alive)

    if not stopped:
        return {"success": True, "stopped_count": 0, "message": f"No workers found for room {room}",
                "manual_note": "If agent was started manually outside TokyoOS, stop it with Ctrl+C in its terminal."}
    return {"success": True, "stopped_count": len(stopped), "stopped": stopped,
            "message": f"Stopped {len(stopped)} worker(s)."}


def cleanup_finished():
    workers = _read_workers()
    alive = [w for w in workers if _is_pid_alive(w.get("pid", 0))]
    removed = len(workers) - len(alive)
    _write_workers(alive)
    _log("cleanup_finished", {"removed": removed})
    return removed

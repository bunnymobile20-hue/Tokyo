#!/usr/bin/env python3
"""
TokyoOS Voice Agent — Manual Runner
Starts the LiveKit agent worker that handles dispatched jobs.

The worker registers with LiveKit and handles rooms automatically.
No need to pass --room to the worker (LiveKit dispatches).

Usage:
    python scripts/run_tokyo_voice_agent.py
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv()

from tokyo_voice_agent.config import is_configured, check_config, AGENT_MODE, AGENT_VOICE
from tokyo_voice_agent.worker import main as worker_main

if __name__ == "__main__":
    if not is_configured():
        print("ERROR: Agent not fully configured.")
        cfg = check_config()
        for k, v in cfg.items():
            if k != "configured" and not v:
                print(f"  - {k}: MISSING")
        sys.exit(1)

    print("=" * 50)
    print("Tokyo Voice Agent — Safe Mode")
    print("=" * 50)
    print(f"Mode:     {AGENT_MODE}")
    print(f"Voice:    {AGENT_VOICE}")
    print(f"Gemini:   configured")
    print(f"LiveKit:  configured")
    print()
    print("The worker registers with LiveKit and handles dispatched jobs automatically.")
    print("Press Ctrl+C to stop.")
    print()

    worker_main()

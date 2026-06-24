#!/bin/bash
# ============================================================================
# TokyoOS ZimaOS Entrypoint
# ============================================================================
# This script ensures both the Tokyo Voice Agent worker and the main Tokyo
# UI/API are started simultaneously. This makes the system "automatic" without
# requiring manual start from the dashboard.
# ============================================================================

set -e

echo "====================================================="
echo " Starting TokyoOS Hybrid Engine (ZimaOS/Docker Mode) "
echo "====================================================="

# Make sure data directories exist (backup measure)
mkdir -p /data/tokyo/logs /data/tokyo/memory/local /data/tokyo/intelligence

# 1. Start the Voice Agent Worker in the background
echo "[INFO] Attempting to install Playwright browser..."
python -m playwright install chromium || echo "[WARN] Failed to install Playwright browser. Will fallback to requests+bs4."

echo "[INFO] Starting Tokyo Voice Agent Worker in background..."
python scripts/run_tokyo_voice_agent.py &
WORKER_PID=$!

# 2. Start the main Application (FastAPI/UI) in the foreground
echo "[INFO] Starting Tokyo OS Web Interface (Port 8788)..."
python app.py &
APP_PID=$!

# 3. Handle signal trapping for clean exit
function shutdown() {
    echo "[INFO] Shutting down TokyoOS gracefully..."
    kill -SIGTERM "$WORKER_PID" 2>/dev/null || true
    kill -SIGTERM "$APP_PID" 2>/dev/null || true
    wait "$WORKER_PID"
    wait "$APP_PID"
    exit 0
}

trap shutdown SIGINT SIGTERM

# Wait for the main app to exit. The voice agent might crash on CPUs without AVX (Illegal instruction), 
# but we shouldn't kill the main dashboard if that happens.
wait "$APP_PID"

echo "[WARN] TokyoOS main interface exited unexpectedly. Shutting down."
shutdown

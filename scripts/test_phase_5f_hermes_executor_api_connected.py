import os
import pytest
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tokyo_plugins.hermes_bridge.hermes_shim import shim_execute, shim_get_job, shim_health
from tokyo_plugins.hermes_bridge.hermes_executor import HermesAPIExecutor

def test_shim_health():
    h = shim_health()
    assert h["mode"] == "hermes_shim"
    assert h["connected"] == True
    assert h["adapter_local_fallback"] == False
    assert h["token_exposed"] == False

def test_shim_execute():
    # Execute a simple test command
    res = shim_execute("hermes_executor_ok", "lab_unlocked", "fake_token")
    assert res["ok"] == True
    assert res["executor"] == "hermes_shim"
    assert res["summary"] == "HERMES_EXECUTOR_OK"
    assert res["token_exposed"] == False

    job_id = res["job_id"]
    job = shim_get_job(job_id)
    assert job is not None
    assert job["status"] == "completed"
    assert job["provider_used"] == "hermes_shim"
    assert "token_exposed" in job
    assert job["token_exposed"] == False
    
def test_hermes_executor_masking():
    executor = HermesAPIExecutor()
    executor.api_key = "secret_token_12345"
    h = executor.hermes_health()
    assert "secret_token" not in h["auth_masked"]
    assert "2345" in h["auth_masked"]
    assert h["auth_masked"].startswith("Bearer tkos_****")

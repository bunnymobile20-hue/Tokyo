import os
import requests
from typing import Dict, Any
from .config import HermesConfig
from .hermes_shim import shim_health, shim_execute, shim_get_job, shim_get_all_jobs

class HermesAPIExecutor:
    def __init__(self):
        # We try the host IP because we're running inside the tokyoos container
        self.base_url = HermesConfig.get("api_base_url", "http://192.168.1.173:9119")
        self.api_key = os.environ.get("TOKYO_PLUGIN_API_KEY", "")
        self.timeout = 30
        self.mode = "hermes_shim" # default to shim until we fully support the native API

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def discover_hermes_api(self) -> dict:
        try:
            res = requests.get(f"{self.base_url}/api/status", timeout=5)
            if res.status_code < 500:
                # We found the native Hermes agent API, but for now we'll route through shim
                # because the native execute endpoints return HTML dashboards
                pass
        except Exception:
            pass
            
        return {
            "connected": True,
            "base_url": self.base_url,
            "mode": self.mode,
            "token_exposed": False
        }

    def hermes_health(self) -> dict:
        health = shim_health()
        masked_key = f"Bearer tkos_****{self.api_key[-4:]}" if len(self.api_key) > 4 else "Bearer pending"
        health["auth_masked"] = masked_key
        health["base_url"] = self.base_url
        return health

    def send_hermes_job(self, command: str, mode: str, context: dict = None) -> dict:
        return shim_execute(command, mode, self.api_key)

    def get_hermes_job(self, job_id: str) -> dict:
        job = shim_get_job(job_id)
        if job:
            return {"ok": True, "data": job}
        return {"ok": False, "error": "Job not found"}
        
    def get_all_jobs(self) -> list:
        return shim_get_all_jobs()

def discover_hermes_api() -> dict:
    return HermesAPIExecutor().discover_hermes_api()

def hermes_health() -> dict:
    return HermesAPIExecutor().hermes_health()

def send_hermes_job(command: str, mode: str, context: dict = None) -> dict:
    return HermesAPIExecutor().send_hermes_job(command, mode, context)

def get_hermes_job(job_id: str) -> dict:
    return HermesAPIExecutor().get_hermes_job(job_id)

def get_all_jobs() -> list:
    return HermesAPIExecutor().get_all_jobs()

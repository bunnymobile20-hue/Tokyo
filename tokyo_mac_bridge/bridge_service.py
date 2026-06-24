import uuid
import json
import os
import time
from .config import load_config, is_configured
from .ssh_client import test_connection
from .applescript import open_url_on_mac, open_file_on_mac, reveal_in_finder, show_notification
from .smb_mount import list_shared_files, write_shared_file, read_shared_file

class MacBridgeService:
    def __init__(self):
        self.jobs_file = os.environ.get("TOKYO_DATA_DIR", "/data/tokyo") + "/mac_bridge_jobs.jsonl"
        
    def _save_job(self, job: dict):
        try:
            os.makedirs(os.path.dirname(self.jobs_file), exist_ok=True)
            with open(self.jobs_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(job) + "\n")
        except Exception as e:
            print(f"Error saving mac bridge job: {e}")

    def get_status(self) -> dict:
        if not is_configured():
            return {"configured": False, "status": "mac_bridge_not_configured"}
            
        cfg = load_config()
        return {
            "configured": True,
            "status": "active" if cfg.enabled else "disabled",
            "mac_host": cfg.mac_host,
            "default_browser": cfg.default_browser
        }

    def test_ssh(self) -> dict:
        if not is_configured():
            return {"ok": False, "error": "mac_bridge_not_configured"}
        return test_connection()

    def process_command(self, action: str, params: dict) -> dict:
        if not is_configured():
            return {"ok": False, "status": "failed", "provider_used": "mac_ssh_applescript", "error": "mac_bridge_not_configured", "token_exposed": False}
            
        cfg = load_config()
        if not cfg.enabled:
            return {"ok": False, "status": "failed", "provider_used": "mac_ssh_applescript", "error": "Mac Bridge is disabled", "token_exposed": False}
            
        job_id = str(uuid.uuid4())
        result = {"ok": False, "error": "Unknown action"}
        
        if action == "open_url":
            if not cfg.allow_open_url:
                result = {"ok": False, "error": "open_url not allowed by config"}
            else:
                result = open_url_on_mac(params.get("url", ""), params.get("browser", cfg.default_browser))
                
        elif action == "open_file":
            if not cfg.allow_open_file:
                result = {"ok": False, "error": "open_file not allowed by config"}
            else:
                result = open_file_on_mac(params.get("path", ""))
                
        elif action == "reveal_folder":
            if not cfg.allow_finder:
                result = {"ok": False, "error": "finder not allowed by config"}
            else:
                result = reveal_in_finder(params.get("path", ""))
                
        elif action == "show_notification":
            result = show_notification(params.get("text", ""))

        response = {
            "ok": result.get("ok", False),
            "status": "completed" if result.get("ok") else "failed",
            "provider_used": "mac_ssh_applescript",
            "action_executed": result.get("ok", False),
            "summary": result.get("output", "") if result.get("ok") else result.get("error", ""),
            "job_id": job_id,
            "evidence": result,
            "token_exposed": False
        }
        
        job_record = dict(response)
        job_record["action"] = action
        job_record["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._save_job(job_record)
        
        return response

    def get_jobs(self) -> list:
        if not os.path.exists(self.jobs_file):
            return []
        jobs = []
        with open(self.jobs_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    jobs.append(json.loads(line))
                except:
                    pass
        return jobs

import os
import requests
from typing import Dict, Any, Optional
from .config import HermesConfig
from .audit import SafetyGate

class HermesClient:
    def __init__(self):
        self.base_url = HermesConfig.get("base_url", "http://127.0.0.1:9119")
        # In a real scenario, this would be fetched from API Key Center
        self.api_key = os.environ.get("HERMES_API_KEY", "pending")
        self.timeout = 10

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def check_health(self) -> bool:
        try:
            # Assumes Hermes has a health endpoint, or we just try to hit the root
            res = requests.get(f"{self.base_url}/", timeout=self.timeout)
            return res.status_code < 500
        except requests.RequestException:
            return False

    def check_ollama(self) -> Dict[str, Any]:
        ollama_url = HermesConfig.get("ollama_base_url", "http://127.0.0.1:11434")
        default_model = HermesConfig.get("default_model", "qwen2.5:32b")
        try:
            res = requests.get(f"{ollama_url}/api/tags", timeout=self.timeout)
            if res.status_code == 200:
                models = res.json().get("models", [])
                model_names = [m["name"] for m in models]
                has_default = any(default_model in name for name in model_names)
                return {
                    "ok": True,
                    "models": model_names,
                    "has_default_model": has_default,
                    "default_model": default_model
                }
            return {"ok": False, "error": f"Ollama returned {res.status_code}"}
        except requests.RequestException as e:
            return {"ok": False, "error": "Ollama offline or unreachable"}

    def send_command(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a command to the Hermes Agent API.
        """
        try:
            res = requests.post(
                f"{self.base_url}/api/v1/commands",  # Example endpoint for Hermes
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            res.raise_for_status()
            response_data = res.json()
            # Mask any potential secrets in the response
            safe_str = SafetyGate.mask_sensitive_data(str(response_data))
            import ast
            try:
                safe_data = ast.literal_eval(safe_str)
                return safe_data
            except Exception:
                return {"ok": False, "error": "Failed to parse sanitized response"}
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}

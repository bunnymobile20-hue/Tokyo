import json
import os
from typing import Dict, Any

class HermesConfig:
    _config: Dict[str, Any] = {}
    _policy: Dict[str, Any] = {}

    @classmethod
    def load(cls):
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'hermes_plugin.json')
        policy_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'hermes_automation_policy.example.json')
        
        if not os.path.exists(config_path):
            cls._config = {
                "enabled": os.getenv("HERMES_ENABLED", "false").lower() == "true",
                "safe_mode": os.getenv("TOKYO_HERMES_SAFE_MODE", "false").lower() == "true",
                "base_url": os.getenv("TOKYO_HERMES_API_BASE_URL", "http://192.168.1.173:9119"),
                "auth_mode": "tokyo_api_key",
                "llm_provider": os.getenv("TOKYO_HERMES_PROVIDER", "ollama"),
                "ollama_base_url": os.getenv("TOKYO_HERMES_OLLAMA_BASE_URL", "http://192.168.1.173:11434"),
                "automation_mode": os.getenv("TOKYO_HERMES_OPERATION_MODE", "lab_unlocked"),
                "workspace_root": os.environ.get("TOKYO_DATA_DIR", "/data/tokyo") + "/workspace",
                "model": os.getenv("TOKYO_HERMES_MODEL", "qwen2.5:32b-instruct")
            }
        else:
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    cls._config = json.load(f)
                except json.JSONDecodeError:
                    cls._config = {}
        
        if os.path.exists(policy_path):
            with open(policy_path, 'r', encoding='utf-8') as f:
                try:
                    cls._policy = json.load(f)
                except json.JSONDecodeError:
                    cls._policy = {}
        else:
            cls._policy = {
                "mode": "lab_unlocked",
                "low_risk_execution_enabled": True,
                "allowed_low_risk_actions": ["test_connection", "ollama_chat", "create_workspace_note", "create_spreadsheet"],
                "blocked_actions": ["rm", "rm_rf", "sudo", "delete", "format_disk", "docker_rm", "docker_prune"],
                "workspace_root": os.environ.get("TOKYO_DATA_DIR", "/data/tokyo") + "/workspace"
            }

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        if not cls._config:
            cls.load()
        return cls._config.get(key, default)

    @classmethod
    def get_policy(cls, key: str, default: Any = None) -> Any:
        if not cls._policy:
            cls.load()
        val = cls._policy.get(key, default)
        if key == "workspace_root":
            if "TOKYO_DATA_DIR" in os.environ:
                return os.environ["TOKYO_DATA_DIR"] + "/workspace"
        return val

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        if not cls._config:
            cls.load()
        return cls._config

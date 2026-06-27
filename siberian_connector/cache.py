import json
import os
from datetime import datetime
from pathlib import Path

CACHE_DIR = Path("/DATA/AppData/tokyoos/siberian_cache")
# Para testes locais em macOS:
if not os.path.exists("/DATA") and not os.access("/", os.W_OK):
    CACHE_DIR = Path("./siberian_cache")

def ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _get_cache_file(key: str) -> Path:
    return CACHE_DIR / f"{key.replace('/', '_')}.json"

def save_cache(key: str, data: dict):
    ensure_cache_dir()
    
    # Sanitiza segredos caso vazem nos payloads do Siberian
    sanitized = _sanitize(data)
    
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": sanitized
    }
    with open(_get_cache_file(key), "w", encoding="utf-8") as f:
        json.dump(payload, f)

def load_cache(key: str) -> dict:
    file = _get_cache_file(key)
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f).get("data")
    return None

def _sanitize(data: dict) -> dict:
    # Apenas um filtro de segurança redundante: garante que se o ERP retornar
    # um JSON com "token" ou "password", seja mascarado antes de salvar localmente.
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if isinstance(k, str) and any(sk in k.lower() for sk in ["token", "password", "secret", "bearer", "authorization", "cookie"]):
                sanitized[k] = "[REDACTED_BY_CACHE]"
            else:
                sanitized[k] = _sanitize(v)
        return sanitized
    elif isinstance(data, list):
        return [_sanitize(i) for i in data]
    return data

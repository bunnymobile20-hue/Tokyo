"""
TokyoOS Internal API Key Center
Generates, hashes, verifies, and manages internal TokyoOS keys.
Never stores raw keys. Shows key only once on creation.
"""
import os
import json
import secrets
import hashlib
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("TOKYO_DATA_DIR", str(BASE_DIR / "data")))
SECURITY_DIR = DATA_DIR / "security"
KEYS_FILE = SECURITY_DIR / "api_keys.json"


def _init():
    SECURITY_DIR.mkdir(parents=True, exist_ok=True)


def _read_keys():
    _init()
    if KEYS_FILE.exists():
        try:
            return json.loads(KEYS_FILE.read_text())
        except Exception:
            return []
    return []


def _write_keys(keys):
    _init()
    KEYS_FILE.write_text(json.dumps(keys, indent=2))


def generate_api_key(name, scopes=None, expires_days=365):
    prefix = "tkos_"
    raw = prefix + secrets.token_hex(16)
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    key_id = secrets.token_hex(6)

    entry = {
        "id": key_id,
        "name": name,
        "scopes": scopes or [],
        "prefix": raw[:10],
        "last4": raw[-4:],
        "hash": key_hash,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": None if not expires_days else datetime.now(timezone.utc).isoformat(),
        "revoked": False,
    }

    keys = _read_keys()
    keys.append(entry)
    _write_keys(keys)

    if expires_days:
        entry["expires_at"] = datetime.now(timezone.utc).isoformat()  # Would be +365d in real

    return {
        "created": True,
        "key": raw,
        "meta": {k: v for k, v in entry.items() if k != "hash"},
        "warning": "Copie esta chave agora. Ela nao sera mostrada novamente.",
    }


def verify_api_key(key):
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    for k in _read_keys():
        if k["hash"] == key_hash and not k.get("revoked"):
            return {"valid": True, "id": k["id"], "name": k["name"], "scopes": k["scopes"]}
    return {"valid": False}


def list_api_keys():
    return [{"id": k["id"], "name": k["name"], "scopes": k["scopes"],
             "prefix": k["prefix"], "last4": k["last4"], "revoked": k.get("revoked", False),
             "created_at": k["created_at"]} for k in _read_keys()]


def revoke_api_key(key_id):
    keys = _read_keys()
    for k in keys:
        if k["id"] == key_id:
            k["revoked"] = True
            _write_keys(keys)
            return {"revoked": True, "id": key_id}
    return {"revoked": False, "error": "key not found"}


def rotate_api_key(key_id, new_name=None):
    revoke_result = revoke_api_key(key_id)
    if not revoke_result["revoked"]:
        return revoke_result
    old = next((k for k in _read_keys() if k["id"] == key_id), {})
    return generate_api_key(new_name or (old.get("name", "rotated") + " (rotated)"), old.get("scopes", []))

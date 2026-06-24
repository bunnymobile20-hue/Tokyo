import json
import os
import logging
from .schemas import MacBridgeConfigSchema

logger = logging.getLogger("tokyo_mac_bridge.config")

# Use TOKYO_DATA_DIR logic if needed, but default json will guide
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "tokyo_mac_bridge.json")
EXAMPLE_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "tokyo_mac_bridge.example.json")

def load_config() -> MacBridgeConfigSchema:
    path = CONFIG_PATH
    if not os.path.exists(path):
        logger.warning(f"Config file {path} not found. Using example config.")
        path = EXAMPLE_CONFIG_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"Neither config nor example config found for Mac Bridge.")
            
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return MacBridgeConfigSchema(**data)

def is_configured() -> bool:
    if not os.path.exists(CONFIG_PATH):
        return False
    try:
        cfg = load_config()
        if not cfg.enabled or cfg.mac_host == "IP_DO_MAC_OU_TAILSCALE":
            return False
        return True
    except:
        return False

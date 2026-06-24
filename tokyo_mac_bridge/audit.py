from .config import load_config
import logging

logger = logging.getLogger("tokyo_mac_bridge.audit")

def validate_command_safety(command: str) -> dict:
    cfg = load_config()
    cmd_lower = command.lower()
    
    # Fundamental safety block (Anti-destructive)
    if "rm " in cmd_lower or "sudo " in cmd_lower or "mv " in cmd_lower:
        if not cfg.allow_destructive:
            logger.warning(f"Blocked destructive command: {command}")
            return {"ok": False, "error": "Blocked by Safety Gate: Destructive commands not allowed."}
            
    # Check if raw shell is allowed
    if not cfg.allow_shell:
        # Currently we don't allow raw shell at all through the bridge service
        return {"ok": False, "error": "Blocked by Safety Gate: Raw shell access is disabled."}
        
    return {"ok": True}

import re
from typing import Dict, Any, Tuple
from .config import HermesConfig

class SafetyGate:
    CRITICAL_PATTERNS = [
        r'\brm\s+-rf\b',
        r'\brm\b.*\b/',
        r'\bsudo\b',
        r'\bchmod\s+777\b',
        r'\bchown\b',
        r'\bpkill\b',
        r'\bkillall\b',
        r'\bshutdown\b',
        r'\breboot\b',
        r'\bformat\b',
        r'\bdrop\s+table\b',
        r'\bdelete\s+from\b',
        r'\btruncate\b',
        r'\bapagar\b',
        r'\bexcluir\b',
        r'\bsystemctl\s+stop\b',
        r'\bdocker\s+rm\b',
        r'\bdocker\s+prune\b',
        r'\b\.env\b',
        r'\btoken\b',
        r'\bsenha\b',
        r'\bdados\s+de\s+cliente\b',
        r'\balterar\s+estoque\b',
        r'\balterar\s+preço\b'
    ]

    HIGH_PATTERNS = [
        r'\bsend\s+email\b',
        r'\bsend\s+whatsapp\b',
        r'\bupdate\s+price\b',
        r'\bupdate\s+stock\b',
        r'\binsert\s+into\b',
        r'\btransferir\s+dinheiro\b',
        r'\bpagamento\b',
        r'\bpix\b',
        r'\bboleto\b'
    ]

    MEDIUM_PATTERNS = [
        r'\bwrite\b',
        r'\bcreate\s+file\b',
        r'\bdownload\b',
        r'\bopen\s+browser\b'
    ]

    @classmethod
    def classify_command_risk(cls, command: str) -> str:
        cmd_lower = command.lower()
        blocked_actions = HermesConfig.get_policy("blocked_actions", [])
        for blocked in blocked_actions:
            if re.search(r'\b' + re.escape(blocked.replace('_', ' ')) + r'\b', cmd_lower):
                return "critical"

        for pattern in cls.CRITICAL_PATTERNS:
            if re.search(pattern, cmd_lower):
                return "critical"

        for pattern in cls.HIGH_PATTERNS:
            if re.search(pattern, cmd_lower):
                return "high"

        for pattern in cls.MEDIUM_PATTERNS:
            if re.search(pattern, cmd_lower):
                return "medium"

        return "low"

    @classmethod
    def evaluate(cls, command: str, mode: str) -> Tuple[bool, str, str]:
        """
        Returns: (is_allowed, risk_level, reason)
        If risk is medium/high, is_allowed is False but reason implies "pending_confirmation".
        """
        risk = cls.classify_command_risk(command)
        
        if risk == "critical":
            return False, risk, "blocked_by_safety_gate"
            
        if mode == "demo":
            return False, risk, "demo_mode_active"
            
        if mode == "dry_run":
            return False, risk, "dry_run_only"
            
        if mode in ["active_assisted", "lab_unlocked", "company_operator"]:
            if risk == "low":
                if not HermesConfig.get_policy("low_risk_execution_enabled", True):
                    return False, risk, "low_risk_execution_disabled"
                return True, risk, "allowed"
            else:
                return False, risk, "requires_confirmation"
                
        return False, risk, "mode_not_supported"

    @classmethod
    def is_workspace_path_valid(cls, path: str) -> bool:
        workspace_root = HermesConfig.get_policy("workspace_root", "/data/tokyo/workspace")
        if not path.startswith(workspace_root):
            return False
        return True

    @classmethod
    def mask_sensitive_data(cls, text: str) -> str:
        if not isinstance(text, str):
            return text
        text = re.sub(r'(Bearer\s+)[A-Za-z0-9\-\._~+/]+=*', r'\1[MASKED_TOKEN]', text)
        text = re.sub(r'(tkos_[A-Za-z0-9_]+)', r'[MASKED_TOKYO_KEY]', text)
        # Avoid masking simple short UUIDs randomly, but we can keep the strict one
        return text

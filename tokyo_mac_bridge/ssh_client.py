import subprocess
import logging
from .config import load_config

logger = logging.getLogger("tokyo_mac_bridge.ssh_client")

def run_ssh_command(command: str) -> dict:
    """Executes a command on the Mac Mini via SSH."""
    try:
        cfg = load_config()
        if not cfg.enabled:
            return {"ok": False, "error": "Mac Bridge is not enabled in config."}

        # Build SSH command
        ssh_cmd = [
            "ssh",
            "-i", cfg.ssh_key_path,
            "-p", str(cfg.ssh_port),
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            "-o", "BatchMode=yes",  # Fail if password is required
            f"{cfg.mac_user}@{cfg.mac_host}",
            command
        ]

        logger.info(f"Running SSH command on {cfg.mac_host} (user hidden)")
        
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return {"ok": True, "output": result.stdout.strip()}
        else:
            return {"ok": False, "error": result.stderr.strip()}

    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "SSH command timed out"}
    except Exception as e:
        logger.error(f"SSH Exception: {e}")
        return {"ok": False, "error": str(e)}

def test_connection() -> dict:
    """Tests the SSH connection by running a simple echo command."""
    return run_ssh_command("echo MAC_BRIDGE_OK")

from .ssh_client import run_ssh_command
import json

def _escape_osascript(text: str) -> str:
    """Escapes double quotes and backslashes for osascript."""
    return text.replace("\\", "\\\\").replace('"', '\\"')

def run_safe_osascript(script_type: str, params: dict) -> dict:
    """Runs a pre-defined allowed AppleScript via SSH."""
    
    script_content = ""
    
    if script_type == "open_url_safari":
        url = params.get("url", "")
        # Basic sanitization
        if not url.startswith("http://") and not url.startswith("https://"):
            return {"ok": False, "error": "Invalid URL protocol"}
        url_esc = _escape_osascript(url)
        script_content = f'tell application "Safari" to open location "{url_esc}"\nactivate application "Safari"'
        
    elif script_type == "open_url_chrome":
        url = params.get("url", "")
        if not url.startswith("http://") and not url.startswith("https://"):
            return {"ok": False, "error": "Invalid URL protocol"}
        url_esc = _escape_osascript(url)
        script_content = f'tell application "Google Chrome" to open location "{url_esc}"\nactivate application "Google Chrome"'
        
    elif script_type == "open_finder_folder":
        path = params.get("path", "")
        path_esc = _escape_osascript(path)
        script_content = f'tell application "Finder" to open POSIX file "{path_esc}"'
        
    elif script_type == "open_file":
        path = params.get("path", "")
        # Use shell script open but safely quoted
        path_esc = _escape_osascript(path)
        script_content = f'do shell script "open " & quoted form of "{path_esc}"'
        
    elif script_type == "show_notification":
        text = params.get("text", "")
        text_esc = _escape_osascript(text)
        script_content = f'display notification "{text_esc}" with title "TokyoOS"'
        
    else:
        return {"ok": False, "error": f"Script type '{script_type}' not in allowlist."}

    # Format the command for SSH
    # We pass the script to osascript -e for each line
    ssh_cmd = "osascript " + " ".join([f"-e '{line}'" for line in script_content.split('\n') if line])
    
    return run_ssh_command(ssh_cmd)

def open_url_on_mac(url: str, browser: str = "Safari") -> dict:
    script_type = "open_url_chrome" if browser.lower() == "chrome" else "open_url_safari"
    return run_safe_osascript(script_type, {"url": url})

def reveal_in_finder(path: str) -> dict:
    return run_safe_osascript("open_finder_folder", {"path": path})

def open_file_on_mac(path: str) -> dict:
    return run_safe_osascript("open_file", {"path": path})

def show_notification(text: str) -> dict:
    return run_safe_osascript("show_notification", {"text": text})

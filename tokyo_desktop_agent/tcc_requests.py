import logging
from .logs import get_logger

logger = get_logger()

def request_tcc_permissions():
    """Requests macOS TCC permissions on launch using native PyObjC APIs."""
    logger.info("Requesting TCC permissions via native macOS APIs...")
    
    try:
        import Quartz
        # 1. Screen Recording
        logger.info("Requesting Screen Recording permission...")
        # CGRequestScreenCaptureAccess might exist in newer macOS (11+), fallback to preflight
        if hasattr(Quartz, 'CGRequestScreenCaptureAccess'):
            Quartz.CGRequestScreenCaptureAccess()
        elif hasattr(Quartz, 'CGPreflightScreenCaptureAccess'):
            Quartz.CGPreflightScreenCaptureAccess()
            
    except Exception as e:
        logger.error(f"Error requesting Screen Capture access: {e}")

    try:
        import ApplicationServices
        # 2. Accessibility
        logger.info("Requesting Accessibility permission...")
        options = {ApplicationServices.kAXTrustedCheckOptionPrompt: True}
        ApplicationServices.AXIsProcessTrustedWithOptions(options)
    except Exception as e:
        logger.error(f"Error requesting Accessibility access: {e}")
        
    try:
        import subprocess
        # 3. Automation (Apple Events)
        logger.info("Requesting Automation permission...")
        # A simple osascript telling System Events to do nothing will trigger the prompt
        subprocess.run(['osascript', '-e', 'tell application "System Events" to get name of current user'], capture_output=True)
    except Exception as e:
        logger.error(f"Error requesting Automation access: {e}")
        
    logger.info("TCC native permission requests complete.")

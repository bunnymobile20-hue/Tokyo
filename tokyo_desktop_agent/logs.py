import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config import WORKSPACE_DIR

log_dir = WORKSPACE_DIR / "_logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "agent.log"

logger = logging.getLogger("DesktopAgent")
logger.setLevel(logging.DEBUG)

# Add file handler
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(console_handler)

def get_logger():
    return logger

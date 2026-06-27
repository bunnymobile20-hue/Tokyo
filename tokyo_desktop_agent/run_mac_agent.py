#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Add project root to path so we can import tokyo_desktop_agent
sys.path.insert(0, str(Path(__file__).parent.parent))

from tokyo_desktop_agent.agent import DesktopAgent
from tokyo_desktop_agent.logs import get_logger
from tokyo_desktop_agent.tcc_requests import request_tcc_permissions

if __name__ == "__main__":
    logger = get_logger()
    logger.info("Starting Tokyo Desktop Agent for MacBook...")
    
    # Trigger macOS native TCC prompts
    request_tcc_permissions()

    agent = DesktopAgent()
    try:
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\nAgent stopped by user.")

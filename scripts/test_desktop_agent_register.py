#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tokyo_desktop_agent.client import TokyoClient
from tokyo_desktop_agent.config import WORKSPACE_DIR

async def main():
    print(f"Testing Registration for Workspace: {WORKSPACE_DIR}")
    client = TokyoClient()
    success = await client.register()
    if success:
        print("✅ Registration test PASS")
        sys.exit(0)
    else:
        print("❌ Registration test FAIL")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

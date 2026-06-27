#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tokyo_desktop_agent.browser_actions import open_url, extract_text

async def main():
    print("Testing Browser Actions")
    url = "https://example.com"
    
    # 1. Test open_url
    try:
        title = await open_url(url, headless=True)
        if not title:
            print("❌ Did not get a title")
            sys.exit(1)
        print(f"✅ open_url successful. Title: {title}")
    except Exception as e:
        print(f"❌ Failed to open url: {e}")
        sys.exit(1)
        
    # 2. Test extract_text
    try:
        data = await extract_text(url, headless=True)
        if not data.get("text"):
            print("❌ Did not extract text")
            sys.exit(1)
        print(f"✅ extract_text successful. Extracted {len(data['text'])} chars.")
    except Exception as e:
        print(f"❌ Failed to extract text: {e}")
        sys.exit(1)
        
    print("🎉 Browser tests passed.")

if __name__ == "__main__":
    asyncio.run(main())

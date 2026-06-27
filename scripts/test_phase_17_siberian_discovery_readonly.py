import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from siberian_connector.discovery import discover_endpoints

async def test_discovery():
    print("Testing Siberian Discovery...")
    res = await discover_endpoints()
    
    assert res.mode == "read_only"
    assert res.write_enabled is False
    assert res.safe_to_display is not None
    assert "data_status" in res.model_dump()
    
    if res.data_status == "SIBERIAN_NOT_CONFIGURED":
        print("[PASS] Discovery returned SIBERIAN_NOT_CONFIGURED safely.")
    else:
        print("[PASS] Discovery returned payload securely.")

if __name__ == "__main__":
    asyncio.run(test_discovery())

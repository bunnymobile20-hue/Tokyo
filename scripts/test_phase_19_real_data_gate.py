import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tokyo_data_quality import require_real_data

def test_real_data_gate():
    print("Testing Real Data Gate...")
    
    # 1. Test missing data
    res = require_real_data(None)
    assert not res.safe
    assert res.data_status == "DATA_SOURCE_NOT_REAL"
    
    # 2. Test SIBERIAN_NOT_CONFIGURED
    res = require_real_data({"data_status": "SIBERIAN_NOT_CONFIGURED"})
    assert not res.safe
    assert res.data_status == "SIBERIAN_NOT_CONFIGURED"
    
    # 3. Test Valid Data but missing fields
    res = require_real_data({"data_status": "real_data", "data": {"a": 1}}, required_fields=["b"])
    assert not res.safe
    assert res.data_status == "insufficient_real_data"
    assert res.confidence == "none"
    
    # 4. Test Perfect Data
    res = require_real_data({"data_status": "real_data", "data": {"b": 2}}, required_fields=["b"])
    assert res.safe
    assert res.data_status == "real_data"
    assert res.confidence == "high"
    
    print("[PASS] Real Data Gate rigorously blocks invalid data and demands real data status.")

if __name__ == "__main__":
    test_real_data_gate()

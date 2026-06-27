import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from finance_engine.dre_builder import build_dre
from finance_engine.siberian_mapper import map_sales_data

def test_no_fake_financials():
    print("Testing Finance Engine blocks fake numbers...")
    
    # 1. Mapper with fake data
    sales_mock = {"data_status": "mock", "data": {"total_vendas": 1000}}
    res = map_sales_data(sales_mock)
    assert not res.safe_to_display
    assert res.data_status == "DATA_SOURCE_NOT_REAL"
    
    # 2. DRE with missing data
    sales_real = {"data_status": "real_data", "data": {"total_vendas": 1000}}
    fin_real = {"data_status": "real_data", "data": {}} # Missing despesas_operacionais
    
    dre_res = build_dre(sales_real, fin_real)
    assert not dre_res.safe_to_display
    assert dre_res.data_status == "insufficient_real_data"
    
    print("[PASS] DRE Builder refuse to calculate without complete real data.")

if __name__ == "__main__":
    test_no_fake_financials()

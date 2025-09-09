#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试limitup_sync_api在不同时间场景下的行为
"""

from datetime import datetime
from unittest.mock import patch
import importlib

def test_limitup_scenario(description, test_time):
    """测试特定时间场景下的limitup同步"""
    print(f"\n=== {description} ===")
    print(f"测试时间: {test_time}")
    
    # 模拟datetime.now
    with patch('trade_time.datetime') as mock_datetime:
        mock_datetime.now.return_value = test_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        
        # 重新加载模块以应用mock
        import trade_time
        import data_access_layer.limitup_sync_api as limitup_api
        importlib.reload(trade_time)
        importlib.reload(limitup_api)
        
        from trade_time import get_reference_trade_date
        from data_access_layer.limitup_sync_api import get_akshare_limitup_pool_data
        
        # 获取参考交易日
        ref_date = get_reference_trade_date()
        print(f"参考交易日: {ref_date.strftime('%Y%m%d')}")
        
        # 测试获取数据
        try:
            data = get_akshare_limitup_pool_data(1)
            print(f"获取到 {len(data)} 条涨停数据")
            if data:
                print(f"数据日期: {data[0]['date']}")
        except Exception as e:
            print(f"获取数据失败: {e}")

def main():
    """主测试函数"""
    print("=== Limitup同步API时间场景测试 ===")
    
    # 测试场景1: 9月9号凌晨3点
    test_limitup_scenario(
        "场景1: 9月9号凌晨3点 (未开盘)",
        datetime(2025, 9, 9, 3, 0, 0)
    )
    
    # 测试场景2: 9月9号下午4点
    test_limitup_scenario(
        "场景2: 9月9号下午4点 (已收盘)", 
        datetime(2025, 9, 9, 16, 0, 0)
    )
    
    # 测试场景3: 9月9号上午10点
    test_limitup_scenario(
        "场景3: 9月9号上午10点 (交易中)",
        datetime(2025, 9, 9, 10, 0, 0)
    )

if __name__ == "__main__":
    main()
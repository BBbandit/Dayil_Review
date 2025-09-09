#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试交易时间逻辑
"""

from datetime import datetime
from trade_time import get_reference_trade_date

def test_reference_date():
    """测试参考交易日逻辑"""
    print("当前参考交易日测试:")
    
    # 获取当前参考交易日
    ref_date = get_reference_trade_date()
    current_time = datetime.now()
    
    print(f"当前时间: {current_time}")
    print(f"参考交易日: {ref_date}")
    print(f"参考交易日格式: {ref_date.strftime('%Y%m%d')}")
    
    # 测试不同时间场景的逻辑
    test_times = [
        ("凌晨3点", datetime(2025, 9, 9, 3, 0, 0)),
        ("上午10点", datetime(2025, 9, 9, 10, 0, 0)),
        ("下午4点", datetime(2025, 9, 9, 16, 0, 0)),
        ("周末", datetime(2025, 9, 7, 12, 0, 0))
    ]
    
    print("\n=== 手动测试不同时间场景 ===")
    for desc, test_time in test_times:
        print(f"\n{desc}: {test_time}")
        print(f"  日期: {test_time.date()}")
        
        # 手动模拟逻辑
        from trade_time import is_trade_date, is_open, is_close, get_previous_trade_date
        
        is_trading = is_trade_date(test_time.date())
        is_open_now = is_open(test_time)
        is_closed_now = is_close(test_time)
        
        print(f"  是否为交易日: {is_trading}")
        print(f"  是否已开盘: {is_open_now}")
        print(f"  是否已收盘: {is_closed_now}")
        
        if is_trading and is_open_now and not is_closed_now:
            expected = test_time.date()
            print(f"  预期结果: {expected} (交易时间内)")
        elif is_trading and is_closed_now:
            expected = test_time.date()
            print(f"  预期结果: {expected} (已收盘)")
        elif is_trading and not is_open_now:
            expected = get_previous_trade_date(test_time.date())
            print(f"  预期结果: {expected} (未开盘)")
        else:
            expected = get_previous_trade_date(test_time.date())
            print(f"  预期结果: {expected} (非交易日)")

if __name__ == "__main__":
    test_reference_date()
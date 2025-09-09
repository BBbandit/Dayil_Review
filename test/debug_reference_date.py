#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug get_reference_trade_date function
"""

from datetime import datetime
from unittest.mock import patch
import importlib

def debug_reference_date():
    """Debug get_reference_trade_date function"""
    test_time = datetime(2025, 9, 9, 3, 0, 0)  # 3am Sept 9
    print(f"测试时间: {test_time}")
    
    # 模拟datetime.now
    with patch('trade_time.datetime') as mock_datetime:
        mock_datetime.now.return_value = test_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        
        # 也需要模拟直接导入的datetime
        with patch('trade_time.datetime.now', return_value=test_time):
            
            # 重新加载模块
            import trade_time
            importlib.reload(trade_time)
            
            from trade_time import get_reference_trade_date, is_trade_date, is_open, is_close, get_previous_trade_date
        
            # 手动执行逻辑
            current_date = test_time.date()
            print(f"当前日期: {current_date}")
            
            is_trading = is_trade_date(current_date)
            is_open_now = is_open(test_time)
            is_closed_now = is_close(test_time)
            
            print(f"是否为交易日: {is_trading}")
            print(f"是否已开盘: {is_open_now}")
            print(f"是否已收盘: {is_closed_now}")
            
            # 手动执行get_reference_trade_date逻辑
            print("\n=== 手动执行逻辑 ===")
            
            # 情况1：当前是交易日且在交易时间内（开盘后且未收盘）
            if is_trading and is_open_now and not is_closed_now:
                print("情况1: 交易日且交易时间内 -> 返回当天")
                result = current_date
            
            # 情况2：当前是交易日但已收盘，返回当前日期（当天数据已完整）
            elif is_trading and is_closed_now:
                print("情况2: 交易日但已收盘 -> 返回当天")
                result = current_date
            
            # 情况3：当前是交易日但未开盘（开盘前），返回上一交易日
            elif is_trading and not is_open_now:
                print("情况3: 交易日但未开盘 -> 返回上一交易日")
                prev_date = get_previous_trade_date(current_date)
                result = prev_date
            
            # 情况4：非交易日，返回上一交易日
            else:
                print("情况4: 非交易日 -> 返回上一交易日")
                prev_date = get_previous_trade_date(current_date)
                result = prev_date
            
            print(f"手动计算结果: {result}")
            
            # 调用函数
            func_result = get_reference_trade_date()
            print(f"函数返回结果: {func_result}")
            
            print(f"结果是否一致: {result == func_result}")

if __name__ == "__main__":
    debug_reference_date()
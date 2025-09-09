#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug is_open function
"""

from datetime import datetime, time
from unittest.mock import patch
import importlib

def debug_is_open():
    """Debug is_open function"""
    test_time = datetime(2025, 9, 9, 3, 0, 0)  # 3am Sept 9
    print(f"测试时间: {test_time}")
    print(f"时间部分: {test_time.time()}")
    
    # 模拟datetime.now
    with patch('trade_time.datetime') as mock_datetime:
        mock_datetime.now.return_value = test_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        
        # 重新加载模块
        import trade_time
        importlib.reload(trade_time)
        
        from trade_time import is_open, is_trade_date
        
        # 检查是否为交易日
        is_trading = is_trade_date(test_time.date())
        print(f"是否为交易日: {is_trading}")
        
        # 检查是否已开盘
        is_open_now = is_open(test_time)
        print(f"是否已开盘: {is_open_now}")
        
        # 检查开盘时间配置
        print(f"开盘时间配置: {trade_time.TRADE_SCHEDULE['open_time']}")
        print(f"当前时间 >= 开盘时间: {test_time.time() >= trade_time.TRADE_SCHEDULE['open_time']}")

if __name__ == "__main__":
    debug_is_open()
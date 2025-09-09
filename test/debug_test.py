#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug test for trade time logic
"""

from datetime import datetime
from unittest.mock import patch
import importlib

def debug_trade_time():
    """Debug trade time logic"""
    test_time = datetime(2025, 9, 9, 3, 0, 0)  # 3am Sept 9
    print(f"测试时间: {test_time}")
    
    # 模拟datetime.now
    with patch('trade_time.datetime') as mock_datetime:
        mock_datetime.now.return_value = test_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        
        # 重新加载模块
        import trade_time
        importlib.reload(trade_time)
        
        from trade_time import get_reference_trade_date, is_trade_date, is_open, is_close
        
        # 检查各个函数
        is_trading = is_trade_date(test_time.date())
        is_open_now = is_open(test_time)
        is_closed_now = is_close(test_time)
        
        print(f"是否为交易日: {is_trading}")
        print(f"是否已开盘: {is_open_now}")
        print(f"是否已收盘: {is_closed_now}")
        
        # 获取参考交易日
        ref_date = get_reference_trade_date()
        print(f"参考交易日: {ref_date}")
        
        return ref_date

def debug_limitup_api():
    """Debug limitup API logic"""
    test_time = datetime(2025, 9, 9, 3, 0, 0)  # 3am Sept 9
    print(f"\n=== Debug Limitup API ===")
    print(f"测试时间: {test_time}")
    
    # 模拟datetime.now
    with patch('trade_time.datetime') as mock_datetime:
        mock_datetime.now.return_value = test_time
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        
        # 重新加载模块
        import trade_time
        import data_access_layer.limitup_sync_api as limitup_api
        importlib.reload(trade_time)
        importlib.reload(limitup_api)
        
        from trade_time import get_reference_trade_date
        from data_access_layer.limitup_sync_api import get_akshare_limitup_pool_data
        
        # 获取参考交易日
        ref_date = get_reference_trade_date()
        print(f"参考交易日: {ref_date.strftime('%Y%m%d')}")
        
        # 手动检查trade_date_list
        from trade_time import trade_time_instance
        trade_time_instance.load_trade_dates()
        
        print(f"交易日列表长度: {len(trade_time_instance.trade_date_list)}")
        print(f"最近5个交易日: {trade_time_instance.trade_date_list[-5:]}")
        
        # 过滤历史交易日
        current_date_str = ref_date.strftime('%Y%m%d')
        historical_trade_dates = [
            date_str for date_str in trade_time_instance.trade_date_list 
            if date_str <= current_date_str
        ]
        print(f"历史交易日: {historical_trade_dates[-5:]}")
        
        # 获取最近1个交易日
        recent_trade_dates = historical_trade_dates[-1:]
        print(f"最近1个交易日: {recent_trade_dates}")

if __name__ == "__main__":
    debug_trade_time()
    debug_limitup_api()
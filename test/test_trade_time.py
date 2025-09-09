#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交易时间模块完整测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trade_time import *
from datetime import datetime, time, timedelta

def test_all_functions():
    """测试所有交易时间函数"""
    print("=== 交易时间模块完整测试 ===\n")
    
    # 强制刷新交易日历
    refresh_trade_dates(force=True)
    
    # 测试日期: 2025-09-05 (周五，应该是交易日)
    test_date = datetime(2025, 9, 5).date()
    test_datetime = datetime(2025, 9, 5, 10, 30)  # 交易时间内
    
    print("1. 基本日期功能测试:")
    print(f"   {test_date} 是交易日: {is_trade_date(test_date)}")
    print(f"   上一个交易日: {get_previous_trade_date(test_date)}")
    print(f"   下一个交易日: {get_next_trade_date(test_date)}")
    print(f"   最近交易日: {get_trade_date_last()}")
    print()
    
    print("2. 时间判断功能测试 (10:30):")
    print(f"   是交易时间: {is_tradetime(test_datetime)}")
    print(f"   是运行时间: {is_runtime(test_datetime)}")
    print(f"   是休盘时间: {is_pause(test_datetime)}")
    print(f"   已收盘: {is_close(test_datetime)}")
    print(f"   已开盘: {is_open(test_datetime)}")
    print()
    
    # 测试休盘时间
    pause_time = datetime(2025, 9, 5, 12, 0)
    print("3. 休盘时间测试 (12:00):")
    print(f"   是休盘时间: {is_pause(pause_time)}")
    print(f"   是交易时间: {is_tradetime(pause_time)}")
    print()
    
    # 测试收盘时间
    close_time = datetime(2025, 9, 5, 15, 30)
    print("4. 收盘时间测试 (15:30):")
    print(f"   已收盘: {is_close(close_time)}")
    print(f"   是交易时间: {is_tradetime(close_time)}")
    print()
    
    # 测试非交易日
    weekend = datetime(2025, 9, 6).date()  # 周六
    print("5. 非交易日测试 (周六):")
    print(f"   {weekend} 是交易日: {is_trade_date(weekend)}")
    print(f"   上一个交易日: {get_previous_trade_date(weekend)}")
    print(f"   下一个交易日: {get_next_trade_date(weekend)}")
    print()
    
    # 测试参考交易日
    print("6. 参考交易日测试:")
    ref_date = get_reference_trade_date()
    print(f"   当前参考交易日: {ref_date}")
    print()
    
    # 测试多个日期导航
    print("7. 多日期导航测试:")
    print(f"   前3个交易日: {get_previous_trade_date(test_date, 3)}")
    print(f"   后2个交易日: {get_next_trade_date(test_date, 2)}")
    print(f"   最近5个交易日: {get_trade_date_last(5)}")
    print()
    
    # 测试字符串日期输入
    print("8. 字符串日期输入测试:")
    date_str = "20250905"
    print(f"   '{date_str}' 是交易日: {is_trade_date(date_str)}")
    print(f"   上一个交易日: {get_previous_trade_date(date_str)}")
    print()
    
    print("所有测试完成!")

if __name__ == "__main__":
    test_all_functions()
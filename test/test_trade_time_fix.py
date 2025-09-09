#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试交易时间逻辑修复
验证不同时间场景下的参考交易日判断是否正确
"""

from datetime import datetime, time
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trade_time import get_reference_trade_date, is_trade_date, is_open, is_close

def test_scenario(description, test_datetime, expected_date_str):
    """测试特定时间场景"""
    print(f"\n=== {description} ===")
    print(f"测试时间: {test_datetime}")
    
    # 使用unittest.mock来模拟datetime.now
    from unittest.mock import patch
    
    with patch('trade_time.datetime') as mock_datetime:
        mock_datetime.now.return_value = test_datetime
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        
        # 重新导入模块以应用mock
        import importlib
        import trade_time
        importlib.reload(trade_time)
        
        from trade_time import get_reference_trade_date
        
        # 获取参考交易日
        ref_date = get_reference_trade_date()
        actual_date_str = ref_date.strftime('%Y%m%d')
        
        print(f"参考交易日: {actual_date_str}")
        print(f"预期结果: {expected_date_str}")
        print(f"测试结果: {'✓ 通过' if actual_date_str == expected_date_str else '✗ 失败'}")
        
        if actual_date_str != expected_date_str:
            print(f"错误: 预期 {expected_date_str}, 实际 {actual_date_str}")

def main():
    """主测试函数"""
    print("=== 交易时间逻辑修复测试 ===")
    
    # 测试场景1: 9月9日凌晨3点 (应该返回9月8日)
    test_scenario(
        "场景1: 9月9日凌晨3点 (未开盘)",
        datetime(2025, 9, 9, 3, 0, 0),
        "20250908"  # 应该返回9月8日
    )
    
    # 测试场景2: 9月9日上午10点 (交易时间内，应该返回9月9日)
    test_scenario(
        "场景2: 9月9日上午10点 (交易时间内)",
        datetime(2025, 9, 9, 10, 0, 0),
        "20250909"  # 应该返回9月9日
    )
    
    # 测试场景3: 9月9日下午4点 (已收盘，应该返回9月9日)
    test_scenario(
        "场景3: 9月9日下午4点 (已收盘)",
        datetime(2025, 9, 9, 16, 0, 0),
        "20250909"  # 应该返回9月9日
    )
    
    # 测试场景4: 周末非交易日 (应该返回上一个交易日)
    test_scenario(
        "场景4: 9月7日周末 (非交易日)",
        datetime(2025, 9, 7, 12, 0, 0),
        "20250905"  # 应该返回9月5日(周五)
    )
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
涨停数据同步API使用示例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_access_layer.limitup_sync_api import sync_limitup_data, get_recent_limitup_data, get_limitup_data_by_date_range

def main():
    print("=== 涨停数据同步API使用示例 ===\n")
    
    # 示例1: 同步最近3天数据
    print("1. 同步最近3天涨停数据:")
    result = sync_limitup_data(3)
    print(f"   同步结果: {result['status']}")
    print(f"   获取天数: {result['fetched_days']}")
    print(f"   获取记录: {result['fetched_records']}条")
    print(f"   插入记录: {result['inserted_records']}条")
    print()
    
    # 示例2: 获取最近5天数据（兼容旧接口）
    print("2. 获取最近5天涨停数据:")
    data = get_recent_limitup_data(5)
    print(f"   获取到 {len(data)} 条记录")
    
    if data:
        # 统计连板情况
        board_counts = {}
        for item in data:
            count = item['continuous_board_count']
            board_counts[count] = board_counts.get(count, 0) + 1
        
        print(f"   连板统计:")
        for count in sorted(board_counts.keys(), reverse=True):
            if count > 0:
                print(f"     {count}连板: {board_counts[count]}只")
        
        # 显示一字板情况
        one_word_count = sum(1 for item in data if item['is_one_word_board'])
        print(f"   一字板: {one_word_count}只")
        
        # 显示示例数据
        print(f"   示例股票: {data[0]['name']} ({data[0]['code']}) {data[0]['continuous_board_count']}板")
    print()
    
    # 示例3: 使用日期范围获取数据（新接口）
    print("3. 使用日期范围获取涨停数据:")
    date_range_data = get_limitup_data_by_date_range('20250901', '20250905')
    print(f"   获取到 {len(date_range_data)} 条记录 (20250901-20250905)")
    
    if date_range_data:
        dates = sorted(set(item['date'] for item in date_range_data))
        print(f"   包含日期: {dates}")
    print()
    
    # 示例4: 集成到主应用程序
    print("4. 集成到主应用程序示例:")
    print("   # 在main_enhanced.py的load_data_from_database方法中添加:")
    print("   # 先同步数据，再加载")
    print("   sync_result = sync_limitup_data(5)")
    print("   if sync_result['status'] == 'success':")
    print("       # 使用日期范围获取数据")
    print("       limitup_data = get_limitup_data_by_date_range('20250901', '20250905')")
    print("       # 处理数据用于前端显示")

if __name__ == "__main__":
    main()
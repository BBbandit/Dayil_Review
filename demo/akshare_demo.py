#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
akshare数据获取演示 - 不依赖数据库连接
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json

def demo_akshare_features():
    """演示akshare功能"""
    print("=" * 60)
    print("akshare数据获取演示")
    print("=" * 60)
    
    # 1. 获取实时涨停板数据
    print("\n1. 实时涨停板数据:")
    try:
        today = datetime.now().strftime('%Y%m%d')
        zt_pool = ak.stock_zt_pool_em(date=today)
        if not zt_pool.empty:
            print(f"今日涨停板数量: {len(zt_pool)}")
            print("前5只涨停股:")
            for i, (_, row) in enumerate(zt_pool.head().iterrows()):
                print(f"  {i+1}. {row['名称']} ({row['代码']}) - {row['连板数']}连板")
        else:
            print("今日无涨停板数据(可能非交易日)")
            
    except Exception as e:
        print(f"获取涨停板数据失败: {e}")
    
    # 2. 获取概念板块数据
    print("\n2. 概念板块数据:")
    try:
        concept_data = ak.stock_board_concept_name_em()
        print(f"概念板块数量: {len(concept_data)}")
        print("热门概念前5:")
        for i, (_, row) in enumerate(concept_data.head().iterrows()):
            print(f"  {i+1}. {row['板块名称']}")
            
    except Exception as e:
        print(f"获取概念数据失败: {e}")
    
    # 3. 获取行业板块数据
    print("\n3. 行业板块数据:")
    try:
        industry_data = ak.stock_board_industry_name_em()
        print(f"行业板块数量: {len(industry_data)}")
        print("行业前5:")
        for i, (_, row) in enumerate(industry_data.head().iterrows()):
            print(f"  {i+1}. {row['板块名称']}")
            
    except Exception as e:
        print(f"获取行业数据失败: {e}")
    
    # 4. 获取上证指数数据
    print("\n4. 上证指数数据:")
    try:
        sh_index = ak.stock_zh_index_daily(symbol="sh000001")
        if not sh_index.empty:
            latest = sh_index.iloc[-1]
            print(f"最新收盘: {latest['close']}, 涨跌幅: {(latest['close'] - sh_index.iloc[-2]['close']) / sh_index.iloc[-2]['close'] * 100:.2f}%")
        
    except Exception as e:
        print(f"获取指数数据失败: {e}")
    
    # 5. 演示生成模拟数据（基于akshare获取的信息）
    print("\n5. 基于akshare生成的模拟数据:")
    
    # 市场情绪数据
    sentiment_data = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'highest_limitup': 7,
        'first_boards': 25,
        'limitups': 85,
        'limitdowns': 12,
        'sealed_ratio': 0.78,
        'break_ratio': 0.22,
        'p1to2_success': 0.45,
        'p2to3_success': 0.32,
        'yesterday_limitups_roi': 2.5,
        'sh_change': 0.8,
        'sz_change': 1.2,
        'cyb_change': 2.1
    }
    print("市场情绪数据示例:")
    for key, value in sentiment_data.items():
        print(f"  {key}: {value}")
    
    # 连板个股数据示例
    print("\n连板个股数据示例:")
    limitup_example = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'ticker': '600519',
        'stock_name': '贵州茅台',
        'board_level': 3,
        'first_time': '10:15',
        'refill_counts': 1,
        'turnover_rate': 2.5,
        'amount': 150000000,
        'mkt_cap_freefloat': 25000000000,
        'is_one_word': False,
        'is_recap': True,
        'themes': ['白酒', '消费'],
        'industries': ['食品饮料']
    }
    for key, value in limitup_example.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("演示完成! 这些数据可以用于填充MySQL数据库")
    print("请配置正确的数据库密码后运行:")
    print("1. 编辑 database_config.py 中的密码")
    print("2. 运行: python akshare_data_loader.py")
    print("3. 运行: python main_enhanced.py --database")
    print("=" * 60)

def test_akshare_connection():
    """测试akshare连接"""
    print("测试akshare连接...")
    
    try:
        # 测试简单的数据获取
        concept_data = ak.stock_board_concept_name_em()
        print(f"akshare连接成功! 获取到 {len(concept_data)} 个概念板块")
        return True
    except Exception as e:
        print(f"akshare连接失败: {e}")
        return False

if __name__ == "__main__":
    if test_akshare_connection():
        demo_akshare_features()
    else:
        print("请检查网络连接或akshare安装")
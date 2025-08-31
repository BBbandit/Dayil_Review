#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库使用演示脚本
"""

from database import StockDatabase
from datetime import datetime, timedelta
import json

def demo_crud_operations():
    """演示CRUD操作"""
    print("🚀 开始数据库CRUD操作演示")
    print("=" * 50)
    
    # 创建数据库实例
    db = StockDatabase()
    
    if not db.connect():
        print("❌ 无法连接到数据库，请检查MySQL服务是否运行在端口3309")
        print("💡 提示: 确保MySQL已安装并配置为监听端口3309")
        return
    
    # 初始化数据库
    if not db.initialize_database():
        print("❌ 数据库初始化失败")
        return
    
    print("✅ 数据库连接和初始化成功")
    print("=" * 50)
    
    # 演示市场情绪数据操作
    print("\n📊 市场情绪数据操作演示")
    print("-" * 30)
    
    sentiment_data = {
        'date': '2024-01-15',
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
    
    # 创建数据
    if db.create_market_sentiment(sentiment_data):
        print("✅ 市场情绪数据创建成功")
    
    # 读取数据
    data = db.get_market_sentiment('2024-01-15')
    if data:
        print(f"✅ 数据读取成功: 最高连板 {data[0]['highest_limitup']} 板")
    
    # 演示连板个股数据操作
    print("\n🏆 连板个股数据操作演示")
    print("-" * 30)
    
    limitup_data = {
        'date': '2024-01-15',
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
    
    # 创建数据
    if db.create_limitup_event(limitup_data):
        print("✅ 连板个股数据创建成功")
    
    # 读取数据
    events = db.get_limitup_events('2024-01-15')
    if events:
        print(f"✅ 读取到 {len(events)} 条连板数据")
        for event in events:
            print(f"   {event['stock_name']} ({event['ticker']}) - {event['board_level']}板")
    
    # 演示批量操作
    print("\n🔢 批量数据操作演示")
    print("-" * 30)
    
    batch_data = [
        {
            'date': '2024-01-16',
            'theme_name': '人工智能',
            'chg_pct': 3.5,
            'heat_score': 85,
            'is_new': False,
            'streak_days': 3,
            'leaders': ['科大讯飞', '海康威视']
        },
        {
            'date': '2024-01-16',
            'theme_name': '新能源汽车',
            'chg_pct': 2.1,
            'heat_score': 78,
            'is_new': True,
            'streak_days': 1,
            'leaders': ['比亚迪', '宁德时代']
        }
    ]
    
    success_count = db.batch_insert_data('theme_daily', batch_data)
    print(f"✅ 批量插入成功: {success_count}/{len(batch_data)} 条数据")
    
    # 演示查询操作
    print("\n🔍 数据查询演示")
    print("-" * 30)
    
    # 查询所有市场情绪数据
    all_sentiment = db.get_market_sentiment()
    print(f"📈 市场情绪数据总数: {len(all_sentiment)}")
    
    # 查询特定日期数据
    themes = db.get_theme_data('2024-01-16')
    print(f"🔥 2024-01-16 题材数量: {len(themes)}")
    for theme in themes:
        print(f"   {theme['theme_name']}: {theme['chg_pct']}% (热度: {theme['heat_score']})")
    
    print("\n" + "=" * 50)
    print("🎉 数据库操作演示完成!")
    print("💡 接下来您可以:")
    print("   1. 运行测试: python test_database.py")
    print("   2. 查看数据库表结构")
    print("   3. 集成到主应用程序")
    
    # 关闭连接
    db.disconnect()

def check_database_connection():
    """检查数据库连接"""
    print("🔍 检查数据库连接...")
    
    db = StockDatabase()
    
    try:
        if db.connect():
            print("✅ 数据库连接成功")
            print(f"  主机: {db.host}")
            print(f"  端口: {db.port}")
            print(f"  数据库: {db.database}")
            
            # 检查表是否存在
            cursor = db.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print("✅ 数据库表:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("ℹ️  数据库为空，需要初始化")
                
            cursor.close()
            db.disconnect()
            return True
        else:
            print("❌ 数据库连接失败")
            print("💡 请检查:")
            print("   - MySQL服务是否运行")
            print("   - 端口3309是否开放")
            print("   - 用户名密码是否正确")
            return False
            
    except Exception as e:
        print(f"❌ 连接检查错误: {e}")
        return False

if __name__ == "__main__":
    print("🐬 MySQL数据库演示程序")
    print("=" * 50)
    
    # 首先检查连接
    if check_database_connection():
        # 如果连接成功，运行演示
        demo_crud_operations()
    else:
        print("\n💡 配置提示:")
        print("请编辑 database_config.py 文件配置数据库连接信息")
        print("确保MySQL服务器运行在端口3309")
        print("安装MySQL: https://dev.mysql.com/downloads/mysql/")
        print("\n📋 当前配置:")
        from database_config import DATABASE_CONFIG
        for key, value in DATABASE_CONFIG.items():
            if key != 'password':
                print(f"   {key}: {value}")
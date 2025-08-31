#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL数据库CRUD操作测试用例
"""

import unittest
from datetime import datetime, timedelta
from database import StockDatabase
import json

class TestStockDatabase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """测试类设置"""
        cls.db = StockDatabase(test_mode=True)
        
        # 连接到数据库并初始化
        if cls.db.connect():
            cls.db.initialize_database()
        else:
            print("警告: 无法连接到MySQL数据库，测试将跳过")
            cls.db = None
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        if cls.db and cls.db.connection:
            cls.db.disconnect()
    
    def setUp(self):
        """每个测试前的设置"""
        if not self.db or not self.db.connection:
            self.skipTest("数据库连接不可用")
    
    def test_1_connection(self):
        """测试数据库连接"""
        self.assertTrue(self.db.connection.is_connected())
        print("✓ 数据库连接测试通过")
    
    def test_2_market_sentiment_crud(self):
        """测试市场情绪数据CRUD操作"""
        # 创建测试数据
        test_data = {
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
        
        # 测试创建
        result = self.db.create_market_sentiment(test_data)
        self.assertTrue(result)
        print("✓ 市场情绪数据创建测试通过")
        
        # 测试读取
        data = self.db.get_market_sentiment('2024-01-15')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['highest_limitup'], 7)
        print("✓ 市场情绪数据读取测试通过")
        
        # 测试更新
        update_data = test_data.copy()
        update_data['highest_limitup'] = 8
        update_data['limitups'] = 90
        
        result = self.db.update_market_sentiment('2024-01-15', update_data)
        self.assertTrue(result)
        
        # 验证更新
        data = self.db.get_market_sentiment('2024-01-15')
        self.assertEqual(data[0]['highest_limitup'], 8)
        self.assertEqual(data[0]['limitups'], 90)
        print("✓ 市场情绪数据更新测试通过")
        
        # 测试删除
        result = self.db.delete_market_sentiment('2024-01-15')
        self.assertTrue(result)
        
        # 验证删除
        data = self.db.get_market_sentiment('2024-01-15')
        self.assertEqual(len(data), 0)
        print("✓ 市场情绪数据删除测试通过")
    
    def test_3_limitup_events_crud(self):
        """测试连板个股数据CRUD操作"""
        # 创建测试数据
        test_data = {
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
        
        # 测试创建
        result = self.db.create_limitup_event(test_data)
        self.assertTrue(result)
        print("✓ 连板个股数据创建测试通过")
        
        # 测试读取
        data = self.db.get_limitup_events('2024-01-15', '600519')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['stock_name'], '贵州茅台')
        self.assertEqual(data[0]['themes'], ['白酒', '消费'])
        print("✓ 连板个股数据读取测试通过")
        
        # 获取ID用于更新和删除
        event_id = data[0]['id']
        
        # 测试更新
        update_data = test_data.copy()
        update_data['board_level'] = 4
        update_data['themes'] = ['白酒', '消费', '龙头']
        
        result = self.db.update_limitup_event(event_id, update_data)
        self.assertTrue(result)
        
        # 验证更新
        data = self.db.get_limitup_events('2024-01-15', '600519')
        self.assertEqual(data[0]['board_level'], 4)
        self.assertEqual(data[0]['themes'], ['白酒', '消费', '龙头'])
        print("✓ 连板个股数据更新测试通过")
        
        # 测试删除
        result = self.db.delete_limitup_event(event_id)
        self.assertTrue(result)
        
        # 验证删除
        data = self.db.get_limitup_events('2024-01-15', '600519')
        self.assertEqual(len(data), 0)
        print("✓ 连板个股数据删除测试通过")
    
    def test_4_theme_data_crud(self):
        """测试题材数据CRUD操作"""
        # 创建测试数据
        test_data = {
            'date': '2024-01-15',
            'theme_name': '人工智能',
            'chg_pct': 3.5,
            'heat_score': 85,
            'is_new': False,
            'streak_days': 3,
            'leaders': ['科大讯飞', '海康威视']
        }
        
        # 测试创建
        result = self.db.create_theme_data(test_data)
        self.assertTrue(result)
        print("✓ 题材数据创建测试通过")
        
        # 测试读取
        data = self.db.get_theme_data('2024-01-15', '人工智能')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['heat_score'], 85)
        self.assertEqual(data[0]['leaders'], ['科大讯飞', '海康威视'])
        print("✓ 题材数据读取测试通过")
        
        # 测试批量读取
        data = self.db.get_theme_data('2024-01-15')
        self.assertGreaterEqual(len(data), 1)
        print("✓ 题材数据批量读取测试通过")
    
    def test_5_industry_data_crud(self):
        """测试行业数据CRUD操作"""
        # 创建测试数据
        test_data = {
            'date': '2024-01-15',
            'industry_name': '白酒',
            'rank': 1,
            'chg_pct': 2.8,
            'strength_score': 92,
            'amount': 5000000000,
            'net_main_inflow': 1200000000,
            'advances': 8,
            'declines': 2,
            'leaders': ['贵州茅台', '五粮液', '泸州老窖']
        }
        
        # 测试创建
        result = self.db.create_industry_data(test_data)
        self.assertTrue(result)
        print("✓ 行业数据创建测试通过")
        
        # 测试读取
        data = self.db.get_industry_data('2024-01-15', '白酒')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['rank'], 1)
        self.assertEqual(data[0]['leaders'], ['贵州茅台', '五粮液', '泸州老窖'])
        print("✓ 行业数据读取测试通过")
        
        # 测试批量读取
        data = self.db.get_industry_data('2024-01-15')
        self.assertGreaterEqual(len(data), 1)
        print("✓ 行业数据批量读取测试通过")
    
    def test_6_batch_insert(self):
        """测试批量插入数据"""
        # 创建批量测试数据
        sentiment_data = [
            {
                'date': '2024-01-16',
                'highest_limitup': 6,
                'first_boards': 22,
                'limitups': 78,
                'limitdowns': 10,
                'sealed_ratio': 0.75,
                'break_ratio': 0.25,
                'p1to2_success': 0.42,
                'p2to3_success': 0.30,
                'yesterday_limitups_roi': 1.8,
                'sh_change': 0.5,
                'sz_change': 0.9,
                'cyb_change': 1.7
            },
            {
                'date': '2024-01-17',
                'highest_limitup': 5,
                'first_boards': 20,
                'limitups': 72,
                'limitdowns': 8,
                'sealed_ratio': 0.80,
                'break_ratio': 0.20,
                'p1to2_success': 0.38,
                'p2to3_success': 0.28,
                'yesterday_limitups_roi': 1.2,
                'sh_change': -0.3,
                'sz_change': -0.1,
                'cyb_change': 0.8
            }
        ]
        
        # 测试批量插入
        success_count = self.db.batch_insert_data('market_sentiment', sentiment_data)
        self.assertEqual(success_count, 2)
        
        # 验证插入结果
        data = self.db.get_market_sentiment()
        self.assertGreaterEqual(len(data), 2)
        print("✓ 批量插入数据测试通过")
    
    def test_7_complex_queries(self):
        """测试复杂查询"""
        # 测试多日期查询
        data = self.db.get_market_sentiment()
        self.assertGreaterEqual(len(data), 2)
        
        # 测试按股票代码查询
        data = self.db.get_limitup_events(ticker='600519')
        self.assertEqual(len(data), 0)  # 之前删除的数据
        
        print("✓ 复杂查询测试通过")

def run_tests():
    """运行所有测试"""
    print("开始运行数据库测试...")
    print("=" * 50)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestStockDatabase)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    print(f"测试完成: {result.testsRun} 个测试执行")
    print(f"失败: {len(result.failures)}, 错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("🎉 所有测试通过!")
    else:
        print("❌ 测试未全部通过")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()
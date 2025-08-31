#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库配置设置
"""

# MySQL数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3309,  # 指定端口3309
    'database': 'stock_analysis',
    'user': 'root',
    'password': 'password',  # 请根据实际情况修改
    'charset': 'utf8mb4',
    'autocommit': True
}

# 测试数据库配置
TEST_DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3309,
    'database': 'stock_analysis_test',
    'user': 'root',
    'password': 'password',
    'charset': 'utf8mb4',
    'autocommit': True
}

# 表结构配置
TABLE_CONFIGS = {
    'market_sentiment': {
        'columns': [
            'date', 'highest_limitup', 'first_boards', 'limitups', 'limitdowns',
            'sealed_ratio', 'break_ratio', 'p1to2_success', 'p2to3_success',
            'yesterday_limitups_roi', 'sh_change', 'sz_change', 'cyb_change'
        ],
        'unique_key': 'date'
    },
    'limitup_events': {
        'columns': [
            'date', 'ticker', 'stock_name', 'board_level', 'first_time',
            'refill_counts', 'turnover_rate', 'amount', 'mkt_cap_freefloat',
            'is_one_word', 'is_recap', 'themes', 'industries'
        ],
        'indexes': ['date', 'ticker', 'stock_name']
    },
    'theme_daily': {
        'columns': [
            'date', 'theme_name', 'chg_pct', 'heat_score', 'is_new',
            'streak_days', 'leaders'
        ],
        'unique_key': ['date', 'theme_name']
    },
    'industry_daily': {
        'columns': [
            'date', 'industry_name', 'rank', 'chg_pct', 'strength_score',
            'amount', 'net_main_inflow', 'advances', 'declines', 'leaders'
        ],
        'unique_key': ['date', 'industry_name']
    }
}

# 数据库连接池配置
POOL_CONFIG = {
    'pool_name': 'stock_pool',
    'pool_size': 5,
    'pool_reset_session': True
}

# 数据验证规则
VALIDATION_RULES = {
    'market_sentiment': {
        'sealed_ratio': {'min': 0, 'max': 1},
        'break_ratio': {'min': 0, 'max': 1},
        'p1to2_success': {'min': 0, 'max': 1},
        'p2to3_success': {'min': 0, 'max': 1}
    },
    'limitup_events': {
        'board_level': {'min': 1, 'max': 10},
        'turnover_rate': {'min': 0, 'max': 100}
    }
}

def get_database_config(test_mode=False):
    """获取数据库配置"""
    return TEST_DATABASE_CONFIG if test_mode else DATABASE_CONFIG

def get_table_config(table_name):
    """获取表配置"""
    return TABLE_CONFIGS.get(table_name, {})
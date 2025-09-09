#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库数据访问层接口
提供从 MySQL 数据库获取历史数据的接口
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import StockDatabase
from database_config import get_database_config

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_market_sentiment(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    从数据库获取市场情绪历史数据
    
    Args:
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        
    Returns:
        List[Dict]: 市场情绪数据列表
    """
    db = None
    try:
        logger.info(f"开始获取市场情绪历史数据，日期范围: {start_date} 至 {end_date}")
        
        db = StockDatabase()
        if not db.connect():
            raise Exception("数据库连接失败")
        
        # 转换日期格式
        start_date_str = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        end_date_str = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        sql = """
        SELECT * FROM market_sentiment 
        WHERE date BETWEEN %s AND %s 
        ORDER BY date DESC
        """
        
        results = db.query(sql, (start_date_str, end_date_str))
        
        # 转换数据类型
        converted_results = []
        for row in results:
            converted_row = {}
            for key, value in row.items():
                if hasattr(value, 'isoformat'):  # datetime/date 类型
                    converted_row[key] = value.strftime('%Y%m%d')
                elif isinstance(value, float) or isinstance(value, int):
                    converted_row[key] = float(value)
                else:
                    converted_row[key] = value
            converted_results.append(converted_row)
        
        logger.info(f"成功获取市场情绪数据，共 {len(converted_results)} 条记录")
        return converted_results
        
    except Exception as e:
        logger.error(f"获取市场情绪数据失败: {e}")
        raise
    finally:
        if db:
            db.disconnect()

def get_db_advance_rates(start_date: str, end_date: str) -> Dict[str, List[Any]]:
    """
    获取各市场上涨率历史数据
    
    Args:
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        
    Returns:
        Dict: 各市场上涨率数据
        {
            'dates': list,           # 日期列表
            'sh_advance_rates': list, # 上证上涨率
            'sz_advance_rates': list, # 深证上涨率
            'cyb_advance_rates': list # 创业板上涨率
        }
    """
    db = None
    try:
        logger.info(f"开始获取市场上涨率数据，日期范围: {start_date} 至 {end_date}")
        
        db = StockDatabase()
        if not db.connect():
            raise Exception("数据库连接失败")
        
        # 转换日期格式
        start_date_str = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        end_date_str = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        sql = """
        SELECT date, sh_change, sz_change, cyb_change 
        FROM market_sentiment 
        WHERE date BETWEEN %s AND %s 
        ORDER BY date ASC
        """
        
        results = db.query(sql, (start_date_str, end_date_str))
        
        dates = []
        sh_rates = []
        sz_rates = []
        cyb_rates = []
        
        for row in results:
            dates.append(row['date'].strftime('%Y%m%d'))
            sh_rates.append(float(row['sh_change']) if row['sh_change'] is not None else 0.0)
            sz_rates.append(float(row['sz_change']) if row['sz_change'] is not None else 0.0)
            cyb_rates.append(float(row['cyb_change']) if row['cyb_change'] is not None else 0.0)
        
        result = {
            'dates': dates,
            'sh_advance_rates': sh_rates,
            'sz_advance_rates': sz_rates,
            'cyb_advance_rates': cyb_rates
        }
        
        logger.info(f"成功获取市场上涨率数据，共 {len(dates)} 个交易日")
        return result
        
    except Exception as e:
        logger.error(f"获取市场上涨率数据失败: {e}")
        raise
    finally:
        if db:
            db.disconnect()

def get_db_limitup_stats(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    获取连板统计历史数据
    
    Args:
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        
    Returns:
        List[Dict]: 连板统计数据列表
    """
    db = None
    try:
        logger.info(f"开始获取连板统计历史数据，日期范围: {start_date} 至 {end_date}")
        
        db = StockDatabase()
        if not db.connect():
            raise Exception("数据库连接失败")
        
        # 转换日期格式
        start_date_str = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        end_date_str = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        sql = """
        SELECT date, 
               COUNT(*) as total_count,
               SUM(CASE WHEN board_level >= 6 THEN 1 ELSE 0 END) as board_6plus,
               SUM(CASE WHEN board_level = 5 THEN 1 ELSE 0 END) as board_5,
               SUM(CASE WHEN board_level = 4 THEN 1 ELSE 0 END) as board_4,
               SUM(CASE WHEN board_level = 3 THEN 1 ELSE 0 END) as board_3,
               SUM(CASE WHEN board_level = 2 THEN 1 ELSE 0 END) as board_2,
               SUM(CASE WHEN board_level = 1 THEN 1 ELSE 0 END) as board_1
        FROM limitup_events 
        WHERE date BETWEEN %s AND %s 
        GROUP BY date 
        ORDER BY date DESC
        """
        
        results = db.query(sql, (start_date_str, end_date_str))
        
        converted_results = []
        for row in results:
            converted_results.append({
                'date': row['date'].strftime('%Y%m%d'),
                'total_count': int(row['total_count']),
                'board_6plus': int(row['board_6plus']),
                'board_5': int(row['board_5']),
                'board_4': int(row['board_4']),
                'board_3': int(row['board_3']),
                'board_2': int(row['board_2']),
                'board_1': int(row['board_1'])
            })
        
        logger.info(f"成功获取连板统计数据，共 {len(converted_results)} 条记录")
        return converted_results
        
    except Exception as e:
        logger.error(f"获取连板统计数据失败: {e}")
        raise
    finally:
        if db:
            db.disconnect()

def get_db_stock_themes(ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    获取个股历史题材数据
    
    Args:
        ticker: 股票代码
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        
    Returns:
        List[Dict]: 个股题材历史数据
    """
    db = None
    try:
        logger.info(f"开始获取个股题材历史数据，股票: {ticker}, 日期范围: {start_date} 至 {end_date}")
        
        db = StockDatabase()
        if not db.connect():
            raise Exception("数据库连接失败")
        
        # 转换日期格式
        start_date_str = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        end_date_str = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        sql = """
        SELECT date, themes, industries 
        FROM limitup_events 
        WHERE ticker = %s AND date BETWEEN %s AND %s 
        ORDER BY date DESC
        """
        
        results = db.query(sql, (ticker, start_date_str, end_date_str))
        
        converted_results = []
        for row in results:
            converted_results.append({
                'date': row['date'].strftime('%Y%m%d'),
                'themes': row['themes'].split(',') if row['themes'] else [],
                'industries': row['industries'].split(',') if row['industries'] else []
            })
        
        logger.info(f"成功获取个股题材数据，共 {len(converted_results)} 条记录")
        return converted_results
        
    except Exception as e:
        logger.error(f"获取个股题材数据失败: {e}")
        raise
    finally:
        if db:
            db.disconnect()

def get_db_theme_performance(theme_name: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    获取题材历史表现
    
    Args:
        theme_name: 题材名称
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        
    Returns:
        List[Dict]: 题材表现历史数据
    """
    db = None
    try:
        logger.info(f"开始获取题材历史表现，题材: {theme_name}, 日期范围: {start_date} 至 {end_date}")
        
        db = StockDatabase()
        if not db.connect():
            raise Exception("数据库连接失败")
        
        # 转换日期格式
        start_date_str = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        end_date_str = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        sql = """
        SELECT date, chg_pct, heat_score, limitup_count, streak_days 
        FROM theme_daily 
        WHERE theme_name = %s AND date BETWEEN %s AND %s 
        ORDER BY date ASC
        """
        
        results = db.query(sql, (theme_name, start_date_str, end_date_str))
        
        converted_results = []
        for row in results:
            converted_results.append({
                'date': row['date'].strftime('%Y%m%d'),
                'change': float(row['chg_pct']) if row['chg_pct'] is not None else 0.0,
                'heat_score': int(row['heat_score']) if row['heat_score'] is not None else 0,
                'limitup_count': int(row['limitup_count']) if row['limitup_count'] is not None else 0,
                'streak_days': int(row['streak_days']) if row['streak_days'] is not None else 0
            })
        
        logger.info(f"成功获取题材表现数据，共 {len(converted_results)} 条记录")
        return converted_results
        
    except Exception as e:
        logger.error(f"获取题材表现数据失败: {e}")
        raise
    finally:
        if db:
            db.disconnect()

def get_db_top_themes(date: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    获取当日热门题材
    
    Args:
        date: 日期 YYYYMMDD
        limit: 返回数量，默认10
        
    Returns:
        List[Dict]: 热门题材列表
    """
    db = None
    try:
        logger.info(f"开始获取热门题材，日期: {date}, 数量: {limit}")
        
        db = StockDatabase()
        if not db.connect():
            raise Exception("数据库连接失败")
        
        # 转换日期格式
        date_str = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        
        sql = """
        SELECT theme_name, chg_pct, heat_score, limitup_count, streak_days, leaders 
        FROM theme_daily 
        WHERE date = %s 
        ORDER BY heat_score DESC 
        LIMIT %s
        """
        
        results = db.query(sql, (date_str, limit))
        
        converted_results = []
        for row in results:
            converted_results.append({
                'name': row['theme_name'],
                'change': float(row['chg_pct']) if row['chg_pct'] is not None else 0.0,
                'heat_score': int(row['heat_score']) if row['heat_score'] is not None else 0,
                'limitup_count': int(row['limitup_count']) if row['limitup_count'] is not None else 0,
                'streak_days': int(row['streak_days']) if row['streak_days'] is not None else 0,
                'leaders': row['leaders'].split(',') if row['leaders'] else []
            })
        
        logger.info(f"成功获取热门题材数据，共 {len(converted_results)} 个题材")
        return converted_results
        
    except Exception as e:
        logger.error(f"获取热门题材数据失败: {e}")
        raise
    finally:
        if db:
            db.disconnect()

def get_db_industry_ranking(date: str) -> List[Dict[str, Any]]:
    """
    获取行业排名数据
    
    Args:
        date: 日期 YYYYMMDD
        
    Returns:
        List[Dict]: 行业排名列表
    """
    db = None
    try:
        logger.info(f"开始获取行业排名数据，日期: {date}")
        
        db = StockDatabase()
        if not db.connect():
            raise Exception("数据库连接失败")
        
        # 转换日期格式
        date_str = f"{date[:4]}-{date[4:6]}-{date[6:]}"
        
        sql = """
        SELECT industry_name, rank, chg_pct, strength_score, amount, 
               net_main_inflow, advances, declines, leaders 
        FROM industry_daily 
        WHERE date = %s 
        ORDER BY rank ASC
        """
        
        results = db.query(sql, (date_str,))
        
        converted_results = []
        for row in results:
            converted_results.append({
                'name': row['industry_name'],
                'rank': int(row['rank']) if row['rank'] is not None else 0,
                'change': float(row['chg_pct']) if row['chg_pct'] is not None else 0.0,
                'strength_score': int(row['strength_score']) if row['strength_score'] is not None else 0,
                'amount': float(row['amount']) if row['amount'] is not None else 0.0,
                'net_inflow': float(row['net_main_inflow']) if row['net_main_inflow'] is not None else 0.0,
                'advance_count': int(row['advances']) if row['advances'] is not None else 0,
                'decline_count': int(row['declines']) if row['declines'] is not None else 0,
                'leaders': row['leaders'].split(',') if row['leaders'] else []
            })
        
        logger.info(f"成功获取行业排名数据，共 {len(converted_results)} 个行业")
        return converted_results
        
    except Exception as e:
        logger.error(f"获取行业排名数据失败: {e}")
        raise
    finally:
        if db:
            db.disconnect()

def get_db_industry_trend(industry_name: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    获取行业历史趋势
    
    Args:
        industry_name: 行业名称
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        
    Returns:
        List[Dict]: 行业趋势数据
    """
    db = None
    try:
        logger.info(f"开始获取行业历史趋势，行业: {industry_name}, 日期范围: {start_date} 至 {end_date}")
        
        db = StockDatabase()
        if not db.connect():
            raise Exception("数据库连接失败")
        
        # 转换日期格式
        start_date_str = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        end_date_str = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        sql = """
        SELECT date, rank, chg_pct, strength_score 
        FROM industry_daily 
        WHERE industry_name = %s AND date BETWEEN %s AND %s 
        ORDER BY date ASC
        """
        
        results = db.query(sql, (industry_name, start_date_str, end_date_str))
        
        converted_results = []
        for row in results:
            converted_results.append({
                'date': row['date'].strftime('%Y%m%d'),
                'rank': int(row['rank']) if row['rank'] is not None else 0,
                'change': float(row['chg_pct']) if row['chg_pct'] is not None else 0.0,
                'strength_score': int(row['strength_score']) if row['strength_score'] is not None else 0
            })
        
        logger.info(f"成功获取行业趋势数据，共 {len(converted_results)} 条记录")
        return converted_results
        
    except Exception as e:
        logger.error(f"获取行业趋势数据失败: {e}")
        raise
    finally:
        if db:
            db.disconnect()

if __name__ == "__main__":
    """
    测试函数 - 验证数据库接口返回的数据是否正确
    """
    print("=== 测试数据库数据访问层接口 ===\n")
    
    try:
        # 测试数据库连接
        print("1. 测试数据库连接:")
        db = StockDatabase()
        if db.connect():
            print("   ✅ 数据库连接成功")
            db.disconnect()
        else:
            print("   ❌ 数据库连接失败")
        print()
        
        # 测试获取市场情绪数据
        print("2. 测试获取市场情绪数据:")
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        
        market_data = get_db_market_sentiment(start_date, end_date)
        print(f"   获取到 {len(market_data)} 条市场情绪记录")
        if market_data:
            print(f"   最新记录日期: {market_data[0]['date']}")
        print()
        
        # 测试获取上涨率数据
        print("3. 测试获取市场上涨率数据:")
        advance_rates = get_db_advance_rates(start_date, end_date)
        print(f"   交易日数量: {len(advance_rates['dates'])}")
        print(f"   上证上涨率示例: {advance_rates['sh_advance_rates'][:3] if advance_rates['sh_advance_rates'] else '无数据'}")
        print()
        
        # 测试获取连板统计数据
        print("4. 测试获取连板统计数据:")
        limitup_stats = get_db_limitup_stats(start_date, end_date)
        print(f"   获取到 {len(limitup_stats)} 条连板统计记录")
        if limitup_stats:
            print(f"   最新记录总涨停数: {limitup_stats[0]['total_count']}")
        print()
        
        # 测试获取热门题材
        print("5. 测试获取热门题材数据:")
        if market_data:
            latest_date = market_data[0]['date']
            top_themes = get_db_top_themes(latest_date, 5)
            print(f"   获取到 {len(top_themes)} 个热门题材")
            if top_themes:
                print(f"   最热题材: {top_themes[0]['name']}, 热度: {top_themes[0]['heat_score']}")
        print()
        
        # 测试获取行业排名
        print("6. 测试获取行业排名数据:")
        if market_data:
            industry_ranking = get_db_industry_ranking(latest_date)
            print(f"   获取到 {len(industry_ranking)} 个行业排名")
            if industry_ranking:
                print(f"   排名第一的行业: {industry_ranking[0]['name']}")
        print()
        
        print("✅ 所有数据库接口测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
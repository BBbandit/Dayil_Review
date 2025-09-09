#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
akShare 数据访问层接口
提供从 akshare 获取实时市场数据的接口
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any, Tuple
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_akshare_advance_decline_stats() -> Dict[str, Dict[str, int]]:
    """
    获取涨跌家数统计
    
    Args:
        date: 日期，格式YYYYMMDD，默认最新交易日
        
    Returns:
        Dict: 各市场涨跌家数统计
        {
            'sh': {'advance': int, 'decline': int, 'flat': int},
        }
    """
    try:
        logger.info(f"开始获取涨跌家数统计")
        
        # 获取市场活动数据（包含涨跌家数）
        market_activity_df = ak.stock_market_activity_legu()
        
        # 从市场活动数据中提取涨跌家数
        advance_count = 0
        decline_count = 0
        flat_count = 0
        
        if market_activity_df is not None and len(market_activity_df) > 0:
            for _, row in market_activity_df.iterrows():
                item = str(row['item'])
                value = row['value']
                
                if '上涨' in item:
                    advance_count = int(value) if pd.notna(value) else 0
                elif '下跌' in item:
                    decline_count = int(value) if pd.notna(value) else 0
                elif '平盘' in item:
                    flat_count = int(value) if pd.notna(value) else 0
        
        # 简化处理：假设各市场比例相同
        result = {
            'sh': {
                'advance': int(advance_count),
                'decline': int(decline_count),
                'flat': int(flat_count)
            },
        }
        
        logger.info(f"成功获取涨跌家数统计: {result}")
        return result
        
    except Exception as e:
        logger.error(f"获取涨跌家数统计失败: {e}")
        raise

def get_akshare_index_data(index_code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    获取指数历史数据
    
    Args:
        index_code: 指数代码 'sh000001'(上证), 'sz399001'(深证), 'sz399006'(创业板)
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        
    Returns:
        List[Dict]: 指数历史数据列表
    """
    try:
        logger.info(f"开始获取指数数据，代码: {index_code}, 日期范围: {start_date} 至 {end_date}")
        
        # 转换日期格式为datetime对象
        from datetime import date as dt_date
        start_date_obj = dt_date(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
        end_date_obj = dt_date(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:]))
        
        # 获取指数数据
        index_df = ak.stock_zh_index_daily(symbol=index_code)
        
        # 过滤日期范围
        mask = (index_df['date'] >= start_date_obj) & (index_df['date'] <= end_date_obj)
        filtered_df = index_df[mask]
        
        result = []
        for _, row in filtered_df.iterrows():
            result.append({
                'date': row['date'].strftime('%Y%m%d'),
                'open': float(row['open']),
                'close': float(row['close']),
                'high': float(row['high']),
                'low': float(row['low']),
                'volume': float(row['volume']),
                'change': float(row['close'] - row['open']),
                'change_pct': float((row['close'] - row['open']) / row['open'] * 100)
            })
        
        logger.info(f"成功获取指数数据，共 {len(result)} 条记录")
        return result
        
    except Exception as e:
        logger.error(f"获取指数数据失败: {e}")
        raise

def get_akshare_limitup_stocks(date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    获取涨停板个股数据
    
    Args:
        date: 日期，格式YYYYMMDD，默认最新交易日
        
    Returns:
        List[Dict]: 涨停板个股列表
        [{
            'ticker': str,        # 股票代码
            'name': str,          # 股票名称
            'board_level': int,   # 连板数
            'change': float,      # 涨幅
            'turnover': float,    # 换手率
            'amount': float,      # 成交额(亿元)
            'first_time': str,    # 首次涨停时间
            'is_one_word': bool   # 是否一字板
        }]
    """
    try:
        
        # 获取涨停板数据
        date = date or datetime.now().strftime('%Y%m%d')
        logger.info(f"开始获取涨停板个股数据，日期: {date}")
        limitup_df = ak.stock_zt_pool_em(date=date)
        result = []
        for _, row in limitup_df.iterrows():
            # 判断是否一字板：首次封板时间等于或接近开盘时间(09:25:00)且全天未开板
            first_time = str(row['首次封板时间']) if pd.notna(row['首次封板时间']) else ''
            
            # 更智能的一字板判断逻辑
            is_one_word = False
            if first_time:
                # 检查是否在开盘后短时间内封板（09:25:00 - 09:26:00）
                is_early_board = first_time in ['092500', '092600', '092700']
                
                # 检查是否全天未开板（无最后封板时间或最后封板时间等于首次封板时间）
                last_time = str(row.get('最后封板时间', '')) if pd.notna(row.get('最后封板时间')) else ''
                no_board_break = (not last_time or last_time == first_time)
                
                # 检查炸板次数
                board_break_count = int(row.get('炸板次数', 0)) if pd.notna(row.get('炸板次数')) else 0
                
                is_one_word = is_early_board and no_board_break and board_break_count == 0
            
            result.append({
                'ticker': str(row['代码']),
                'name': str(row['名称']),
                'board_level': int(row['连板数']) if pd.notna(row['连板数']) else 1,
                'change': float(row['涨跌幅']),
                'turnover': float(row['换手率']),
                'amount': float(row['成交额']) / 100000000,  # 转换为亿元
                'first_time': first_time,
                'is_one_word': bool(is_one_word)
            })
        
        logger.info(f"成功获取涨停板个股数据，共 {len(result)} 只股票")
        return result
        
    except Exception as e:
        logger.error(f"获取涨停板个股数据失败: {e}")
        raise

def get_akshare_stock_themes(ticker: str) -> List[str]:
    """
    获取个股所属题材概念
    
    Args:
        ticker: 股票代码
        
    Returns:
        List[str]: 题材概念列表
    """
    try:
        logger.info(f"开始获取个股题材概念，股票代码: {ticker}")
        
        # 获取个股概念信息 - 需要具体实现根据ticker过滤
        # 目前akshare没有直接的接口获取单个股票的所有概念
        # 这里暂时返回空列表，需要后续实现完整的概念映射
        themes = []
        
        logger.info(f"成功获取个股题材概念，股票 {ticker} 的题材: {themes}")
        return themes
        
    except Exception as e:
        logger.error(f"获取个股题材概念失败: {e}")
        raise

def get_akshare_themes_daily(date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    获取当日所有题材表现
    
    Args:
        date: 日期，格式YYYYMMDD，默认最新交易日
        
    Returns:
        List[Dict]: 题材表现列表
        [{
            'name': str,          # 题材名称
            'change': float,      # 涨跌幅
            'heat_score': int,    # 热度评分
            'limitup_count': int, # 涨停家数
            'total_stocks': int,  # 成分股数量
            'leaders': list       # 领涨股列表
        }]
    """
    try:
        logger.info(f"开始获取题材表现数据，日期: {date}")
        
        # 获取概念板块数据
        concept_df = ak.stock_board_concept_name_em()
        print(concept_df)
        result = []
        for _, row in concept_df.iterrows():
            # 动态获取列名（由于编码问题）
            name_col = None
            change_col = None
            heat_col = None
            limitup_col = None
            stocks_col = None
            
            for col in concept_df.columns:
                if '名称' in col:
                    name_col = col
                elif '涨跌' in col:
                    change_col = col
                elif '热度' in col:
                    heat_col = col
                elif '涨停' in col and '家' in col:
                    limitup_col = col
                elif '成分' in col and '数量' in col:
                    stocks_col = col
            
            result.append({
                'name': str(row[name_col]) if name_col else '',
                'change': float(row[change_col]) if change_col and pd.notna(row[change_col]) else 0.0,
                'heat_score': int(row[heat_col] * 100) if heat_col and pd.notna(row[heat_col]) else 50,
                'limitup_count': int(row[limitup_col]) if limitup_col and pd.notna(row[limitup_col]) else 0,
                'total_stocks': int(row[stocks_col]) if stocks_col and pd.notna(row[stocks_col]) else 0,
                'leaders': []  # 需要具体实现
            })
        
        logger.info(f"成功获取题材表现数据，共 {len(result)} 个题材")
        return result
        
    except Exception as e:
        logger.error(f"获取题材表现数据失败: {e}")
        raise

def get_akshare_industries_daily(date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    获取行业板块数据
    
    Args:
        date: 日期，格式YYYYMMDD，默认最新交易日
        
    Returns:
        List[Dict]: 行业板块列表
        [{
            'name': str,              # 行业名称
            'change': float,          # 涨跌幅
            'rank': int,              # 排名
            'amount': float,          # 成交额(亿元)
            'net_inflow': float,      # 净流入(亿元)
            'advance_count': int,     # 上涨家数
            'decline_count': int,     # 下跌家数
            'leaders': list           # 领涨股列表
        }]
    """
    try:
        logger.info(f"开始获取行业板块数据，日期: {date}")
        
        # 获取行业板块数据
        industry_df = ak.stock_board_industry_name_em()
        
        result = []
        for idx, row in industry_df.iterrows():
            result.append({
                'name': str(row['板块名称']),
                'change': float(row['涨跌幅']),
                'rank': idx + 1,
                'amount': float(row['总市值']) / 100000000,  # 简化处理
                'net_inflow': float(row['净流入'] if pd.notna(row['净流入']) else 0),
                'advance_count': int(row['上涨家数']) if pd.notna(row['上涨家数']) else 0,
                'decline_count': int(row['下跌家数']) if pd.notna(row['下跌家数']) else 0,
                'leaders': []  # 需要具体实现
            })
        
        logger.info(f"成功获取行业板块数据，共 {len(result)} 个行业")
        return result
        
    except Exception as e:
        logger.error(f"获取行业板块数据失败: {e}")
        raise

if __name__ == "__main__":
    """
    测试函数 - 验证接口返回的数据是否正确
    """
    print("=== 测试 akshare 数据访问层接口 ===\n")
    
    try:
        # 测试涨跌家数统计
        print("1. 测试获取涨跌家数统计:")
        ad_stats = get_akshare_advance_decline_stats()
        print(f"   上证上涨: {ad_stats['sh']['advance']}, 下跌: {ad_stats['sh']['decline']}")
        print()
        
        # 测试涨停板个股数据
        print("2. 测试获取涨停板个股数据:")
        limitup_stocks = get_akshare_limitup_stocks()
        print(f"   涨停板数量: {len(limitup_stocks)}")
        if limitup_stocks:
            print(f"   示例股票: {limitup_stocks[0]['name']} ({limitup_stocks[0]['ticker']})")
            print(f"   连板数: {limitup_stocks[0]['board_level']}, 涨幅: {limitup_stocks[0]['change']}%")
        print()
        
        # # 测试题材表现数据
        # print("3. 测试获取题材表现数据:")
        # themes = get_akshare_themes_daily()
        # print(f"   题材数量: {len(themes)}")
        # if themes:
        #     print(f"   示例题材: {themes[0]['name']}, 涨跌幅: {themes[0]['change']}%")
        # print()
        
        # # 测试行业板块数据
        # print("4. 测试获取行业板块数据:")
        # industries = get_akshare_industries_daily()
        # print(f"   行业数量: {len(industries)}")
        # if industries:
        #     print(f"   示例行业: {industries[0]['name']}, 涨跌幅: {industries[0]['change']}%")
        # print()
        
        # 测试指数数据
        print("5. 测试获取指数数据:")
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
        index_data = get_akshare_index_data('sh000001', start_date, end_date)
        print(f"   获取到上证指数 {len(index_data)} 天数据")
        if index_data:
            print(f"   最新数据: 收盘价 {index_data[-1]['close']}, 涨跌幅 {index_data[-1]['change_pct']}%")
        print()
        
        print("所有接口测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
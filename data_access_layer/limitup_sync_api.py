#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
涨停数据同步API
负责从akshare获取5日内涨停数据并与数据库进行增量同步
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional
import json
from collections import defaultdict
import concurrent.futures
from tqdm import tqdm
import pywencai

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import StockDatabase, get_database

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_limitup_pool_table() -> bool:
    """
    创建涨停池数据表，匹配stock_zt_pool_em()返回的数据结构
    
    Returns:
        bool: 是否创建成功
    """
    try:
        db = get_database()
        if not db.connect():
            logger.error("数据库连接失败")
            return False
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS limitup_pool (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL COMMENT '交易日期',
            code VARCHAR(10) NOT NULL COMMENT '股票代码',
            name VARCHAR(50) NOT NULL COMMENT '股票名称',
            change_percent DECIMAL(10,6) COMMENT '涨跌幅',
            latest_price DECIMAL(10,2) COMMENT '最新价',
            amount DECIMAL(15,2) COMMENT '成交额',
            circulation_market_value DECIMAL(15,2) COMMENT '流通市值',
            total_market_value DECIMAL(15,2) COMMENT '总市值',
            turnover_rate DECIMAL(10,6) COMMENT '换手率',
            sealed_fund DECIMAL(15,2) COMMENT '封板资金',
            first_limit_time VARCHAR(10) COMMENT '首次封板时间',
            last_limit_time VARCHAR(10) COMMENT '最后封板时间',
            board_break_count INT COMMENT '炸板次数',
            limit_up_count VARCHAR(20) COMMENT '涨停统计',
            continuous_board_count INT COMMENT '连板数',
            industry VARCHAR(50) COMMENT '所属行业',
            is_one_word_board BOOLEAN DEFAULT FALSE COMMENT '是否一字板',
            themes JSON COMMENT '题材概念',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_stock_date (date, code),
            INDEX idx_date (date),
            INDEX idx_code (code),
            INDEX idx_name (name),
            INDEX idx_continuous_board (continuous_board_count),
            INDEX idx_industry (industry)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='涨停池数据表'
        """
        
        cursor = db.connection.cursor()
        cursor.execute(create_table_query)
        cursor.close()
        
        logger.info("涨停池数据表创建/验证完成")
        return True
        
    except Exception as e:
        logger.error(f"创建涨停池数据表失败: {e}")
        return False


def get_akshare_limitup_pool_data(days: int = 5) -> List[Dict[str, Any]]:
    """
    获取指定天数内的涨停池数据
    
    Args:
        days: 获取最近多少天的数据，默认5天
        
    Returns:
        List[Dict]: 涨停池数据列表
    """
    all_data = []
    
    try:
        # 导入交易时间模块
        from trade_time import trade_time_instance
        
        # 确保交易日历已加载
        trade_time_instance.load_trade_dates()
        
        # 获取当前参考交易日（考虑是否已收盘）
        from trade_time import get_reference_trade_date
        reference_trade_date = get_reference_trade_date()
        current_date_str = reference_trade_date.strftime('%Y%m%d')
        
        # 过滤掉未来的交易日，只保留历史交易日
        historical_trade_dates = [
            date_str for date_str in trade_time_instance.trade_date_list 
            if date_str <= current_date_str
        ]
        
        if not historical_trade_dates:
            logger.warning("没有找到历史交易日数据")
            return []
        
        # 获取最近days个交易日（从最新的开始）
        recent_trade_dates = historical_trade_dates[-days:]
        
        logger.info(f"获取最近 {len(recent_trade_dates)} 个交易日数据: {recent_trade_dates}")
        
        for target_date in recent_trade_dates:
            logger.info(f"正在获取 {target_date} 的涨停池数据...")
            
            try:
                # 获取pywencai涨停原因数据
                reason_mapping = {}
                try:
                    # 转换日期格式: 20241008 -> 10月8号
                    year = target_date[:4]
                    month = str(int(target_date[4:6]))
                    day = str(int(target_date[6:8]))
                    date_query = f"{month}月{day}号"
                    
                    query_params = {
                        'query': f'{date_query}涨停，非ST',
                        'sort_key': 'code',
                        'sort_order': 'asc'
                    }
                    pywencai_data = get_pywencai_limitup_data(**query_params)
                    
                    # 创建股票代码到涨停原因的映射
                    if '股票代码' in pywencai_data.columns and f'涨停原因类别[{target_date}]' in pywencai_data.columns:
                        for _, row in pywencai_data.iterrows():
                            stock_code_full = str(row['股票代码'])
                            reason = str(row[f'涨停原因类别[{target_date}]'])
                            # 提取基础代码 (去除.SZ/.SH后缀)
                            base_code = stock_code_full.split('.')[0]
                            if reason and reason != 'nan':
                                reason_mapping[base_code] = [reason]
                    
                    logger.info(f"成功获取 {len(reason_mapping)} 条涨停原因数据")
                    
                except Exception as e:
                    logger.warning(f"获取pywencai涨停原因数据失败: {e}")
                    reason_mapping = {}
                
                # 调用akshare接口获取涨停池数据
                limitup_df = ak.stock_zt_pool_em(date=target_date)
                
                if limitup_df is not None and len(limitup_df) > 0:
                    # 转换DataFrame为字典列表
                    for _, row in limitup_df.iterrows():
                        stock_code = str(row.iloc[1]) if len(row) > 1 else ''
                        
                        # 获取涨停原因
                        themes = []
                        if stock_code and stock_code in reason_mapping:
                            themes = reason_mapping[stock_code]
                        
                        data = {
                            'date': target_date,
                            'code': stock_code,      # 代码 (位置1)
                            'name': str(row.iloc[2]) if len(row) > 2 else '',      # 名称 (位置2)
                            'change_percent': float(row.iloc[3]) if len(row) > 3 and pd.notna(row.iloc[3]) else 0.0,  # 涨跌幅
                            'latest_price': float(row.iloc[4]) if len(row) > 4 and pd.notna(row.iloc[4]) else 0.0,    # 最新价
                            'amount': float(row.iloc[5]) if len(row) > 5 and pd.notna(row.iloc[5]) else 0.0,          # 成交额
                            'circulation_market_value': float(row.iloc[6]) if len(row) > 6 and pd.notna(row.iloc[6]) else 0.0,  # 流通市值
                            'total_market_value': float(row.iloc[7]) if len(row) > 7 and pd.notna(row.iloc[7]) else 0.0,       # 总市值
                            'turnover_rate': float(row.iloc[8]) if len(row) > 8 and pd.notna(row.iloc[8]) else 0.0,   # 换手率
                            'sealed_fund': float(row.iloc[9]) if len(row) > 9 and pd.notna(row.iloc[9]) else 0.0,     # 封板资金
                            'first_limit_time': str(row.iloc[10]) if len(row) > 10 and pd.notna(row.iloc[10]) else '', # 首次封板时间
                            'last_limit_time': str(row.iloc[11]) if len(row) > 11 and pd.notna(row.iloc[11]) else '',  # 最后封板时间
                            'board_break_count': int(row.iloc[12]) if len(row) > 12 and pd.notna(row.iloc[12]) else 0, # 炸板次数
                            'limit_up_count': str(row.iloc[13]) if len(row) > 13 and pd.notna(row.iloc[13]) else '',   # 涨停统计
                            'continuous_board_count': int(row.iloc[14]) if len(row) > 14 and pd.notna(row.iloc[14]) else 0,  # 连板数
                            'industry': str(row.iloc[15]) if len(row) > 15 and pd.notna(row.iloc[15]) else '',         # 所属行业
                            'is_one_word_board': False,  # 需要根据逻辑判断
                            'themes': json.dumps(themes)  # 使用pywencai获取的涨停原因
                        }
                        
                        # 判断是否一字板: 没有炸板且首次封板时间和最后封板时间都小于等于093000
                        first_time = data['first_limit_time']
                        last_time = data['last_limit_time']
                        board_break_count = data['board_break_count']
                        
                        if first_time and last_time and board_break_count == 0:
                            # 检查时间是否小于等于093000
                            try:
                                first_time_int = int(first_time)
                                last_time_int = int(last_time)
                                # 判断是否都是有效的交易时间且小于等于093000
                                # 注意: 092502转换为整数后是92502(5位), 但原始字符串长度是6位
                                if (first_time_int <= 93000 and last_time_int <= 93000 and 
                                    len(first_time) == 6 and len(last_time) == 6):
                                    data['is_one_word_board'] = True
                                else:
                                    data['is_one_word_board'] = False
                            except (ValueError, TypeError):
                                data['is_one_word_board'] = False
                        else:
                            data['is_one_word_board'] = False
                        
                        all_data.append(data)
                        
                    logger.info(f"成功获取 {target_date} 的 {len(limitup_df)} 条涨停数据")
                else:
                    logger.warning(f"{target_date} 无涨停数据或数据为空")
                    
            except Exception as e:
                logger.warning(f"获取 {target_date} 涨停数据失败: {e}")
                continue
                
    except Exception as e:
        logger.error(f"获取涨停池数据失败: {e}")
        raise
    
    return all_data

def get_existing_dates_from_db() -> List[str]:
    """
    获取数据库中已存在的日期列表
    
    Returns:
        List[str]: 已存在日期的列表，格式YYYYMMDD
    """
    try:
        db = get_database()
        if not db.connect():
            return []
            
        query = "SELECT DISTINCT date FROM limitup_pool ORDER BY date DESC"
        result = db.execute_query(query)
        
        if result:
            # 转换日期格式为YYYYMMDD
            dates = [row['date'].strftime('%Y%m%d') if hasattr(row['date'], 'strftime') 
                    else str(row['date']) for row in result]
            return dates
        else:
            return []
            
    except Exception as e:
        logger.error(f"获取数据库日期列表失败: {e}")
        return []

def insert_limitup_data_to_db(data_list: List[Dict[str, Any]]) -> int:
    """
    批量插入涨停数据到数据库
    
    Args:
        data_list: 涨停数据列表
        
    Returns:
        int: 成功插入的记录数
    """
    success_count = 0
    
    try:
        db = get_database()
        if not db.connect():
            return 0
        
        insert_query = """
        INSERT INTO limitup_pool 
        (date, code, name, change_percent, latest_price, amount, 
         circulation_market_value, total_market_value, turnover_rate, sealed_fund,
         first_limit_time, last_limit_time, board_break_count, limit_up_count,
         continuous_board_count, industry, is_one_word_board, themes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            change_percent = VALUES(change_percent),
            latest_price = VALUES(latest_price),
            amount = VALUES(amount),
            circulation_market_value = VALUES(circulation_market_value),
            total_market_value = VALUES(total_market_value),
            turnover_rate = VALUES(turnover_rate),
            sealed_fund = VALUES(sealed_fund),
            first_limit_time = VALUES(first_limit_time),
            last_limit_time = VALUES(last_limit_time),
            board_break_count = VALUES(board_break_count),
            limit_up_count = VALUES(limit_up_count),
            continuous_board_count = VALUES(continuous_board_count),
            industry = VALUES(industry),
            is_one_word_board = VALUES(is_one_word_board),
            themes = VALUES(themes),
            updated_at = CURRENT_TIMESTAMP
        """
        
        cursor = db.connection.cursor()
        
        for data in data_list:
            try:
                params = (
                    data['date'], data['code'], data['name'], data['change_percent'],
                    data['latest_price'], data['amount'],
                    data['circulation_market_value'], data['total_market_value'],
                    data['turnover_rate'], data['sealed_fund'],
                    data['first_limit_time'], data['last_limit_time'],
                    data['board_break_count'], data['limit_up_count'],
                    data['continuous_board_count'], data['industry'],
                    data['is_one_word_board'], data['themes']
                )
                
                cursor.execute(insert_query, params)
                success_count += 1
                
            except Exception as e:
                logger.warning(f"插入数据失败 {data['code']}-{data['date']}: {e}")
                # 调试输出：显示有问题的数据
                if "turnover_rate" in str(e):
                    logger.debug(f"问题数据 - turnover_rate: {data.get('turnover_rate', 'N/A')} (类型: {type(data.get('turnover_rate'))})")
                    logger.debug(f"完整数据: {data}")
                continue
        
        db.connection.commit()
        cursor.close()
        
    except Exception as e:
        logger.error(f"批量插入数据失败: {e}")
        if 'cursor' in locals():
            cursor.close()
    
    return success_count

def sync_limitup_data(days: int = 5) -> Dict[str, Any]:
    """
    同步涨停数据的主函数
    
    Args:
        days: 同步最近多少天的数据，默认5天
        
    Returns:
        Dict: 同步结果统计
    """
    result = {
        'total_days': days,
        'fetched_days': 0,
        'fetched_records': 0,
        'inserted_records': 0,
        'existing_dates': [],
        'new_dates': [],
        'status': 'success'
    }
    
    try:
        logger.info(f"开始同步最近 {days} 天的涨停数据...")
        
        # 1. 确保数据表存在
        if not create_limitup_pool_table():
            result['status'] = 'table_creation_failed'
            return result
        
        # 2. 获取数据库中已存在的日期
        existing_dates = get_existing_dates_from_db()
        result['existing_dates'] = existing_dates
        logger.info(f"数据库中已存在 {len(existing_dates)} 个日期的数据")
        
        # 3. 从akshare获取数据
        akshare_data = get_akshare_limitup_pool_data(days)
        result['fetched_records'] = len(akshare_data)
        
        if not akshare_data:
            logger.warning("未获取到任何涨停数据")
            result['status'] = 'no_data'
            return result
        
        # 4. 过滤出需要插入的新数据
        new_data = []
        processed_dates = set()
        
        for data in akshare_data:
            date_str = data['date']
            processed_dates.add(date_str)
            
            if date_str not in existing_dates:
                new_data.append(data)
        
        result['fetched_days'] = len(processed_dates)
        result['new_dates'] = list(processed_dates - set(existing_dates))
        
        # 5. 插入新数据
        if new_data:
            inserted_count = insert_limitup_data_to_db(new_data)
            result['inserted_records'] = inserted_count
            logger.info(f"成功插入 {inserted_count} 条新记录")
        else:
            logger.info("无需插入新数据，所有数据已存在")
        
        logger.info(f"数据同步完成: 获取 {result['fetched_records']} 条记录, 插入 {result['inserted_records']} 条新记录")
        
    except Exception as e:
        logger.error(f"数据同步失败: {e}")
        result['status'] = 'error'
        result['error_message'] = str(e)
    
    return result

def get_limitup_data_by_date_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    获取指定日期范围内的涨停数据
    
    Args:
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD
        
    Returns:
        List[Dict]: 涨停数据列表
    """
    try:
        db = get_database()
        if not db.connect():
            logger.warning("数据库连接失败，尝试从akshare获取数据")
            # 这里需要实现从akshare按日期范围获取数据的逻辑
            return []
        
        query = """
        SELECT * FROM limitup_pool 
        WHERE date BETWEEN %s AND %s 
        ORDER BY date DESC, continuous_board_count DESC
        """
        
        result = db.execute_query(query, (start_date, end_date))
        
        if result and len(result) > 0:
            # 转换数据库数据格式
            converted_data = []
            for row in result:
                converted_data.append({
                    'date': row['date'].strftime('%Y%m%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                    'code': row['code'],
                    'name': row['name'],
                    'change_percent': float(row['change_percent']),
                    'latest_price': float(row['latest_price']),
                    'turnover_rate': float(row['turnover_rate']),
                    'amount': float(row['amount']),
                    'circulation_market_value': float(row['circulation_market_value']),
                    'total_market_value': float(row['total_market_value']),
                    'first_limit_time': row['first_limit_time'],
                    'last_limit_time': row['last_limit_time'],
                    'limit_up_count': row['limit_up_count'],
                    'continuous_board_count': int(row['continuous_board_count']),
                    'board_break_count': int(row['board_break_count']),
                    'is_one_word_board': bool(row['is_one_word_board']),
                    'industry': row.get('industry', ''),
                    'themes': row.get('themes', '[]')
                })
            return converted_data
        else:
            logger.info(f"数据库中没有 {start_date} 到 {end_date} 的涨停数据")
            return []
            
    except Exception as e:
        logger.error(f"获取涨停数据失败: {e}")
        return []

def get_recent_limitup_data(days: int = 5) -> List[Dict[str, Any]]:
    """
    获取最近N天的涨停数据（兼容旧接口）
    
    Args:
        days: 获取最近多少天的数据
        
    Returns:
        List[Dict]: 涨停数据列表
    """
    # 导入交易时间模块
    from trade_time import trade_time_instance
    
    # 确保交易日历已加载
    trade_time_instance.load_trade_dates()
    
    # 获取当前参考交易日（考虑是否已收盘）
    from trade_time import get_reference_trade_date
    reference_trade_date = get_reference_trade_date()
    current_date_str = reference_trade_date.strftime('%Y%m%d')
    
    # 过滤掉未来的交易日，只保留历史交易日
    historical_trade_dates = [
        date_str for date_str in trade_time_instance.trade_date_list 
        if date_str <= current_date_str
    ]
    
    if not historical_trade_dates or len(historical_trade_dates) < days:
        logger.warning(f"没有足够的交易日数据，请求{days}天，只有{len(historical_trade_dates)}天")
        days = min(days, len(historical_trade_dates))
    
    # 获取最近days个交易日
    recent_trade_dates = historical_trade_dates[-days:]
    
    if not recent_trade_dates:
        return []
    
    start_date = recent_trade_dates[0]
    end_date = recent_trade_dates[-1]
    
    return get_limitup_data_by_date_range(start_date, end_date)

def get_pywencai_limitup_data(**kwargs):
    """
    使用pywencai获取涨停数据
    
    Args:
        **kwargs: 查询参数，如query, sort_key, sort_order等
        
    Returns:
        pandas.DataFrame: 涨停数据
    """
    try:
        # 设置默认查询参数
        default_params = {
            'query': '涨停，非ST',
            'sort_key': 'code',
            'sort_order': 'asc'
        }
        
        # 合并默认参数和用户参数
        query_params = {**default_params, **kwargs}
        
        logger.info(f"使用pywencai查询参数: {query_params}")
        
        # 调用pywencai获取数据
        data = pywencai.get(**query_params)
        
        logger.info(f"成功获取 {len(data)} 条涨停数据")
        
        # 打印数据信息
        print(f"\n=== pywencai涨停数据查询结果 ===")
        print(f"数据形状: {data.shape}")
        print(f"列名: {list(data.columns)}")
        
        # 筛选只保留股票代码和涨停原因类别
        if '股票代码' in data.columns and '涨停原因类别[20250905]' in data.columns:
            filtered_data = data[['股票代码', '涨停原因类别[20250905]']]
            print(f"\n筛选后的数据 (股票代码 + 涨停原因类别):")
            print(filtered_data)
        else:
            print(f"\n前5行数据:")
            print(data.head())
        
        return data
        
    except Exception as e:
        logger.error(f"pywencai查询失败: {e}")
        raise


if __name__ == "__main__":
    """
    测试函数
    """
    print("=== 测试涨停数据同步API ===\n")
    
    # # 测试pywencai接口
    # print("1. 测试pywencai涨停查询功能:")
    # query_params = {
    #     'query': '9月6号涨停，非ST',
    #     'sort_key': 'code',
    #     'sort_order': 'asc'
    # }
    # pywencai_data = get_pywencai_limitup_data(**query_params)
    # print()
    
    # 测试数据同步
    print("2. 测试数据同步功能:")
    sync_result = sync_limitup_data(5)  
    print(f"   同步结果: {sync_result}")
    print()
    
    # 测试数据获取
    print("3. 测试数据获取功能:")
    limitup_data = get_recent_limitup_data(5)
    print(f"   获取到 {len(limitup_data)} 条涨停数据")
    if limitup_data:
        print(f"   示例数据: {limitup_data[0]}")
    print()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据访问层工具函数
提供数据验证、格式化、比较和更新功能
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_akshare_data(data: Any, data_type: str) -> Tuple[bool, str]:
    """
    验证akshare数据正确性
    
    Args:
        data: 要验证的数据
        data_type: 数据类型 'market', 'limitup', 'theme', 'industry'
        
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    try:
        logger.info(f"开始验证akshare数据，数据类型: {data_type}")
        
        if data is None:
            return False, "数据为空"
        
        # 根据数据类型进行不同的验证
        if data_type == 'market':
            # 验证市场数据
            if not isinstance(data, dict):
                return False, "市场数据格式错误，应为字典"
            
            required_fields = ['total_turnover', 'advance_count', 'decline_count', 
                              'close_limitup', 'sh_advance_rate', 'date']
            for field in required_fields:
                if field not in data:
                    return False, f"缺少必要字段: {field}"
            
            # 数值范围验证
            if data['total_turnover'] < 0:
                return False, "总成交额不能为负数"
            if data['advance_count'] < 0 or data['decline_count'] < 0:
                return False, "涨跌家数不能为负数"
            if not (0 <= data['sh_advance_rate'] <= 100):
                return False, "上证上涨率应在0-100之间"
                
        elif data_type == 'limitup':
            # 验证涨停板数据
            if not isinstance(data, list):
                return False, "涨停板数据格式错误，应为列表"
            
            if len(data) == 0:
                return True, "无涨停板数据"
                
            for stock in data:
                if not isinstance(stock, dict):
                    return False, "涨停板个股数据格式错误"
                
                required_fields = ['ticker', 'name', 'board_level', 'change']
                for field in required_fields:
                    if field not in stock:
                        return False, f"涨停板个股缺少字段: {field}"
                
                if stock['board_level'] < 1:
                    return False, "连板数不能小于1"
                    
        elif data_type == 'theme':
            # 验证题材数据
            if not isinstance(data, list):
                return False, "题材数据格式错误，应为列表"
                
            for theme in data:
                if not isinstance(theme, dict):
                    return False, "题材数据格式错误"
                
                if 'name' not in theme:
                    return False, "题材缺少名称字段"
                    
        elif data_type == 'industry':
            # 验证行业数据
            if not isinstance(data, list):
                return False, "行业数据格式错误，应为列表"
                
            for industry in data:
                if not isinstance(industry, dict):
                    return False, "行业数据格式错误"
                
                if 'name' not in industry:
                    return False, "行业缺少名称字段"
        else:
            return False, f"不支持的数据类型: {data_type}"
        
        logger.info(f"akshare数据验证通过，数据类型: {data_type}")
        return True, "验证通过"
        
    except Exception as e:
        logger.error(f"数据验证失败: {e}")
        return False, f"验证异常: {str(e)}"

def compare_akshare_db_data(akshare_data: Any, db_data: Any, tolerance: float = 0.1) -> Dict[str, Any]:
    """
    对比akshare和数据库数据一致性
    
    Args:
        akshare_data: akshare获取的数据
        db_data: 数据库获取的数据
        tolerance: 允许的差异容忍度
        
    Returns:
        Dict: 对比结果
        {
            'is_consistent': bool,      # 是否一致
            'differences': list,        # 差异列表
            'similarity_score': float   # 相似度评分
        }
    """
    try:
        logger.info("开始对比akshare和数据库数据一致性")
        
        if akshare_data is None and db_data is None:
            return {
                'is_consistent': True,
                'differences': [],
                'similarity_score': 1.0
            }
        
        if akshare_data is None or db_data is None:
            return {
                'is_consistent': False,
                'differences': ['一方数据为空'],
                'similarity_score': 0.0
            }
        
        # 简单对比逻辑，实际应根据具体数据结构实现
        differences = []
        
        if isinstance(akshare_data, dict) and isinstance(db_data, dict):
            # 字典数据对比
            all_keys = set(akshare_data.keys()) | set(db_data.keys())
            
            for key in all_keys:
                akshare_val = akshare_data.get(key)
                db_val = db_data.get(key)
                
                if akshare_val != db_val:
                    if (isinstance(akshare_val, (int, float)) and 
                        isinstance(db_val, (int, float)) and 
                        abs(akshare_val - db_val) <= tolerance):
                        # 数值差异在容忍范围内
                        continue
                    differences.append(f"字段 {key}: akshare={akshare_val}, db={db_val}")
                    
        elif isinstance(akshare_data, list) and isinstance(db_data, list):
            # 列表数据对比
            if len(akshare_data) != len(db_data):
                differences.append(f"数据数量不同: akshare={len(akshare_data)}, db={len(db_data)}")
            
        similarity_score = 1.0 - (len(differences) / max(len(str(akshare_data)), len(str(db_data)), 1))
        
        result = {
            'is_consistent': len(differences) == 0,
            'differences': differences,
            'similarity_score': round(similarity_score, 2)
        }
        
        logger.info(f"数据对比完成，一致性: {result['is_consistent']}, 相似度: {result['similarity_score']}")
        return result
        
    except Exception as e:
        logger.error(f"数据对比失败: {e}")
        return {
            'is_consistent': False,
            'differences': [f"对比异常: {str(e)}"],
            'similarity_score': 0.0
        }

def format_market_data_for_ui(raw_data: Dict[str, Any], source: str = 'akshare') -> Dict[str, Any]:
    """
    将原始市场数据格式化为前端UI需要的格式
    
    Args:
        raw_data: 原始数据
        source: 数据来源 'akshare' 或 'database'
        
    Returns:
        Dict: 格式化后的数据
    """
    try:
        logger.info(f"开始格式化市场数据，来源: {source}")
        
        formatted_data = {
            'total_turnover': round(float(raw_data.get('total_turnover', 0)), 2),
            'advance_count': int(raw_data.get('advance_count', 0)),
            'decline_count': int(raw_data.get('decline_count', 0)),
            'open_limitup': int(raw_data.get('open_limitup', 0)),
            'close_limitup': int(raw_data.get('close_limitup', 0)),
            'sh_advance_rate': round(float(raw_data.get('sh_advance_rate', 0)), 1),
            'sz_advance_rate': round(float(raw_data.get('sz_advance_rate', 0)), 1),
            'cyb_advance_rate': round(float(raw_data.get('cyb_advance_rate', 0)), 1),
            'date': raw_data.get('date', ''),
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
        
        # 计算涨跌比率
        total_stocks = formatted_data['advance_count'] + formatted_data['decline_count']
        if total_stocks > 0:
            formatted_data['advance_ratio'] = round(formatted_data['advance_count'] / total_stocks * 100, 1)
        else:
            formatted_data['advance_ratio'] = 0.0
        
        logger.info(f"市场数据格式化完成，来源: {source}")
        return formatted_data
        
    except Exception as e:
        logger.error(f"市场数据格式化失败: {e}")
        # 返回默认格式数据
        return {
            'total_turnover': 0.0,
            'advance_count': 0,
            'decline_count': 0,
            'open_limitup': 0,
            'close_limitup': 0,
            'sh_advance_rate': 0.0,
            'sz_advance_rate': 0.0,
            'cyb_advance_rate': 0.0,
            'date': '',
            'source': source,
            'advance_ratio': 0.0,
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }

def format_limitup_data_for_ui(raw_data: List[Dict[str, Any]], source: str = 'akshare') -> List[Dict[str, Any]]:
    """
    格式化连板数据供前端UI使用
    
    Args:
        raw_data: 原始连板数据列表
        source: 数据来源
        
    Returns:
        List[Dict]: 格式化后的连板数据
    """
    try:
        logger.info(f"开始格式化连板数据，来源: {source}, 数量: {len(raw_data)}")
        
        formatted_data = []
        for stock in raw_data:
            formatted_stock = {
                'ticker': str(stock.get('ticker', '')).zfill(6),
                'name': str(stock.get('name', '')),
                'board_level': int(stock.get('board_level', 1)),
                'change': round(float(stock.get('change', 0)), 2),
                'turnover': round(float(stock.get('turnover', 0)), 2),
                'amount': round(float(stock.get('amount', 0)), 2),
                'first_time': str(stock.get('first_time', '')),
                'is_one_word': bool(stock.get('is_one_word', False)),
                'themes': stock.get('themes', []),
                'market': _determine_market(stock.get('ticker', '')),
                'source': source
            }
            formatted_data.append(formatted_stock)
        
        logger.info(f"连板数据格式化完成，数量: {len(formatted_data)}")
        return formatted_data
        
    except Exception as e:
        logger.error(f"连板数据格式化失败: {e}")
        return []

def format_theme_data_for_ui(raw_data: List[Dict[str, Any]], source: str = 'akshare') -> List[Dict[str, Any]]:
    """
    格式化题材数据供前端UI使用
    
    Args:
        raw_data: 原始题材数据列表
        source: 数据来源
        
    Returns:
        List[Dict]: 格式化后的题材数据
    """
    try:
        logger.info(f"开始格式化题材数据，来源: {source}, 数量: {len(raw_data)}")
        
        formatted_data = []
        for theme in raw_data:
            formatted_theme = {
                'name': str(theme.get('name', '')),
                'change': round(float(theme.get('change', 0)), 2),
                'heat_score': int(theme.get('heat_score', 0)),
                'limitup_count': int(theme.get('limitup_count', 0)),
                'total_stocks': int(theme.get('total_stocks', 0)),
                'leaders': theme.get('leaders', []),
                'is_hot': theme.get('heat_score', 0) >= 70,
                'is_high_volume': theme.get('limitup_count', 0) >= 3,
                'source': source
            }
            formatted_data.append(formatted_theme)
        
        logger.info(f"题材数据格式化完成，数量: {len(formatted_data)}")
        return formatted_data
        
    except Exception as e:
        logger.error(f"题材数据格式化失败: {e}")
        return []

def format_industry_data_for_ui(raw_data: List[Dict[str, Any]], source: str = 'akshare') -> List[Dict[str, Any]]:
    """
    格式化行业数据供前端UI使用
    
    Args:
        raw_data: 原始行业数据列表
        source: 数据来源
        
    Returns:
        List[Dict]: 格式化后的行业数据
    """
    try:
        logger.info(f"开始格式化行业数据，来源: {source}, 数量: {len(raw_data)}")
        
        formatted_data = []
        for industry in raw_data:
            formatted_industry = {
                'name': str(industry.get('name', '')),
                'rank': int(industry.get('rank', 0)),
                'change': round(float(industry.get('change', 0)), 2),
                'amount': round(float(industry.get('amount', 0)), 2),
                'net_inflow': round(float(industry.get('net_inflow', 0)), 2),
                'advance_count': int(industry.get('advance_count', 0)),
                'decline_count': int(industry.get('decline_count', 0)),
                'leaders': industry.get('leaders', []),
                'strength_score': int(industry.get('strength_score', 0)),
                'source': source
            }
            formatted_data.append(formatted_industry)
        
        logger.info(f"行业数据格式化完成，数量: {len(formatted_data)}")
        return formatted_data
        
    except Exception as e:
        logger.error(f"行业数据格式化失败: {e}")
        return []

def update_database_from_akshare(date: Optional[str] = None) -> Dict[str, Any]:
    """
    从akshare获取数据并更新到数据库
    
    Args:
        date: 日期，格式YYYYMMDD，默认最新交易日
        
    Returns:
        Dict: 更新结果统计
    """
    try:
        logger.info(f"开始从akshare更新数据库数据，日期: {date}")
        
        # 这里需要导入具体的数据库操作函数
        # 实际实现时会调用具体的插入/更新方法
        
        result = {
            'success': True,
            'message': '数据更新功能待实现',
            'updated_count': 0,
            'failed_count': 0,
            'date': date or datetime.now().strftime('%Y%m%d'),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"数据库更新操作完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"数据库更新失败: {e}")
        return {
            'success': False,
            'message': f"更新失败: {str(e)}",
            'updated_count': 0,
            'failed_count': 0,
            'date': date or '',
            'timestamp': datetime.now().isoformat()
        }

def batch_update_market_data(start_date: str, end_date: str) -> Dict[str, Any]:
    """
    批量更新历史数据
    
    Args:
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
        
    Returns:
        Dict: 批量更新结果
    """
    try:
        logger.info(f"开始批量更新历史数据，日期范围: {start_date} 至 {end_date}")
        
        # 这里需要实现具体的批量更新逻辑
        
        result = {
            'success': True,
            'message': '批量更新功能待实现',
            'total_days': 0,
            'updated_days': 0,
            'failed_days': 0,
            'start_date': start_date,
            'end_date': end_date,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"批量更新操作完成: {result}")
        return result
        
    except Exception as e:
        logger.error(f"批量更新失败: {e}")
        return {
            'success': False,
            'message': f"批量更新失败: {str(e)}",
            'total_days': 0,
            'updated_days': 0,
            'failed_days': 0,
            'start_date': start_date,
            'end_date': end_date,
            'timestamp': datetime.now().isoformat()
        }

def _determine_market(ticker: str) -> str:
    """
    根据股票代码确定市场类型
    
    Args:
        ticker: 股票代码
        
    Returns:
        str: 市场类型 'sh'/'sz'/'cyb'/'kcb'
    """
    if not ticker:
        return 'unknown'
    
    ticker_str = str(ticker).zfill(6)
    
    if ticker_str.startswith('6'):
        return 'sh'  # 上海主板
    elif ticker_str.startswith('0'):
        return 'sz'  # 深圳主板/中小板
    elif ticker_str.startswith('3'):
        return 'cyb'  # 创业板
    elif ticker_str.startswith('688'):
        return 'kcb'  # 科创板
    else:
        return 'unknown'

if __name__ == "__main__":
    """
    测试函数 - 验证工具函数功能
    """
    print("=== 测试数据访问层工具函数 ===\n")
    
    try:
        # 测试数据验证
        print("1. 测试数据验证功能:")
        test_data = {'total_turnover': 10000, 'advance_count': 2000, 'date': '20250101'}
        is_valid, message = validate_akshare_data(test_data, 'market')
        print(f"   验证结果: {is_valid}, 消息: {message}")
        print()
        
        # 测试数据对比
        print("2. 测试数据对比功能:")
        data1 = {'value': 10.5, 'count': 100}
        data2 = {'value': 10.6, 'count': 100}
        comparison = compare_akshare_db_data(data1, data2, 0.2)
        print(f"   对比结果: {comparison['is_consistent']}")
        print(f"   相似度: {comparison['similarity_score']}")
        print()
        
        # 测试数据格式化
        print("3. 测试数据格式化功能:")
        market_data = {
            'total_turnover': 12345.678,
            'advance_count': 2500,
            'decline_count': 1500,
            'close_limitup': 35,
            'sh_advance_rate': 62.345
        }
        formatted = format_market_data_for_ui(market_data)
        print(f"   格式化后成交额: {formatted['total_turnover']}")
        print(f"   格式化后上涨率: {formatted['sh_advance_rate']}")
        print()
        
        print("✅ 所有工具函数测试完成!")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
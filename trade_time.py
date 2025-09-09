#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交易时间处理模块
提供交易日历、交易时间判断、日期导航等功能
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta, time
import logging
from typing import List, Dict, Optional, Set
import pickle
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 交易时间配置
TRADE_SCHEDULE = {
    'open_time': time(9, 30),      # 开盘时间
    'close_time': time(15, 0),     # 收盘时间
    'morning_start': time(9, 15),  # 早盘集合竞价开始
    'morning_end': time(9, 25),    # 早盘集合竞价结束
    'afternoon_start': time(11, 30),  # 午盘开始
    'afternoon_end': time(13, 0),     # 午盘结束
    'pause_start': time(11, 30),   # 休盘开始
    'pause_end': time(13, 0),      # 休盘结束
}

# 缓存文件路径
CACHE_FILE = 'trade_date_cache.pkl'

class TradeTime:
    def __init__(self):
        self.trade_dates = set()
        self.trade_date_list = []
        self.load_trade_dates()
    
    def fetch_stocks_trade_date(self, start_date: str = None, end_date: str = None) -> List[str]:
        """
        获取交易日历
        
        Args:
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            
        Returns:
            List[str]: 交易日列表，格式YYYYMMDD
        """
        try:
            logger.info(f"获取交易日历: {start_date} 至 {end_date}")
            
            # 设置默认日期范围（最近365天）
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # 使用akshare获取交易日历
            trade_date_df = ak.tool_trade_date_hist_sina()
            
            if trade_date_df is not None and len(trade_date_df) > 0:
                # 过滤日期范围
                # 确保日期列为字符串类型进行比较
                trade_date_df['trade_date_str'] = trade_date_df['trade_date'].astype(str)
                mask = (trade_date_df['trade_date_str'] >= start_date) & (trade_date_df['trade_date_str'] <= end_date)
                filtered_dates = trade_date_df[mask]['trade_date'].tolist()
                
                # 转换为字符串列表 (YYYYMMDD格式)
                trade_dates = []
                for date in filtered_dates:
                    if hasattr(date, 'strftime'):
                        trade_dates.append(date.strftime('%Y%m%d'))
                    else:
                        # 处理字符串日期
                        date_str = str(date)
                        if '-' in date_str:
                            # 转换 YYYY-MM-DD 为 YYYYMMDD
                            trade_dates.append(date_str.replace('-', ''))
                        else:
                            trade_dates.append(date_str)
                
                logger.info(f"成功获取 {len(trade_dates)} 个交易日")
                return trade_dates
            else:
                logger.warning("获取交易日历失败，返回空列表")
                return []
                
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            # 返回一个默认的交易日列表（周一至周五）
            return self._generate_default_trade_dates(start_date, end_date)
    
    def _generate_default_trade_dates(self, start_date: str, end_date: str) -> List[str]:
        """生成默认的交易日历（周一至周五）"""
        start = datetime.strptime(start_date, '%Y%m%d')
        end = datetime.strptime(end_date, '%Y%m%d')
        
        trade_dates = []
        current = start
        
        while current <= end:
            # 周一至周五为交易日
            if current.weekday() < 5:  # 0-4: Monday to Friday
                trade_dates.append(current.strftime('%Y%m%d'))
            current += timedelta(days=1)
        
        return trade_dates
    
    def load_trade_dates(self, force_refresh: bool = False) -> None:
        """加载交易日历到内存"""
        # 检查缓存文件是否存在且未过期
        cache_valid = False
        if not force_refresh and os.path.exists(CACHE_FILE):
            file_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
            if (datetime.now() - file_time).days < 7:  # 缓存有效期7天
                try:
                    with open(CACHE_FILE, 'rb') as f:
                        cached_data = pickle.load(f)
                        self.trade_dates = cached_data.get('trade_dates', set())
                        self.trade_date_list = cached_data.get('trade_date_list', [])
                        cache_valid = True
                        logger.info(f"从缓存加载 {len(self.trade_dates)} 个交易日")
                except Exception as e:
                    logger.warning(f"加载缓存失败: {e}")
        
        if not cache_valid or force_refresh:
            # 重新获取交易日历
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y%m%d')  # 最近2年
            
            trade_dates = self.fetch_stocks_trade_date(start_date, end_date)
            self.trade_dates = set(trade_dates)
            self.trade_date_list = sorted(trade_dates)
            
            # 保存到缓存
            try:
                with open(CACHE_FILE, 'wb') as f:
                    pickle.dump({
                        'trade_dates': self.trade_dates,
                        'trade_date_list': self.trade_date_list,
                        'last_updated': datetime.now()
                    }, f)
                logger.info(f"交易日历缓存已更新，共 {len(self.trade_dates)} 个交易日")
            except Exception as e:
                logger.error(f"保存缓存失败: {e}")
    
    def is_trade_date(self, date_obj) -> bool:
        """
        判断是否为交易日
        
        Args:
            date_obj: 日期对象，可以是datetime.date、datetime.datetime或字符串YYYYMMDD
            
        Returns:
            bool: 是否为交易日
        """
        try:
            if isinstance(date_obj, datetime):
                date_str = date_obj.strftime('%Y%m%d')
            elif isinstance(date_obj, str):
                date_str = date_obj
            else:
                date_str = date_obj.strftime('%Y%m%d')
            
            return date_str in self.trade_dates
            
        except Exception as e:
            logger.error(f"判断交易日失败: {e}")
            return False
    
    def get_previous_trade_date(self, date_obj, n: int = 1) -> Optional[datetime]:
        """
        获取前N个交易日
        
        Args:
            date_obj: 参考日期
            n: 往前推的天数
            
        Returns:
            Optional[datetime]: 前N个交易日，如果没有则返回None
        """
        try:
            if isinstance(date_obj, datetime):
                current_date = date_obj
            elif isinstance(date_obj, str):
                current_date = datetime.strptime(date_obj, '%Y%m%d')
            else:
                current_date = datetime.combine(date_obj, time())
            
            current_str = current_date.strftime('%Y%m%d')
            
            if current_str not in self.trade_date_list:
                # 如果当前日期不是交易日，找到最近的交易日
                idx = self._find_nearest_trade_date_index(current_str)
            else:
                idx = self.trade_date_list.index(current_str)
            
            if idx >= n:
                prev_date_str = self.trade_date_list[idx - n]
                return datetime.strptime(prev_date_str, '%Y%m%d').date()
            else:
                logger.warning(f"无法找到前 {n} 个交易日")
                return None
                
        except Exception as e:
            logger.error(f"获取前一个交易日失败: {e}")
            return None
    
    def get_next_trade_date(self, date_obj, n: int = 1) -> Optional[datetime]:
        """
        获取后N个交易日
        
        Args:
            date_obj: 参考日期
            n: 往后推的天数
            
        Returns:
            Optional[datetime]: 后N个交易日，如果没有则返回None
        """
        try:
            if isinstance(date_obj, datetime):
                current_date = date_obj
            elif isinstance(date_obj, str):
                current_date = datetime.strptime(date_obj, '%Y%m%d')
            else:
                current_date = datetime.combine(date_obj, time())
            
            current_str = current_date.strftime('%Y%m%d')
            
            if current_str not in self.trade_date_list:
                # 如果当前日期不是交易日，找到最近的交易日
                idx = self._find_nearest_trade_date_index(current_str)
            else:
                idx = self.trade_date_list.index(current_str)
            
            if idx + n < len(self.trade_date_list):
                next_date_str = self.trade_date_list[idx + n]
                return datetime.strptime(next_date_str, '%Y%m%d').date()
            else:
                logger.warning(f"无法找到后 {n} 个交易日")
                return None
                
        except Exception as e:
            logger.error(f"获取后一个交易日失败: {e}")
            return None
    
    def _find_nearest_trade_date_index(self, date_str: str) -> int:
        """找到最近交易日的索引"""
        target_date = datetime.strptime(date_str, '%Y%m%d')
        
        # 二分查找最近的交易日
        left, right = 0, len(self.trade_date_list) - 1
        while left <= right:
            mid = (left + right) // 2
            mid_date = datetime.strptime(self.trade_date_list[mid], '%Y%m%d')
            
            if mid_date < target_date:
                left = mid + 1
            else:
                right = mid - 1
        
        # 返回最接近的交易日索引
        return max(0, min(left, len(self.trade_date_list) - 1))
    
    def is_tradetime(self, dt: datetime) -> bool:
        """
        判断是否为交易时间（开盘时间内）
        
        Args:
            dt: 时间对象
            
        Returns:
            bool: 是否为交易时间
        """
        if not self.is_trade_date(dt):
            return False
        
        current_time = dt.time()
        return (TRADE_SCHEDULE['open_time'] <= current_time <= TRADE_SCHEDULE['close_time'])
    
    def is_runtime(self, dt: datetime) -> bool:
        """
        判断是否为运行时间（包括集合竞价）
        
        Args:
            dt: 时间对象
            
        Returns:
            bool: 是否为运行时间
        """
        if not self.is_trade_date(dt):
            return False
        
        current_time = dt.time()
        return (TRADE_SCHEDULE['morning_start'] <= current_time <= TRADE_SCHEDULE['close_time'])
    
    def is_pause(self, dt: datetime) -> bool:
        """
        判断是否为休盘时间
        
        Args:
            dt: 时间对象
            
        Returns:
            bool: 是否为休盘时间
        """
        if not self.is_trade_date(dt):
            return False
        
        current_time = dt.time()
        return (TRADE_SCHEDULE['pause_start'] <= current_time < TRADE_SCHEDULE['pause_end'])
    
    def is_close(self, dt: datetime) -> bool:
        """
        判断是否已收盘
        
        Args:
            dt: 时间对象
            
        Returns:
            bool: 是否已收盘
        """
        if not self.is_trade_date(dt):
            return True  # 非交易日视为已收盘
        
        current_time = dt.time()
        return current_time > TRADE_SCHEDULE['close_time']
    
    def is_open(self, dt: datetime) -> bool:
        """
        判断是否已开盘
        
        Args:
            dt: 时间对象
            
        Returns:
            bool: 是否已开盘
        """
        if not self.is_trade_date(dt):
            return False
        
        current_time = dt.time()
        return current_time >= TRADE_SCHEDULE['open_time']
    
    def get_trade_date_last(self, n: int = 1) -> Optional[datetime]:
        """
        获取最近N个交易日
        
        Args:
            n: 最近N个交易日
            
        Returns:
            Optional[datetime]: 最近N个交易日
        """
        try:
            if len(self.trade_date_list) >= n:
                last_date_str = self.trade_date_list[-n]
                return datetime.strptime(last_date_str, '%Y%m%d').date()
            else:
                logger.warning(f"无法找到最近 {n} 个交易日")
                return None
                
        except Exception as e:
            logger.error(f"获取最近交易日失败: {e}")
            return None

# 全局实例
trade_time_instance = TradeTime()

# 便捷函数
def is_trade_date(date_obj) -> bool:
    """判断是否为交易日"""
    return trade_time_instance.is_trade_date(date_obj)

def get_previous_trade_date(date_obj, n: int = 1) -> Optional[datetime]:
    """获取前N个交易日"""
    return trade_time_instance.get_previous_trade_date(date_obj, n)

def get_next_trade_date(date_obj, n: int = 1) -> Optional[datetime]:
    """获取后N个交易日"""
    return trade_time_instance.get_next_trade_date(date_obj, n)

def is_tradetime(dt: datetime) -> bool:
    """判断是否为交易时间"""
    return trade_time_instance.is_tradetime(dt)

def is_runtime(dt: datetime) -> bool:
    """判断是否为运行时间"""
    return trade_time_instance.is_runtime(dt)

def is_pause(dt: datetime) -> bool:
    """判断是否为休盘时间"""
    return trade_time_instance.is_pause(dt)

def is_close(dt: datetime) -> bool:
    """判断是否已收盘"""
    return trade_time_instance.is_close(dt)

def is_open(dt: datetime) -> bool:
    """判断是否已开盘"""
    return trade_time_instance.is_open(dt)

def get_trade_date_last(n: int = 1) -> Optional[datetime]:
    """获取最近N个交易日"""
    return trade_time_instance.get_trade_date_last(n)

def get_reference_trade_date() -> datetime.date:
    """
    获取当前交易参考日期
    
    Returns:
        datetime.date: 参考交易日
    """
    now_time = datetime.now()
    current_date = now_time.date()
    
    
    # 情况1：当前是交易日且在交易时间内（开盘后且未收盘）
    if is_trade_date(current_date) and is_open(now_time) and not is_close(now_time):
        logger.debug(f"参考交易日判断: 交易日 {current_date} 交易时间内 -> 返回当天")
        return current_date
    
    # 情况2：当前是交易日但已收盘，返回当前日期（当天数据已完整）
    if is_trade_date(current_date) and is_close(now_time):
        logger.debug(f"参考交易日判断: 交易日 {current_date} 已收盘 -> 返回当天")
        return current_date
    
    # 情况3：当前是交易日但未开盘（开盘前），返回上一交易日
    if is_trade_date(current_date) and not is_open(now_time):
        prev_date = get_previous_trade_date(current_date)
        logger.debug(f"参考交易日判断: 交易日 {current_date} 未开盘 -> 返回上一交易日 {prev_date}")
        return prev_date
    
    # 情况4：非交易日，返回上一交易日
    prev_date = get_previous_trade_date(current_date)
    logger.debug(f"参考交易日判断: 非交易日 {current_date} -> 返回上一交易日 {prev_date}")
    return prev_date

def refresh_trade_dates(force: bool = False) -> None:
    """刷新交易日历缓存"""
    trade_time_instance.load_trade_dates(force)

if __name__ == "__main__":
    """测试函数"""
    print("=== 交易时间模块测试 ===\n")
    
    # 刷新交易日历
    refresh_trade_dates()
    
    # 测试基本功能
    today = datetime.now().date()
    print(f"今天 {today} 是交易日: {is_trade_date(today)}")
    
    prev_date = get_previous_trade_date(today)
    print(f"上一个交易日: {prev_date}")
    
    next_date = get_next_trade_date(today)
    print(f"下一个交易日: {next_date}")
    
    # 测试时间判断
    now = datetime.now()
    print(f"当前时间 {now.time()} 是交易时间: {is_tradetime(now)}")
    print(f"当前时间 {now.time()} 是运行时间: {is_runtime(now)}")
    print(f"当前时间 {now.time()} 是休盘时间: {is_pause(now)}")
    print(f"当前时间 {now.time()} 已收盘: {is_close(now)}")
    print(f"当前时间 {now.time()} 已开盘: {is_open(now)}")
    
    # 测试参考交易日
    ref_date = get_reference_trade_date()
    print(f"当前参考交易日: {ref_date}")
    
    # 测试最近交易日
    last_trade_date = get_trade_date_last()
    print(f"最近交易日: {last_trade_date}")
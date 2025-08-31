#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL数据库配置和CRUD操作接口
端口: 3309
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

from database_config import get_database_config

class StockDatabase:
    def __init__(self, host=None, port=None, database=None, 
                 user=None, password=None, test_mode=False):
        """初始化数据库连接"""
        # 使用配置或参数
        config = get_database_config(test_mode)
        self.host = host or config['host']
        self.port = port or config['port']
        self.database = database or config['database']
        self.user = user or config['user']
        self.password = password or config['password']
        self.connection = None
        
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print(f"成功连接到MySQL数据库 (端口: {self.port})")
                return True
        except Error as e:
            print(f"数据库连接错误: {e}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("数据库连接已关闭")
    
    def execute_query(self, query: str, params: tuple = None):
        """执行查询语句"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"查询执行错误: {e}")
            return None
    
    def execute_update(self, query: str, params: tuple = None):
        """执行更新语句"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Error as e:
            print(f"更新执行错误: {e}")
            self.connection.rollback()
            return 0
    
    def initialize_database(self):
        """初始化数据库表结构"""
        if not self.connect():
            return False
        
        try:
            # 创建数据库（如果不存在）
            create_db_query = f"CREATE DATABASE IF NOT EXISTS {self.database}"
            cursor = self.connection.cursor()
            cursor.execute(create_db_query)
            
            # 使用数据库
            cursor.execute(f"USE {self.database}")
            
            # 创建市场情绪表
            create_sentiment_table = """
            CREATE TABLE IF NOT EXISTS market_sentiment (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL UNIQUE,
                highest_limitup INT NOT NULL,
                first_boards INT NOT NULL,
                limitups INT NOT NULL,
                limitdowns INT NOT NULL,
                sealed_ratio DECIMAL(5,3) NOT NULL,
                break_ratio DECIMAL(5,3) NOT NULL,
                p1to2_success DECIMAL(5,3) NOT NULL,
                p2to3_success DECIMAL(5,3) NOT NULL,
                yesterday_limitups_roi DECIMAL(5,2) NOT NULL,
                sh_change DECIMAL(5,2) NOT NULL,
                sz_change DECIMAL(5,2) NOT NULL,
                cyb_change DECIMAL(5,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            
            # 创建连板个股表
            create_limitup_table = """
            CREATE TABLE IF NOT EXISTS limitup_events (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                ticker VARCHAR(10) NOT NULL,
                stock_name VARCHAR(50) NOT NULL,
                board_level INT NOT NULL,
                first_time VARCHAR(5) NOT NULL,
                refill_counts INT NOT NULL,
                turnover_rate DECIMAL(5,2) NOT NULL,
                amount BIGINT NOT NULL,
                mkt_cap_freefloat BIGINT NOT NULL,
                is_one_word BOOLEAN DEFAULT FALSE,
                is_recap BOOLEAN DEFAULT FALSE,
                themes JSON NOT NULL,
                industries JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_date (date),
                INDEX idx_ticker (ticker),
                INDEX idx_stock_name (stock_name)
            )
            """
            
            # 创建题材表
            create_theme_table = """
            CREATE TABLE IF NOT EXISTS theme_daily (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                theme_name VARCHAR(50) NOT NULL,
                chg_pct DECIMAL(5,2) NOT NULL,
                heat_score INT NOT NULL,
                is_new BOOLEAN DEFAULT FALSE,
                streak_days INT NOT NULL,
                leaders JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_theme_date (date, theme_name),
                INDEX idx_date (date),
                INDEX idx_theme_name (theme_name)
            )
            """
            
            # 创建行业表
            create_industry_table = """
            CREATE TABLE IF NOT EXISTS industry_daily (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                industry_name VARCHAR(50) NOT NULL,
                rank INT NOT NULL,
                chg_pct DECIMAL(5,2) NOT NULL,
                strength_score INT NOT NULL,
                amount BIGINT NOT NULL,
                net_main_inflow BIGINT NOT NULL,
                advances INT NOT NULL,
                declines INT NOT NULL,
                leaders JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_industry_date (date, industry_name),
                INDEX idx_date (date),
                INDEX idx_industry_name (industry_name)
            )
            """
            
            # 执行创建表语句
            cursor.execute(create_sentiment_table)
            cursor.execute(create_limitup_table)
            cursor.execute(create_theme_table)
            cursor.execute(create_industry_table)
            
            cursor.close()
            print("数据库表结构初始化完成")
            return True
            
        except Error as e:
            print(f"数据库初始化错误: {e}")
            return False
    
    # CRUD 操作 - 市场情绪数据
    def create_market_sentiment(self, data: Dict[str, Any]) -> bool:
        """创建市场情绪数据"""
        query = """
        INSERT INTO market_sentiment 
        (date, highest_limitup, first_boards, limitups, limitdowns, 
         sealed_ratio, break_ratio, p1to2_success, p2to3_success, 
         yesterday_limitups_roi, sh_change, sz_change, cyb_change)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            highest_limitup = VALUES(highest_limitup),
            first_boards = VALUES(first_boards),
            limitups = VALUES(limitups),
            limitdowns = VALUES(limitdowns),
            sealed_ratio = VALUES(sealed_ratio),
            break_ratio = VALUES(break_ratio),
            p1to2_success = VALUES(p1to2_success),
            p2to3_success = VALUES(p2to3_success),
            yesterday_limitups_roi = VALUES(yesterday_limitups_roi),
            sh_change = VALUES(sh_change),
            sz_change = VALUES(sz_change),
            cyb_change = VALUES(cyb_change)
        """
        
        params = (
            data['date'], data['highest_limitup'], data['first_boards'], 
            data['limitups'], data['limitdowns'], data['sealed_ratio'], 
            data['break_ratio'], data['p1to2_success'], data['p2to3_success'],
            data['yesterday_limitups_roi'], data['sh_change'], 
            data['sz_change'], data['cyb_change']
        )
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def get_market_sentiment(self, date: str = None) -> List[Dict]:
        """获取市场情绪数据"""
        if date:
            query = "SELECT * FROM market_sentiment WHERE date = %s ORDER BY date DESC"
            params = (date,)
        else:
            query = "SELECT * FROM market_sentiment ORDER BY date DESC LIMIT 100"
            params = None
        
        return self.execute_query(query, params)
    
    def update_market_sentiment(self, date: str, data: Dict[str, Any]) -> bool:
        """更新市场情绪数据"""
        query = """
        UPDATE market_sentiment 
        SET highest_limitup = %s, first_boards = %s, limitups = %s, limitdowns = %s,
            sealed_ratio = %s, break_ratio = %s, p1to2_success = %s, p2to3_success = %s,
            yesterday_limitups_roi = %s, sh_change = %s, sz_change = %s, cyb_change = %s
        WHERE date = %s
        """
        
        params = (
            data['highest_limitup'], data['first_boards'], data['limitups'], 
            data['limitdowns'], data['sealed_ratio'], data['break_ratio'], 
            data['p1to2_success'], data['p2to3_success'], data['yesterday_limitups_roi'],
            data['sh_change'], data['sz_change'], data['cyb_change'], date
        )
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def delete_market_sentiment(self, date: str) -> bool:
        """删除市场情绪数据"""
        query = "DELETE FROM market_sentiment WHERE date = %s"
        params = (date,)
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    # CRUD 操作 - 连板个股数据
    def create_limitup_event(self, data: Dict[str, Any]) -> bool:
        """创建连板个股数据"""
        query = """
        INSERT INTO limitup_events 
        (date, ticker, stock_name, board_level, first_time, refill_counts,
         turnover_rate, amount, mkt_cap_freefloat, is_one_word, is_recap,
         themes, industries)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            data['date'], data['ticker'], data['stock_name'], data['board_level'],
            data['first_time'], data['refill_counts'], data['turnover_rate'],
            data['amount'], data['mkt_cap_freefloat'], data['is_one_word'],
            data['is_recap'], json.dumps(data['themes']), json.dumps(data['industries'])
        )
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def get_limitup_events(self, date: str = None, ticker: str = None) -> List[Dict]:
        """获取连板个股数据"""
        if date and ticker:
            query = "SELECT * FROM limitup_events WHERE date = %s AND ticker = %s"
            params = (date, ticker)
        elif date:
            query = "SELECT * FROM limitup_events WHERE date = %s ORDER BY board_level DESC"
            params = (date,)
        elif ticker:
            query = "SELECT * FROM limitup_events WHERE ticker = %s ORDER BY date DESC"
            params = (ticker,)
        else:
            query = "SELECT * FROM limitup_events ORDER BY date DESC, board_level DESC LIMIT 100"
            params = None
        
        result = self.execute_query(query, params)
        # 解析JSON字段
        for item in result:
            item['themes'] = json.loads(item['themes'])
            item['industries'] = json.loads(item['industries'])
        return result
    
    def update_limitup_event(self, event_id: int, data: Dict[str, Any]) -> bool:
        """更新连板个股数据"""
        query = """
        UPDATE limitup_events 
        SET board_level = %s, first_time = %s, refill_counts = %s,
            turnover_rate = %s, amount = %s, mkt_cap_freefloat = %s,
            is_one_word = %s, is_recap = %s, themes = %s, industries = %s
        WHERE id = %s
        """
        
        params = (
            data['board_level'], data['first_time'], data['refill_counts'],
            data['turnover_rate'], data['amount'], data['mkt_cap_freefloat'],
            data['is_one_word'], data['is_recap'], json.dumps(data['themes']),
            json.dumps(data['industries']), event_id
        )
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def delete_limitup_event(self, event_id: int) -> bool:
        """删除连板个股数据"""
        query = "DELETE FROM limitup_events WHERE id = %s"
        params = (event_id,)
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    # CRUD 操作 - 题材数据
    def create_theme_data(self, data: Dict[str, Any]) -> bool:
        """创建题材数据"""
        query = """
        INSERT INTO theme_daily 
        (date, theme_name, chg_pct, heat_score, is_new, streak_days, leaders)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            chg_pct = VALUES(chg_pct),
            heat_score = VALUES(heat_score),
            is_new = VALUES(is_new),
            streak_days = VALUES(streak_days),
            leaders = VALUES(leaders)
        """
        
        params = (
            data['date'], data['theme_name'], data['chg_pct'], data['heat_score'],
            data['is_new'], data['streak_days'], json.dumps(data['leaders'])
        )
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def get_theme_data(self, date: str = None, theme_name: str = None) -> List[Dict]:
        """获取题材数据"""
        if date and theme_name:
            query = "SELECT * FROM theme_daily WHERE date = %s AND theme_name = %s"
            params = (date, theme_name)
        elif date:
            query = "SELECT * FROM theme_daily WHERE date = %s ORDER BY heat_score DESC"
            params = (date,)
        elif theme_name:
            query = "SELECT * FROM theme_daily WHERE theme_name = %s ORDER BY date DESC"
            params = (theme_name,)
        else:
            query = "SELECT * FROM theme_daily ORDER BY date DESC, heat_score DESC LIMIT 100"
            params = None
        
        result = self.execute_query(query, params)
        # 解析JSON字段
        for item in result:
            item['leaders'] = json.loads(item['leaders'])
        return result
    
    # CRUD 操作 - 行业数据
    def create_industry_data(self, data: Dict[str, Any]) -> bool:
        """创建行业数据"""
        query = """
        INSERT INTO industry_daily 
        (date, industry_name, rank, chg_pct, strength_score, amount, 
         net_main_inflow, advances, declines, leaders)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            rank = VALUES(rank),
            chg_pct = VALUES(chg_pct),
            strength_score = VALUES(strength_score),
            amount = VALUES(amount),
            net_main_inflow = VALUES(net_main_inflow),
            advances = VALUES(advances),
            declines = VALUES(declines),
            leaders = VALUES(leaders)
        """
        
        params = (
            data['date'], data['industry_name'], data['rank'], data['chg_pct'],
            data['strength_score'], data['amount'], data['net_main_inflow'],
            data['advances'], data['declines'], json.dumps(data['leaders'])
        )
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def get_industry_data(self, date: str = None, industry_name: str = None) -> List[Dict]:
        """获取行业数据"""
        if date and industry_name:
            query = "SELECT * FROM industry_daily WHERE date = %s AND industry_name = %s"
            params = (date, industry_name)
        elif date:
            query = "SELECT * FROM industry_daily WHERE date = %s ORDER BY rank ASC"
            params = (date,)
        elif industry_name:
            query = "SELECT * FROM industry_daily WHERE industry_name = %s ORDER BY date DESC"
            params = (industry_name,)
        else:
            query = "SELECT * FROM industry_daily ORDER BY date DESC, rank ASC LIMIT 100"
            params = None
        
        result = self.execute_query(query, params)
        # 解析JSON字段
        for item in result:
            item['leaders'] = json.loads(item['leaders'])
        return result
    
    def batch_insert_data(self, data_type: str, data_list: List[Dict]) -> int:
        """批量插入数据"""
        success_count = 0
        for data in data_list:
            if data_type == 'market_sentiment':
                if self.create_market_sentiment(data):
                    success_count += 1
            elif data_type == 'limitup_events':
                if self.create_limitup_event(data):
                    success_count += 1
            elif data_type == 'theme_daily':
                if self.create_theme_data(data):
                    success_count += 1
            elif data_type == 'industry_daily':
                if self.create_industry_data(data):
                    success_count += 1
        return success_count

# 单例模式
db_instance = None

def get_database():
    """获取数据库实例"""
    global db_instance
    if db_instance is None:
        db_instance = StockDatabase()
    return db_instance
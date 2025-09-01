#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票市场分析仪表板 - 增强版
包含完整的4个功能模块: 连板天梯、大盘情绪、题材追踪、行业追踪
使用模拟数据实现所有功能
"""

import os
import webbrowser
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pyecharts.charts import Line, Bar, HeatMap, Graph, WordCloud, Radar, TreeMap, Sankey
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo

# 数据库支持
from database import StockDatabase, get_database

# 创建输出目录
os.makedirs('output', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

class EnhancedStockDashboard:
    def __init__(self, use_database=False):
        self.current_page = "ladder"  # 默认页面: ladder, sentiment, themes, industries
        self.html_file = 'output/stock_dashboard_enhanced.html'
        self.use_database = use_database
        self.db = None
        
        # 强制使用数据库模式
        self.use_database = True
        self.db = get_database()
        if self.db.connect():
            print("√ 数据库连接成功")
            self.data = self.load_data_from_database()
        else:
            print("❌ 数据库连接失败，程序退出")
            exit(1)
    
    def generate_comprehensive_mock_data(self):
        """生成完整的模拟数据"""
        dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D')
        date_strs = [d.strftime('%Y-%m-%d') for d in dates]
        
        # 1. 市场情绪数据
        market_sentiment = []
        for i, date in enumerate(date_strs):
            sentiment = {
                'date': date,
                'highest_limitup': np.random.randint(3, 10),
                'first_boards': np.random.randint(20, 50),
                'limitups': np.random.randint(30, 100),
                'limitdowns': np.random.randint(5, 20),
                'sealed_ratio': round(np.random.uniform(0.6, 0.9), 3),
                'break_ratio': round(np.random.uniform(0.1, 0.3), 3),
                'p1to2_success': round(np.random.uniform(0.3, 0.7), 3),
                'p2to3_success': round(np.random.uniform(0.2, 0.5), 3),
                'yesterday_limitups_roi': round(np.random.uniform(-2, 5), 2),
                'sh_change': round(np.random.uniform(-1, 2), 2),
                'sz_change': round(np.random.uniform(-1, 2), 2),
                'cyb_change': round(np.random.uniform(-2, 3), 2)
            }
            market_sentiment.append(sentiment)
        
        # 2. 连板个股数据
        stocks = ['贵州茅台', '宁德时代', '比亚迪', '隆基绿能', '药明康德', '东方财富', 
                 '中信证券', '中国平安', '招商银行', '万科A', '格力电器', '美的集团']
        themes_list = ['白酒', '新能源', '汽车', '光伏', '医药', '金融科技', '证券', 
                      '保险', '银行', '房地产', '家电', '智能制造']
        industries_list = ['食品饮料', '电力设备', '汽车', '新能源', '医药生物', '非银金融',
                          '证券', '保险', '银行', '房地产', '家用电器', '机械设备']
        
        limitup_events = []
        for date in date_strs:
            for i in range(np.random.randint(5, 15)):
                stock_idx = np.random.randint(0, len(stocks))
                event = {
                    'date': date,
                    'ticker': f'{600000 + stock_idx}',
                    'stock_name': stocks[stock_idx],
                    'board_level': np.random.randint(1, 6),
                    'first_time': f'{np.random.randint(9, 14)}:{np.random.randint(10, 59):02d}',
                    'refill_counts': np.random.randint(0, 3),
                    'turnover_rate': round(np.random.uniform(1, 15), 2),
                    'amount': int(np.random.uniform(10000000, 200000000)),
                    'mkt_cap_freefloat': int(np.random.uniform(1000000000, 10000000000)),
                    'is_one_word': np.random.choice([True, False], p=[0.3, 0.7]),
                    'is_recap': np.random.choice([True, False], p=[0.2, 0.8]),
                    'themes': [themes_list[stock_idx]],
                    'industries': [industries_list[stock_idx]]
                }
                limitup_events.append(event)
        
        # 3. 题材数据
        theme_names = ['人工智能', '新能源汽车', '光伏储能', '芯片半导体', '医药医疗', 
                      '消费电子', '军工', '信创', '数字经济', '元宇宙']
        
        theme_daily = []
        for date in date_strs:
            for theme in theme_names:
                theme_data = {
                    'date': date,
                    'theme_name': theme,
                    'chg_pct': round(np.random.uniform(-5, 8), 2),
                    'heat_score': np.random.randint(30, 100),
                    'is_new': np.random.choice([True, False], p=[0.1, 0.9]),
                    'streak_days': np.random.randint(1, 5),
                    'leaders': [stocks[i] for i in np.random.choice(range(len(stocks)), 2)]
                }
                theme_daily.append(theme_data)
        
        # 4. 行业数据
        industry_names = ['银行', '证券', '保险', '房地产', '白酒', '医药', '新能源', 
                         '半导体', '消费电子', '军工', '电力', '煤炭']
        
        industry_daily = []
        for date in date_strs:
            for i, industry in enumerate(industry_names):
                industry_data = {
                    'date': date,
                    'industry_name': industry,
                    'rank': i + 1,
                    'chg_pct': round(np.random.uniform(-3, 6), 2),
                    'strength_score': np.random.randint(50, 100),
                    'amount': int(np.random.uniform(1000000000, 5000000000)),
                    'net_main_inflow': int(np.random.uniform(-500000000, 2000000000)),
                    'advances': np.random.randint(5, 30),
                    'declines': np.random.randint(2, 15),
                    'leaders': [stocks[j] for j in np.random.choice(range(len(stocks)), 3)]
                }
                industry_daily.append(industry_data)
        
        return {
            'market_sentiment': pd.DataFrame(market_sentiment),
            'limitup_events': pd.DataFrame(limitup_events),
            'theme_daily': pd.DataFrame(theme_daily),
            'industry_daily': pd.DataFrame(industry_daily),
            'dates': date_strs
        }
    
    def load_data_from_database(self):
        """从数据库加载数据"""
        print("√ 从数据库加载数据...")
        
        data = {}
        
        try:
            # 加载市场情绪数据
            sentiment_data = self.db.get_market_sentiment()
            data['market_sentiment'] = pd.DataFrame(sentiment_data) if sentiment_data else pd.DataFrame()
            
            # 加载连板个股数据
            limitup_data = self.db.get_limitup_events()
            data['limitup_events'] = pd.DataFrame(limitup_data) if limitup_data else pd.DataFrame()
            
            # 加载题材数据
            theme_data = self.db.get_theme_data()
            data['theme_daily'] = pd.DataFrame(theme_data) if theme_data else pd.DataFrame()
            
            # 加载行业数据
            industry_data = self.db.get_industry_data()
            data['industry_daily'] = pd.DataFrame(industry_data) if industry_data else pd.DataFrame()
            
            # 获取日期列表
            if not data['market_sentiment'].empty:
                dates = sorted(data['market_sentiment']['date'].unique())
                data['dates'] = [str(date) for date in dates]
            else:
                # 如果没有数据，使用默认日期
                data['dates'] = ['2024-01-01', '2024-01-02', '2024-01-03']
            
            print(f"√ 数据加载完成: ")
            print(f"   市场情绪: {len(data['market_sentiment'])} 条")
            print(f"   连板个股: {len(data['limitup_events'])} 条")
            print(f"   题材数据: {len(data['theme_daily'])} 条")
            print(f"   行业数据: {len(data['industry_daily'])} 条")
            
        except Exception as e:
            print(f"❌ 数据库数据加载失败: {e}")
            print("❌ 程序退出")
            exit(1)
        
        return data
    
    def create_sentiment_heatmap(self):
        """创建大盘情绪热力图"""
        sentiment_data = self.data['market_sentiment']
        dates = self.data['dates']
        
        # 定义热力图指标
        indicators = [
            'highest_limitup', 'limitups', 'limitdowns', 'sealed_ratio',
            'break_ratio', 'p1to2_success', 'p2to3_success', 'sh_change'
        ]
        indicator_names = [
            '连板高度', '涨停数', '跌停数', '封板率',
            '炸板率', '1进2成功率', '2进3成功率', '上证涨跌'
        ]
        
        heatmap_data = []
        for i, indicator in enumerate(indicators):
            for j, date in enumerate(dates):
                date_data = sentiment_data[sentiment_data['date'] == date]
                if not date_data.empty:
                    value = date_data[indicator].iloc[0]
                    heatmap_data.append([j, i, value])
        
        heatmap = (
            HeatMap(init_opts=opts.InitOpts(theme=ThemeType.DARK))
            .add_xaxis(dates)
            .add_yaxis(
                "情绪指标",
                indicator_names,
                heatmap_data,
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="大盘情绪热力图"),
                visualmap_opts=opts.VisualMapOpts(
                    min_=-5, max_=10, is_calculable=True, orient="horizontal", pos_left="center"
                ),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            )
        )
        return heatmap
    
    def create_limitup_ladder(self):
        """创建连板天梯"""
        # 按日期和连板数分组
        ladder_data = self.data['limitup_events']
        dates = self.data['dates']
        
        ladder_html = ""
        for date in dates:
            date_data = ladder_data[ladder_data['date'] == date]
            if not date_data.empty:
                ladder_html += f'''
                <div class="date-column">
                    <h4 class="column-date">{date}</h4>
                    <div class="ladder-cards">
                '''
                
                for _, stock in date_data.iterrows():
                    badge_class = "one-word" if stock['is_one_word'] else "normal"
                    badge_class += " recap" if stock['is_recap'] else ""
                    
                    ladder_html += f'''
                    <div class="limitup-card {badge_class}" onclick="showStockDetail('{stock['ticker']}')">
                        <div class="stock-header">
                            <span class="board-level">{stock['board_level']}板</span>
                            <h5>{stock['stock_name']}</h5>
                            <span class="stock-code">{stock['ticker']}</span>
                        </div>
                        <div class="stock-info">
                            <p>📈 涨停时间: {stock['first_time']}</p>
                            <p>🔄 换手率: {stock['turnover_rate']}%</p>
                            <p>💰 成交额: {stock['amount']:,}</p>
                            <div class="tags">
                                <span class="theme-tag">{stock['themes'][0]}</span>
                                <span class="industry-tag">{stock['industries'][0]}</span>
                            </div>
                        </div>
                    </div>
                    '''
                
                ladder_html += '''
                    </div>
                </div>
                '''
        
        return ladder_html
    
    def create_theme_cards(self):
        """创建题材胶囊卡片"""
        theme_data = self.data['theme_daily']
        dates = self.data['dates']
        
        theme_html = ""
        for date in dates:
            date_data = theme_data[theme_data['date'] == date]
            if not date_data.empty:
                theme_html += f'''
                <div class="date-column">
                    <h4 class="column-date">{date}</h4>
                    <div class="theme-cards">
                '''
                
                # 取热度最高的5个题材
                top_themes = date_data.nlargest(5, 'heat_score')
                
                for _, theme in top_themes.iterrows():
                    change_class = "positive" if theme['chg_pct'] > 0 else "negative"
                    new_badge = "🆕" if theme['is_new'] else ""
                    
                    theme_html += f'''
                    <div class="theme-card" onclick="showThemeDetail('{theme['theme_name']}')">
                        <div class="theme-header">
                            <h5>{theme['theme_name']}</h5>
                            <span class="heat-score">🔥{theme['heat_score']}</span>
                        </div>
                        <div class="theme-info">
                            <p class="change {change_class}">📊 {theme['chg_pct']}%</p>
                            <p class="leaders">🏆 {', '.join(theme['leaders'])}</p>
                            <p class="streak">📅 连涨{theme['streak_days']}天 {new_badge}</p>
                        </div>
                    </div>
                    '''
                
                theme_html += '''
                    </div>
                </div>
                '''
        
        return theme_html
    
    def create_industry_cards(self):
        """创建行业排名卡片"""
        industry_data = self.data['industry_daily']
        dates = self.data['dates']
        
        industry_html = ""
        for date in dates:
            date_data = industry_data[industry_data['date'] == date]
            if not date_data.empty:
                industry_html += f'''
                <div class="date-column">
                    <h4 class="column-date">{date}</h4>
                    <div class="industry-cards">
                '''
                
                # 取排名前5的行业
                top_industries = date_data.nsmallest(5, 'rank')
                
                for _, industry in top_industries.iterrows():
                    change_class = "positive" if industry['chg_pct'] > 0 else "negative"
                    flow_class = "inflow" if industry['net_main_inflow'] > 0 else "outflow"
                    
                    industry_html += f'''
                    <div class="industry-card" onclick="showIndustryDetail('{industry['industry_name']}')">
                        <div class="industry-header">
                            <span class="rank-badge">#{industry['rank']}</span>
                            <h5>{industry['industry_name']}</h5>
                        </div>
                        <div class="industry-info">
                            <p class="change {change_class}">📈 {industry['chg_pct']}%</p>
                            <p class="strength">💪 强度: {industry['strength_score']}</p>
                            <p class="flow {flow_class}">💰 净流入: {industry['net_main_inflow']:,}</p>
                            <p class="leaders">🎯 领涨: {', '.join(industry['leaders'][:2])}</p>
                        </div>
                    </div>
                    '''
                
                industry_html += '''
                    </div>
                </div>
                '''
        
        return industry_html
    
    def generate_enhanced_html(self):
        """生成增强版HTML页面"""
        # 创建各个模块的内容
        sentiment_chart = self.create_sentiment_heatmap()
        ladder_content = self.create_limitup_ladder()
        theme_content = self.create_theme_cards()
        industry_content = self.create_industry_cards()
        
        # 读取模板
        html_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票市场分析仪表板 - 增强版</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        :root {
            --bg: #0f1115;
            --panel: #151922;
            --text: #e5e7eb;
            --muted: #9aa3b2;
            --accent: #ff9f0a;
            --red: #ef4444;
            --green: #22c55e;
            --chip-bg: #1f2430;
            --badge-purple: #8b5cf6;
            --badge-cyan: #06b6d4;
            --grid-border: #262c3a;
            --hover: rgba(255,255,255,.06);
            --shadow: 0 6px 20px rgba(0,0,0,.25);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
        
        .container {
            display: grid;
            grid-template-columns: 220px 1fr;
            grid-template-rows: auto 1fr auto;
            grid-template-areas: 
                "sidebar header"
                "sidebar main"
                "sidebar footer";
            min-height: 100vh;
        }
        
        .sidebar {
            grid-area: sidebar;
            background: var(--panel);
            padding: 20px;
            border-right: 1px solid var(--grid-border);
        }
        
        .sidebar h2 {
            color: var(--accent);
            margin-bottom: 30px;
            text-align: center;
            font-size: 1.2em;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            color: var(--text);
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 8px;
            transition: all 0.3s;
        }
        
        .nav-item:hover {
            background: var(--hover);
            transform: translateX(4px);
        }
        
        .nav-item.active {
            background: var(--accent);
            color: #000;
            font-weight: bold;
        }
        
        .nav-icon {
            margin-right: 10px;
            font-size: 1.1em;
        }
        
        .header {
            grid-area: header;
            background: var(--panel);
            padding: 20px;
            border-bottom: 1px solid var(--grid-border);
        }
        
        .timeline {
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .date-picker {
            padding: 8px 12px;
            border: 1px solid var(--grid-border);
            border-radius: 6px;
            background: var(--bg);
            color: var(--text);
        }
        
        .filter-btn {
            padding: 8px 16px;
            background: var(--accent);
            color: #000;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .main {
            grid-area: main;
            padding: 20px;
            overflow-x: auto;
        }
        
        .content-section {
            margin-bottom: 30px;
        }
        
        .section-title {
            color: var(--accent);
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .scrollable-columns {
            display: flex;
            gap: 20px;
            overflow-x: auto;
            padding: 10px 0;
        }
        
        .date-column {
            min-width: 320px;
            background: var(--panel);
            border-radius: 12px;
            padding: 15px;
            border: 1px solid var(--grid-border);
        }
        
        .column-date {
            color: var(--accent);
            margin-bottom: 15px;
            text-align: center;
            font-size: 1.1em;
        }
        
        .ladder-cards, .theme-cards, .industry-cards {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .limitup-card, .theme-card, .industry-card {
            background: var(--chip-bg);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--accent);
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .limitup-card:hover, .theme-card:hover, .industry-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }
        
        .limitup-card.one-word {
            border-left-color: var(--badge-purple);
        }
        
        .limitup-card.recap {
            border-left-color: var(--badge-cyan);
        }
        
        .stock-header, .theme-header, .industry-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            gap: 8px;
        }
        
        .board-level {
            background: var(--accent);
            color: #000;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .rank-badge {
            background: var(--accent);
            color: #000;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .heat-score {
            background: var(--red);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        
        .stock-code {
            color: var(--muted);
            font-size: 0.8em;
        }
        
        .stock-info p, .theme-info p, .industry-info p {
            margin: 4px 0;
            font-size: 0.9em;
        }
        
        .tags {
            display: flex;
            gap: 6px;
            margin-top: 8px;
        }
        
        .theme-tag, .industry-tag {
            background: var(--badge-purple);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7em;
        }
        
        .industry-tag {
            background: var(--badge-cyan);
        }
        
        .change.positive {
            color: var(--red);
            font-weight: bold;
        }
        
        .change.negative {
            color: var(--green);
            font-weight: bold;
        }
        
        .flow.inflow {
            color: var(--red);
        }
        
        .flow.outflow {
            color: var(--green);
        }
        
        .leaders {
            color: var(--muted);
            font-size: 0.8em;
        }
        
        .chart-container {
            background: var(--panel);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid var(--grid-border);
        }
        
        .chart {
            width: 100%;
            height: 400px;
        }
        
        .footer {
            grid-area: footer;
            background: var(--panel);
            padding: 15px 20px;
            text-align: center;
            color: var(--muted);
            border-top: 1px solid var(--grid-border);
        }
        
        /* 滚动条样式 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--grid-border);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--muted);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 左侧导航栏 -->
        <aside class="sidebar">
            <h2>📈 股票分析</h2>
            <a href="#" class="nav-item active" onclick="switchPage('ladder')">
                <span class="nav-icon">🏆</span> 连板天梯
            </a>
            <a href="#" class="nav-item" onclick="switchPage('sentiment')">
                <span class="nav-icon">📊</span> 大盘情绪
            </a>
            <a href="#" class="nav-item" onclick="switchPage('themes')">
                <span class="nav-icon">🔥</span> 题材追踪
            </a>
            <a href="#" class="nav-item" onclick="switchPage('industries')">
                <span class="nav-icon">🏢</span> 行业追踪
            </a>
        </aside>
        
        <!-- 顶部时间轴 -->
        <header class="header">
            <div class="timeline">
                <h3>市场分析仪表板</h3>
                <input type="date" class="date-picker" id="startDate" value="2024-01-01">
                <span>至</span>
                <input type="date" class="date-picker" id="endDate" value="2024-01-10">
                <select class="date-picker" id="marketSelect">
                    <option value="ALL">全部市场</option>
                    <option value="SH">上证A股</option>
                    <option value="SZ">深证A股</option>
                    <option value="CYB">创业板</option>
                    <option value="KCB">科创板</option>
                </select>
                <button class="filter-btn" onclick="applyFilters()">应用筛选</button>
            </div>
        </header>
        
        <!-- 主要内容区 -->
        <main class="main">
            <!-- 连板天梯页面 -->
            <div id="ladder-page" class="content-section">
                <h3 class="section-title">🏆 连板天梯</h3>
                <div class="scrollable-columns">
                    {{ladder_content}}
                </div>
            </div>
            
            <!-- 大盘情绪页面 -->
            <div id="sentiment-page" class="content-section" style="display: none;">
                <h3 class="section-title">📊 大盘情绪分析</h3>
                <div class="chart-container">
                    <div id="sentiment-chart" class="chart"></div>
                </div>
            </div>
            
            <!-- 题材追踪页面 -->
            <div id="themes-page" class="content-section" style="display: none;">
                <h3 class="section-title">🔥 题材追踪</h3>
                <div class="scrollable-columns">
                    {{theme_content}}
                </div>
            </div>
            
            <!-- 行业追踪页面 -->
            <div id="industries-page" class="content-section" style="display: none;">
                <h3 class="section-title">🏢 行业追踪</h3>
                <div class="scrollable-columns">
                    {{industry_content}}
                </div>
            </div>
        </main>
        
        <!-- 页脚 -->
        <footer class="footer">
            <p>© 2024 股票分析系统 | 数据更新时间: {{current_time}} | 使用模拟数据</p>
        </footer>
    </div>
    
    <script>
        // 页面切换函数
        function switchPage(page) {
            // 隐藏所有页面
            document.getElementById('ladder-page').style.display = 'none';
            document.getElementById('sentiment-page').style.display = 'none';
            document.getElementById('themes-page').style.display = 'none';
            document.getElementById('industries-page').style.display = 'none';
            
            // 显示选中页面
            document.getElementById(page + '-page').style.display = 'block';
            
            // 更新导航激活状态
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // 如果是情绪页面，初始化图表
            if (page === 'sentiment') {
                initSentimentChart();
            }
        }
        
        // 初始化情绪图表
        function initSentimentChart() {
            var sentimentChart = echarts.init(document.getElementById('sentiment-chart'));
            sentimentChart.setOption({{sentiment_chart_option}});
            
            // 窗口调整时重绘图表
            window.addEventListener('resize', function() {
                sentimentChart.resize();
            });
        }
        
        // 应用筛选条件
        function applyFilters() {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            const market = document.getElementById('marketSelect').value;
            
            console.log('应用筛选:', { startDate, endDate, market });
            // 这里可以添加AJAX请求来更新数据
            alert('筛选功能已触发，实际项目中会更新数据');
        }
        
        // 显示股票详情
        function showStockDetail(ticker) {
            console.log('显示股票详情:', ticker);
            alert('股票详情功能: ' + ticker);
        }
        
        // 显示题材详情
        function showThemeDetail(themeName) {
            console.log('显示题材详情:', themeName);
            alert('题材详情功能: ' + themeName);
        }
        
        // 显示行业详情
        function showIndustryDetail(industryName) {
            console.log('显示行业详情:', industryName);
            alert('行业详情功能: ' + industryName);
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            // 默认显示连板天梯页面
            switchPage('ladder');
        });
    </script>
</body>
</html>
        '''
        
        # 替换模板中的变量
        html_content = html_template
        html_content = html_content.replace('{{current_time}}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        html_content = html_content.replace('{{ladder_content}}', ladder_content)
        html_content = html_content.replace('{{theme_content}}', theme_content)
        html_content = html_content.replace('{{industry_content}}', industry_content)
        html_content = html_content.replace('{{sentiment_chart_option}}', sentiment_chart.dump_options())
        
        # 写入HTML文件
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return self.html_file
    
    def open_in_browser(self):
        """在浏览器中打开生成的HTML"""
        webbrowser.open('file://' + os.path.abspath(self.html_file))
        print(f"增强版仪表板已生成: {os.path.abspath(self.html_file)}")

def main():
    """主函数"""
    
    print("正在生成增强版股票市场分析仪表板...")
    
    # 创建仪表板实例
    dashboard = EnhancedStockDashboard(use_database=True)
    
    # 生成HTML
    html_file = dashboard.generate_enhanced_html()
    
    # 在浏览器中打开
    dashboard.open_in_browser()
    
    print("增强版仪表板生成完成!")

if __name__ == "__main__":
    main()
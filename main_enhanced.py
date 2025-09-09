#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票市场分析仪表板 - 增强版
包含完整的功能模块: 连板天梯、大盘情绪
使用模拟数据实现所有功能
"""

import os
import webbrowser
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pyecharts.charts import Line, Bar, HeatMap, Graph, WordCloud, Radar, TreeMap, Sankey, Pie, Grid
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo

# 数据库支持
from database import StockDatabase, get_database

# 涨停数据同步API
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_access_layer.limitup_sync_api import get_limitup_data_by_date_range, get_recent_limitup_data

# 创建输出目录
os.makedirs('output', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

class EnhancedStockDashboard:
    def __init__(self,):
        self.current_page = "ladder"  # 默认页面: ladder, sentiment
        self.html_file = 'output/stock_dashboard_enhanced.html'
        self.db = None
        
        # 强制使用数据库模式
        self.db = get_database()
        if self.db.connect():
            print("√ 数据库连接成功")
            # 检查并更新数据库数据
            self.check_and_update_database()
            self.data = self.load_data_from_database()
        else:
            print("❌ 数据库连接失败，程序退出")
            exit(1)
    
    def generate_comprehensive_mock_data(self):
        """生成完整的模拟数据（已禁用）"""
        print("❌ 模拟数据功能已禁用，请使用真实数据库数据")
        return {
            'market_sentiment': pd.DataFrame(),
            'limitup_events': pd.DataFrame(),
            'industry_daily': pd.DataFrame(),
            'dates': []
        }
    
    def _convert_db_data(self, data_list):
        """转换数据库返回的特殊数据类型为Python基本类型"""
        if not data_list:
            return []
        
        converted_data = []
        for item in data_list:
            converted_item = {}
            for key, value in item.items():
                # 转换Decimal为float
                if hasattr(value, '__class__') and 'Decimal' in str(value.__class__):
                    converted_item[key] = float(value)
                # 转换date为字符串
                elif hasattr(value, '__class__') and 'date' in str(value.__class__):
                    converted_item[key] = str(value)
                # 转换datetime为字符串
                elif hasattr(value, '__class__') and 'Timestamp' in str(value.__class__):
                    converted_item[key] = str(value)
                # 转换MySQL boolean (0/1) 为 Python boolean
                elif key in ['is_one_word', 'is_recap', 'is_new'] and value in [0, 1]:
                    converted_item[key] = bool(value)
                else:
                    converted_item[key] = value
            converted_data.append(converted_item)
        
        return converted_data
    
    def check_and_update_database(self):
        """检查数据库是否需要更新，如果需要则进行增量更新"""
        print("√ 检查数据库数据状态...")
        
        # 获取数据库中最新的交易日期
        latest_db_date = self.db.get_latest_trade_date()
        
        # 获取当前参考交易日（考虑是否已收盘）
        from trade_time import get_reference_trade_date
        current_date = get_reference_trade_date()
        current_date_str = current_date.strftime('%Y-%m-%d')
        
        # 存储最新日期用于UI显示
        self.latest_db_date = latest_db_date.strftime('%Y-%m-%d') if latest_db_date else current_date_str
        
        if latest_db_date:
            print(f"   数据库最新日期: {latest_db_date}")
            print(f"   当前日期: {current_date}")
            
            # 如果数据库日期不是最新，则进行更新
            if latest_db_date < current_date:
                print(f"   需要更新数据: {latest_db_date} -> {current_date}")
                self.update_database_incrementally(latest_db_date, current_date)
            else:
                print("   数据库数据已是最新，无需更新")
        else:
            print("   数据库为空，需要初始化数据")
            self.initialize_database_with_mock_data()
    
    def update_database_incrementally(self, start_date, end_date):
        """增量更新数据库数据"""
        print(f"√ 增量更新数据库数据: {start_date} 到 {end_date}")
        
        # 使用真实数据同步API
        from data_access_layer.limitup_sync_api import sync_limitup_data
        
        # 计算需要同步的天数
        from trade_time import trade_time_instance
        trade_time_instance.load_trade_dates()
        
        # 获取日期范围内的所有交易日
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        
        trade_dates_in_range = [
            date_str for date_str in trade_time_instance.trade_date_list 
            if start_str <= date_str <= end_str
        ]
        
        if not trade_dates_in_range:
            print("   无需更新，日期范围内无交易日")
            return
        
        # 同步数据（带超时保护）
        try:
            from threading import Thread
            import queue
            
            # 使用队列传递结果
            result_queue = queue.Queue()
            
            def sync_worker():
                try:
                    result = sync_limitup_data(len(trade_dates_in_range))
                    result_queue.put(("success", result))
                except Exception as e:
                    result_queue.put(("error", str(e)))
            
            # 启动工作线程
            worker_thread = Thread(target=sync_worker)
            worker_thread.daemon = True
            worker_thread.start()
            
            # 等待60秒
            worker_thread.join(60)
            
            if worker_thread.is_alive():
                print("⚠️  数据同步超时，跳过同步使用现有数据")
            else:
                # 获取结果
                result_type, result_value = result_queue.get_nowait()
                if result_type == "success":
                    print(f"√ 数据同步完成: {result_value}")
                else:
                    print(f"⚠️  数据同步失败: {result_value}")
                    
        except Exception as e:
            print(f"⚠️  数据同步异常: {e}")
    
    def generate_incremental_mock_data(self, start_date, end_date):
        """生成增量模拟数据（已禁用）"""
        print("❌ 模拟数据功能已禁用，请使用真实数据库数据")
        return {}
    
    def initialize_database_with_mock_data(self):
        """用模拟数据初始化数据库（已禁用）"""
        print("❌ 模拟数据初始化已禁用，请先同步真实数据")
        print("❌ 运行: python -m data_access_layer.limitup_sync_api 同步涨停数据")
        exit(1)
    
    def populate_stock_info_table(self):
        """填充股票基本信息表（已禁用）"""
        print("❌ 模拟股票信息已禁用，股票信息将从真实数据中获取")
        return 0
    
    def calculate_promotion_rates(self, current_date_str):
        """计算连板晋级率
        
        Args:
            current_date_str: 当前日期 (YYYYMMDD格式)
            
        Returns:
            Dict[int, float]: 各板级的晋级率，key为板级，value为晋级率百分比
        """
        promotion_rates = {}
        
        try:
            # 获取当前日期的数据
            ladder_data = self.data['limitup_events']
            current_date_data = ladder_data[ladder_data['date'] == current_date_str]
            
            if current_date_data.empty:
                return promotion_rates
            
            # 获取所有日期并排序
            all_dates = sorted(ladder_data['date'].unique())
            current_date_idx = all_dates.index(current_date_str)
            
            # 需要前一个交易日的数据来计算晋级率
            if current_date_idx == 0:
                return promotion_rates  # 没有前一个交易日
            
            previous_date_str = all_dates[current_date_idx - 1]
            previous_date_data = ladder_data[ladder_data['date'] == previous_date_str]
            
            if previous_date_data.empty:
                return promotion_rates
            
            # 计算各板级的数量（当前日期）
            current_board_counts = {}
            for board_level in range(1, 9):  # 1板到8板
                count = len(current_date_data[current_date_data['continuous_board_count'] == board_level])
                if count > 0:
                    current_board_counts[board_level] = count
            
            # 计算前一个交易日各板级的数量
            previous_board_counts = {}
            for board_level in range(1, 9):  # 1板到8板
                count = len(previous_date_data[previous_date_data['continuous_board_count'] == board_level])
                if count > 0:
                    previous_board_counts[board_level] = count
            
            # 计算晋级率（从n板晋级到n+1板的比率）
            for board_level in range(2, 9):  # 从2板开始计算晋级率
                if board_level in current_board_counts and (board_level - 1) in previous_board_counts:
                    current_count = current_board_counts[board_level]
                    previous_count = previous_board_counts[board_level - 1]
                    
                    if previous_count > 0:
                        promotion_rate = (current_count / previous_count) * 100
                        promotion_rates[board_level] = round(promotion_rate, 1)
                    else:
                        promotion_rates[board_level] = 0.0
                
        except Exception as e:
            print(f"计算晋级率时出错: {e}")
            return promotion_rates
        
        return promotion_rates
    
    def load_data_from_database(self):
        """从数据库加载数据"""
        print("√ 从数据库加载数据...")
        
        data = {}
        
        try:
            # 加载市场情绪数据
            sentiment_data = self.db.get_market_sentiment()
            data['market_sentiment'] = pd.DataFrame(self._convert_db_data(sentiment_data)) if sentiment_data else pd.DataFrame()
            
            # 加载连板个股数据 - 使用新的limitup_pool表
            # 获取最近5天的涨停数据（带超时保护）
            try:
                from threading import Thread
                import queue
                
                # 使用队列传递结果
                data_queue = queue.Queue()
                
                def data_worker():
                    try:
                        result = get_recent_limitup_data(5)
                        data_queue.put(("success", result))
                    except Exception as e:
                        data_queue.put(("error", str(e)))
                
                # 启动工作线程
                worker_thread = Thread(target=data_worker)
                worker_thread.daemon = True
                worker_thread.start()
                
                # 等待30秒
                worker_thread.join(30)
                
                if worker_thread.is_alive():
                    print("⚠️  连板数据加载超时，使用数据库现有数据")
                    # 从数据库直接获取最近数据
                    try:
                        # 获取所有数据然后筛选最近5天
                        all_data = self.db.get_limitup_events()
                        if all_data:
                            # 转换为DataFrame并筛选最近日期
                            df = pd.DataFrame(self._convert_db_data(all_data))
                            if not df.empty and 'date' in df.columns:
                                # 获取最近的日期
                                recent_dates = sorted(df['date'].unique(), reverse=True)[:5]
                                data['limitup_events'] = df[df['date'].isin(recent_dates)]
                            else:
                                data['limitup_events'] = df
                        else:
                            data['limitup_events'] = pd.DataFrame()
                    except:
                        data['limitup_events'] = pd.DataFrame()
                else:
                    # 获取结果
                    result_type, result_value = data_queue.get_nowait()
                    if result_type == "success":
                        data['limitup_events'] = pd.DataFrame(result_value) if result_value else pd.DataFrame()
                    else:
                        print(f"⚠️  连板数据加载失败: {result_value}")
                        data['limitup_events'] = pd.DataFrame()
                
            except Exception as e:
                print(f"⚠️  连板数据加载异常: {e}")
                data['limitup_events'] = pd.DataFrame()
            
            # 获取日期列表 - 优先使用连板数据的日期，按最新到最旧排序
            if not data['limitup_events'].empty:
                dates = sorted(data['limitup_events']['date'].unique(), reverse=True)
                # 最多显示5天数据
                data['dates'] = [str(date) for date in dates[:5]]
            elif not data['market_sentiment'].empty:
                dates = sorted(data['market_sentiment']['date'].unique(), reverse=True)
                # 最多显示5天数据
                data['dates'] = [str(date) for date in dates[:5]]
            else:
                # 如果没有数据，使用默认日期
                data['dates'] = ['20240901', '20240902', '20240903']
            
            print(f"√ 数据加载完成: ")
            print(f"   市场情绪: {len(data['market_sentiment'])} 条")
            print(f"   连板个股: {len(data['limitup_events'])} 条")
            
            # 调试信息：检查数据内容
            print(f"   市场情绪列名: {list(data['market_sentiment'].columns) if not data['market_sentiment'].empty else '空'}")
            print(f"   连板个股列名: {list(data['limitup_events'].columns) if not data['limitup_events'].empty else '空'}")
            # 调试：检查limitup_events数据来源
            if not data['limitup_events'].empty:
                print(f"   limitup_events数据来源: {type(data['limitup_events'])}")
                print(f"   limitup_events数据行数: {len(data['limitup_events'])}")
                print(f"   limitup_events包含的日期: {data['limitup_events']['date'].unique()}")
            if not data['market_sentiment'].empty:
                print(f"   最新市场情绪数据: {dict(data['market_sentiment'].iloc[-1])}")
            if not data['limitup_events'].empty:
                print(f"   首个连板个股: {dict(data['limitup_events'].iloc[0])}")
                # 调试：检查行业和题材数据
                first_stock = data['limitup_events'].iloc[0]
                print(first_stock)
                
            
        except Exception as e:
            print(f"❌ 数据库数据加载失败: {e}")
            print("❌ 程序退出")
            exit(1)
        
        return data
    
    def create_congestion_chart(self):
        """创建大盘拥挤度图表"""
        try:
            import akshare as ak
            # 获取拥挤度数据
            congestion_data = ak.stock_a_congestion_lg()
            
            # 获取市场活跃度数据
            activity_data = ak.stock_market_activity_legu()
            
            # 确保数据按日期排序
            congestion_data = congestion_data.sort_values('date')
            
            # 提取数据
            dates = congestion_data['date'].tolist()
            close_prices = congestion_data['close'].tolist()
            congestion_values = congestion_data['congestion'].tolist()
            
            # 默认只显示最近两个月的数据点
            two_months_count = min(60, len(dates))  # 最多显示60个数据点（约两个月）
            recent_dates = dates[-two_months_count:]
            recent_close_prices = close_prices[-two_months_count:]
            recent_congestion_values = congestion_values[-two_months_count:]
            
            # 计算Y轴范围，使振幅更明显 - 增加间距
            close_min = min(recent_close_prices)
            close_max = max(recent_close_prices)
            close_range = close_max - close_min
            # 设置20%的边距，增加振幅可见性
            close_y_min = close_min - close_range * 0.2
            close_y_max = close_max + close_range * 0.2
            
            # 拥挤度范围扩展以增加振幅可见性
            congestion_min = min(recent_congestion_values)
            congestion_max = max(recent_congestion_values)
            congestion_range = congestion_max - congestion_min
            congestion_y_min = max(0, congestion_min - congestion_range * 0.3)  # 30%边距
            congestion_y_max = min(1, congestion_max + congestion_range * 0.3)  # 30%边距
            
            # 创建双Y轴折线图
            line = (
                Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%", height="400px"))
                .add_xaxis(recent_dates)
                .add_yaxis(
                    "大盘点数",
                    recent_close_prices,
                    yaxis_index=0,
                    linestyle_opts=opts.LineStyleOpts(width=2, color="#ff9f0a"),
                    itemstyle_opts=opts.ItemStyleOpts(color="#ff9f0a"),
                    label_opts=opts.LabelOpts(is_show=True, position="top", color="#ff9f0a"),
                    markpoint_opts=opts.MarkPointOpts(
                        data=[
                            opts.MarkPointItem(type_="max", name="最高点"),
                            opts.MarkPointItem(type_="min", name="最低点")
                        ]
                    ),
                    is_smooth=True  # 启用平滑曲线
                )
                .add_yaxis(
                    "拥挤度",
                    recent_congestion_values,
                    yaxis_index=1,
                    linestyle_opts=opts.LineStyleOpts(width=2, color="#48dbfb"),
                    itemstyle_opts=opts.ItemStyleOpts(color="#48dbfb"),
                    label_opts=opts.LabelOpts(is_show=True, position="top", color="#48dbfb"),
                    markline_opts=opts.MarkLineOpts(
                        data=[
                            opts.MarkLineItem(y=0.5, name="警戒线", linestyle_opts=opts.LineStyleOpts(
                                type_="dashed", color="#ef4444", width=2
                            ))
                        ]
                    ),
                    is_smooth=True  # 启用平滑曲线
                )
                .extend_axis(
                    yaxis=opts.AxisOpts(
                        name="拥挤度",
                        type_="value",
                        position="right",
                        min_=congestion_y_min,
                        max_=congestion_y_max,
                        axisline_opts=opts.AxisLineOpts(
                            linestyle_opts=opts.LineStyleOpts(color="#48dbfb")
                        ),
                        axislabel_opts=opts.LabelOpts(formatter="{value}"),
                        splitline_opts=opts.SplitLineOpts(is_show=False)
                    )
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="大盘情绪", pos_left="center"),
                    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                    xaxis_opts=opts.AxisOpts(
                        type_="category",
                        boundary_gap=False,
                        axislabel_opts=opts.LabelOpts(rotate=45),
                        splitline_opts=opts.SplitLineOpts(is_show=False),
                        axisline_opts=opts.AxisLineOpts(is_show=False)
                    ),
                    yaxis_opts=opts.AxisOpts(
                        name="大盘点数",
                        type_="value",
                        position="left",
                        min_=close_y_min,
                        max_=close_y_max,
                        axisline_opts=opts.AxisLineOpts(
                            linestyle_opts=opts.LineStyleOpts(color="#ff9f0a")
                        ),
                        axislabel_opts=opts.LabelOpts(formatter="{value}"),
                        splitline_opts=opts.SplitLineOpts(is_show=False)
                    ),
                    datazoom_opts=[
                        opts.DataZoomOpts(
                            type_="inside",
                            range_start=50,  # 默认显示最近50%的数据（约两个月）
                            range_end=100
                        ),
                        opts.DataZoomOpts(
                            type_="slider",
                            is_show=True,
                            xaxis_index=[0],
                            pos_bottom="10%",
                            range_start=50,  # 默认显示最近50%的数据（约两个月）
                            range_end=100
                        )
                    ],
                    legend_opts=opts.LegendOpts(
                        pos_top="10%",
                        pos_right="10%"
                    )
                )
            )
            # 创建环形饼状图 - 只显示主要分类
            main_pie_items = ['上涨', '下跌', '平盘', '停牌']
            main_pie_data = []
            main_colors = ["#22c55e", "#ef4444", "#9ca3af", "#6b7280"]  # 绿、红、灰、深灰
            
            # 获取主要分类数据
            for i, item in enumerate(main_pie_items):
                item_data = activity_data[activity_data['item'] == item]
                if not item_data.empty:
                    value = item_data['value'].iloc[0]
                    if pd.notna(value) and value > 0:
                        main_pie_data.append((f"{item}: {int(value)}", value))
            
            # 获取统计日期
            stat_date = ""
            date_data = activity_data[activity_data['item'] == '统计日期']
            if not date_data.empty:
                stat_date = date_data['value'].iloc[0]
            
            # 创建环形饼图 - 左对齐并改进暗黑主题可见性
            pie_chart = (
                Pie(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="100%", height="400px"))
                .add(
                    "",
                    main_pie_data,
                    center=["50%", "50%"],  # 居中显示
                    radius=["40%", "70%"],  # 环形饼图
                    label_opts=opts.LabelOpts(
                        formatter="{b}",
                        position="outside",
                        font_size=12,
                        font_weight="bold",
                        color="#ffffff",  # 白色文字在暗黑主题中更明显
                        text_border_width=1,
                        text_border_color="rgba(0,0,0,0.5)"  # 添加黑色边框增强可见性
                    ),
                    tooltip_opts=opts.TooltipOpts(
                        trigger="item",
                        formatter="{a} <br/>{b} ({d}%)"
                    )
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(
                        title=f"市场状态分布\n{stat_date}",
                        pos_left="center",
                        pos_bottom="2%",  # 移动到图表底部
                        title_textstyle_opts=opts.TextStyleOpts(
                            font_size=14,
                            color="#ffffff"  # 白色标题
                        )
                    ),
                    legend_opts=opts.LegendOpts(
                        orient="vertical",
                        pos_left="10%",  # 左对齐图例
                        pos_top="25%",
                        type_="scroll",
                        textstyle_opts=opts.TextStyleOpts(
                            color="#ffffff"  # 白色图例文字
                        )
                    )
                )
                .set_colors(main_colors)
            )
            
            # 返回两个独立的图表对象，让HTML模板分别渲染
            return {
                'line_chart': line,
                'pie_chart': pie_chart
            }
            
        except Exception as e:
            print(f"❌ 获取图表数据失败: {e}")
            # 返回一个空的图表
            return Line(init_opts=opts.InitOpts(theme=ThemeType.DARK))
    
    def create_limitup_ladder(self):
        """创建连板天梯"""
        # 按日期和连板数分组
        ladder_data = self.data['limitup_events']
        dates = self.data['dates']
        
        ladder_html = ""
        for date in dates:
            # 转换日期格式匹配 (YYYYMMDD → YYYY-MM-DD)
            formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}" if len(date) == 8 and date.isdigit() else date
            date_data = ladder_data[ladder_data['date'] == date]
            if not date_data.empty:
                
                # 计算统计信息
                max_board = date_data['continuous_board_count'].max()
                one_word_count = date_data['is_one_word_board'].sum()
                board_break_count = len(date_data[date_data['board_break_count'] > 0])  # 统计有炸板的个股数量
                
                # 统计各板数量
                board_counts = {}
                for i in range(1, 9):  # 扩展到8板
                    count = len(date_data[date_data['continuous_board_count'] == i])
                    if count > 0:
                        board_counts[i] = count
                
                # 计算晋级率
                promotion_rates = self.calculate_promotion_rates(date)
                
                # 统计所有题材概念出现次数（拆分组合概念）
                theme_counts = {}
                for _, stock in date_data.iterrows():
                    themes = []
                    try:
                        if pd.notna(stock.get('themes')):
                            themes = json.loads(stock.get('themes', '[]'))
                    except (json.JSONDecodeError, TypeError):
                        themes = []
                    
                    # 拆分组合概念（如"半年报扭亏+品牌升级+数字化"拆分为单个概念）
                    for theme in themes:
                        # 按+号拆分概念
                        individual_themes = [t.strip() for t in theme.split('+') if t.strip()]
                        for individual_theme in individual_themes:
                            theme_counts[individual_theme] = theme_counts.get(individual_theme, 0) + 1
                
                # 按出现次数降序排序题材，取前10个
                sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                
                # 生成统计HTML
                stats_html = f'''
                <div class="summary-stats">
                    <div class="summary-item"><span class="summary-label">最高板:</span><span class="summary-value">{max_board}板</span></div>
                    <div class="summary-item"><span class="summary-label">一字板:</span><span class="summary-value">{one_word_count}个</span></div>
                    <div class="summary-item"><span class="summary-label">炸板数:</span><span class="summary-value">{board_break_count}个</span></div>
                '''
                
                # 添加各板数量统计（包含晋级率）
                for board, count in board_counts.items():
                    if board == 1:
                        # 1板不显示晋级率
                        stats_html += f'<div class="summary-item"><span class="summary-label">{board}板:</span><span class="summary-value">{count}个</span></div>'
                    else:
                        # 2板及以上显示晋级率
                        promotion_rate = promotion_rates.get(board, 0)
                        if promotion_rate > 0:
                            stats_html += f'<div class="summary-item"><span class="summary-label">{board}板:</span><span class="summary-value">{count}个 ({promotion_rate}%)</span></div>'
                        else:
                            stats_html += f'<div class="summary-item"><span class="summary-label">{board}板:</span><span class="summary-value">{count}个</span></div>'
                
                # 添加所有题材概念显示
                if sorted_themes:
                    stats_html += '<div class="theme-stats">'
                    for theme, count in sorted_themes:
                        stats_html += f'<div class="theme-stat-item"><span>{theme}</span><span class="theme-stat-count">{count}次</span></div>'
                    stats_html += '</div>'
                
                stats_html += '</div>'
                
                ladder_html += f'''
                <div class="date-column">
                    <h4 class="column-date">{formatted_date}</h4>
                    {stats_html}
                    <div class="ladder-cards">
                '''
                
                for _, stock in date_data.iterrows():
                    board_level = stock.get('continuous_board_count', 0)
                    badge_class = f"board-{board_level}"
                    badge_class += " one-word" if stock.get('is_one_word_board', False) else ""
                    badge_class += " board-break" if stock.get('board_break_count', 0) > 0 else ""
                    
                    # 格式化金额和换手率
                    amount_formatted = f"{stock.get('amount', 0):,.0f}" if pd.notna(stock.get('amount')) else "0"
                    turnover_formatted = f"{stock.get('turnover_rate', 0):.2f}" if pd.notna(stock.get('turnover_rate')) else "0.00"
                    
                    # 解析概念数据
                    themes = []
                    try:
                        if pd.notna(stock.get('themes')):
                            themes = json.loads(stock.get('themes', '[]'))
                    except (json.JSONDecodeError, TypeError):
                        themes = []
                    
                    themes_html = ''
                    if themes:
                        theme_tags = " ".join([f'<span class="theme-tag">{theme}</span>' for theme in themes[:3]])
                        themes_html = f'<div class="tags">{theme_tags}</div>'
                    
                    # 格式化总市值
                    total_market_value_formatted = f"{stock.get('total_market_value', 0):,.0f}" if pd.notna(stock.get('total_market_value')) else "0"
                    
                    ladder_html += f'''
                    <div class="limitup-card {badge_class}" onclick="showStockDetail('{stock.get('code', '')}')">
                        <div class="stock-header">
                            <span class="board-level">{stock.get('continuous_board_count', 0)}板</span>
                            <h5>{stock.get('name', '')}</h5>
                            <span class="stock-code">{stock.get('code', '')}</span>
                            {('<span class="one-word-badge">一字</span>' if stock.get('is_one_word_board', False) else '')}
                            {('<span class="board-break-badge">💥炸板</span>' if stock.get('board_break_count', 0) > 0 else '')}
                        </div>
                        <div class="stock-info">
                            <p>💰 最新价: {stock.get('latest_price', 0):.2f}</p>
                            <p>📊 总市值: {total_market_value_formatted}</p>
                            <p>📈 涨停时间: {stock.get('first_limit_time', '')} - {stock.get('last_limit_time', '')}</p>
                            <p>💥 炸板次数: {stock.get('board_break_count', 0)}次</p>
                            <p>📊 涨停统计: {stock.get('limit_up_count', '')}</p>
                            <p>🔄 换手率: {turnover_formatted}%</p>
                            <p>💰 成交额: {amount_formatted}</p>
                            <p>🏭 行业: {stock.get('industry', '')}</p>
                            {themes_html}
                        </div>
                    </div>
                    '''
                
                ladder_html += '''
                    </div>
                </div>
                '''
        
        return ladder_html
    
    def generate_market_options(self):
        """生成市场筛选选项"""
        market_options = ""
        market_boards = self.db.get_market_boards()
        
        # 映射市场板块到显示名称
        market_display_names = {
            '主板': '主板',
            '创业板': '创业板',
            '科创板': '科创板'
        }
        
        for board in market_boards:
            display_name = market_display_names.get(board, board)
            market_options += f'<option value="{board}">{display_name}</option>\n'
        
        return market_options

    def generate_enhanced_html(self):
        """生成增强版HTML页面"""
        # 创建各个模块的内容
        congestion_chart = self.create_congestion_chart()
        ladder_content = self.create_limitup_ladder()
        market_options = self.generate_market_options()
        
        # 获取所有可用日期（按最新到最旧排序）
        all_dates = []
        if not self.data['limitup_events'].empty:
            all_dates = sorted(self.data['limitup_events']['date'].unique(), reverse=True)
        elif not self.data['market_sentiment'].empty:
            all_dates = sorted(self.data['market_sentiment']['date'].unique(), reverse=True)
        all_dates = [str(date) for date in all_dates]
        
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

        .pagination-controls {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-right: 20px;
        }

        .pagination-btn {
            padding: 6px 12px;
            background: var(--chip-bg);
            color: var(--text);
            border: 1px solid var(--grid-border);
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9em;
        }

        .pagination-btn:hover {
            background: var(--accent);
            color: #000;
        }

        .pagination-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .page-info {
            font-size: 0.9em;
            color: var(--muted);
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
            max-height: calc(100vh - 200px);
            overflow-y: auto;
        }
        
        .date-column {
            min-width: 400px; /* 增加宽度以显示统计信息 */
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
        
        .summary-stats {
            background: var(--chip-bg);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid var(--grid-border);
        }
        
        .summary-item {
            display: flex;
            justify-content: space-between;
            margin: 4px 0;
            font-size: 0.85em;
        }
        
        .summary-label {
            color: var(--muted);
        }
        
        .summary-value {
            color: var(--accent);
            font-weight: bold;
        }
        
        
        
        
        .ladder-cards, .industry-cards {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .limitup-card, .industry-card {
            background: var(--chip-bg);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid var(--accent);
            cursor: pointer;
            transition: all 0.3s;
            min-height: 280px; /* 增加最小高度以显示完整内容 */
        }
        
        .limitup-card:hover, .industry-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }
        
        /* 不同板级边框颜色 */
        .limitup-card.board-1 { border-left-color: #ff6b6b; }
        .limitup-card.board-2 { border-left-color: #feca57; }
        .limitup-card.board-3 { border-left-color: #48dbfb; }
        .limitup-card.board-4 { border-left-color: #1dd1a1; }
        .limitup-card.board-5 { border-left-color: #ff9ff3; }
        .limitup-card.board-6 { border-left-color: #f368e0; }
        .limitup-card.board-7 { border-left-color: #ff9f0a; }
        .limitup-card.board-8 { border-left-color: #ee5253; }
        
        .limitup-card.one-word {
            border-left-color: var(--badge-purple);
        }
        
        .limitup-card.board-break {
            background: linear-gradient(135deg, var(--chip-bg) 0%, #ff6b6b20 100%);
        }
        
        .stock-header, .industry-header {
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
        
        .one-word-badge {
            background: var(--badge-purple);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 8px;
        }
        
        .board-break-badge {
            background: var(--red);
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 8px;
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
        
        .stock-info p, .industry-info p {
            margin: 4px 0;
            font-size: 0.9em;
        }
        
        .tags {
            display: flex;
            gap: 6px;
            margin-top: 8px;
        }
        
        .industry-tag {
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
            <h2>📈 Bandit</h2>
            <a href="#" class="nav-item active" onclick="switchPage('ladder')">
                <span class="nav-icon">📊</span> 市场分析
            </a>
        </aside>
        
        <!-- 顶部时间轴 -->
        <header class="header">
            <div class="timeline">
                <h3>市场分析仪表板</h3>
                <div class="pagination-controls">
                    <button class="pagination-btn" onclick="changePage(-1)" id="prevBtn">← 上一页</button>
                    <span class="page-info" id="pageInfo">第 1 页 / 共 1 页</span>
                    <button class="pagination-btn" onclick="changePage(1)" id="nextBtn">下一页 →</button>
                </div>
            </div>
        </header>
        
        <!-- 主要内容区 -->
        <main class="main">
            <!-- 市场分析页面 -->
            <div id="ladder-page" class="content-section">
                <!-- 大盘情绪图表 -->
                <h3 class="section-title">📊 大盘情绪</h3>
                <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                    <!-- 左边图表 - 占2/3空间 -->
                    <div style="flex: 2;">
                        <div class="chart-container">
                            <div id="line-chart" class="chart"></div>
                        </div>
                    </div>
                    <!-- 右边饼图 - 占1/3空间 -->
                    <div style="flex: 1;">
                        <div class="chart-container">
                            <div id="pie-chart" class="chart"></div>
                        </div>
                    </div>
                </div>
                
                <!-- 连板天梯 -->
                <h3 class="section-title">🏆 连板天梯</h3>
                <div class="scrollable-columns">
                    {{ladder_content}}
                </div>
            </div>
            
            
        </main>
        
        <!-- 页脚 -->
        <footer class="footer">
            <p>© 2024 Bandit分析系统 | 数据更新时间: {{current_time}} | 使用pywencai&akshare数据</p>
        </footer>
    </div>
    
    <script>
        // 初始化图表
        function initCharts() {
            // 初始化折线图
            var lineChart = echarts.init(document.getElementById('line-chart'));
            lineChart.setOption({{line_chart_option}});
            
            // 初始化饼图
            var pieChart = echarts.init(document.getElementById('pie-chart'));
            pieChart.setOption({{pie_chart_option}});
            
            // 窗口调整时重绘图表
            window.addEventListener('resize', function() {
                lineChart.resize();
                pieChart.resize();
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
        
        

        // 分页功能
        let currentPage = 1;
        const pageSize = 5; // 每页显示5天数据
        const allDates = {{all_dates}}; // 所有可用日期

        function changePage(direction) {
            const totalPages = Math.ceil(allDates.length / pageSize);
            currentPage += direction;
            
            // 限制页码范围
            if (currentPage < 1) currentPage = 1;
            if (currentPage > totalPages) currentPage = totalPages;
            
            // 更新分页按钮状态
            updatePaginationControls();
            
            // 更新显示的数据
            updateDisplayedData();
        }

        function updatePaginationControls() {
            const totalPages = Math.ceil(allDates.length / pageSize);
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            const pageInfo = document.getElementById('pageInfo');
            
            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage === totalPages;
            pageInfo.textContent = `第 ${currentPage} 页 / 共 ${totalPages} 页`;
        }

        function updateDisplayedData() {
            const startIndex = (currentPage - 1) * pageSize;
            const endIndex = startIndex + pageSize;
            const currentDates = allDates.slice(startIndex, endIndex);
            
            console.log('显示日期:', currentDates);
            // 这里可以添加AJAX请求来更新页面数据
            alert(`已切换到第 ${currentPage} 页，显示日期: ${currentDates.join(', ')}`);
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            // 初始化图表
            initCharts();
            // 初始化分页控件
            updatePaginationControls();
        });
    </script>
</body>
</html>
        '''
        
        # 替换模板中的变量
        html_content = html_template
        html_content = html_content.replace('{{current_time}}', self.latest_db_date)
        html_content = html_content.replace('{{market_options}}', market_options)
        html_content = html_content.replace('{{ladder_content}}', ladder_content)
        html_content = html_content.replace('{{line_chart_option}}', congestion_chart['line_chart'].dump_options())
        html_content = html_content.replace('{{pie_chart_option}}', congestion_chart['pie_chart'].dump_options())
        html_content = html_content.replace('{{all_dates}}', json.dumps(all_dates))
        
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
    dashboard = EnhancedStockDashboard()
    
    # 生成HTML
    html_file = dashboard.generate_enhanced_html()
    
    # 在浏览器中打开
    dashboard.open_in_browser()
    
    print("增强版仪表板生成完成!")

if __name__ == "__main__":
    main()
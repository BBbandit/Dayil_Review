#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票市场分析仪表板主程序
集成PyEcharts和Plotly可视化，自动生成HTML并在浏览器中打开
"""

import os
import webbrowser
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pyecharts.charts import Line, Bar, HeatMap, Graph
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 创建输出目录
os.makedirs('output', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

class StockDashboard:
    def __init__(self):
        self.data = self.generate_sample_data()
        self.html_file = 'output/stock_dashboard.html'
    
    def generate_sample_data(self):
        """生成示例数据"""
        dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
        
        # 生成股票数据
        stocks = ['贵州茅台', '宁德时代', '比亚迪', '隆基绿能', '药明康德']
        
        data = {
            'date': [],
            'stock': [],
            'price': [],
            'change': [],
            'volume': [],
            'theme': [],
            'status': []
        }
        
        themes = ['白酒', '新能源', '汽车', '光伏', '医药']
        statuses = ['上涨', '下跌', '横盘', '突破', '回调']
        
        for date in dates:
            for i, stock in enumerate(stocks):
                data['date'].append(date.strftime('%Y-%m-%d'))
                data['stock'].append(stock)
                data['price'].append(round(100 + np.random.randn() * 20, 2))
                data['change'].append(round(np.random.randn() * 5, 2))
                data['volume'].append(int(1000000 + np.random.randn() * 200000))
                data['theme'].append(themes[i % len(themes)])
                data['status'].append(np.random.choice(statuses))
        
        return pd.DataFrame(data)
    
    def create_market_sentiment_chart(self):
        """创建大盘情绪图表"""
        sentiment_data = self.data.groupby('date').agg({
            'change': 'mean',
            'volume': 'sum'
        }).reset_index()
        
        line = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.DARK))
            .add_xaxis(sentiment_data['date'].tolist())
            .add_yaxis("平均涨跌幅", 
                      sentiment_data['change'].round(2).tolist(),
                      is_smooth=True,
                      label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("总成交量", 
                      (sentiment_data['volume'] / 1000000).round(2).tolist(),
                      yaxis_index=1,
                      is_smooth=True,
                      label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="大盘情绪分析"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="涨跌幅(%)",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                datazoom_opts=[opts.DataZoomOpts()],
            )
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="成交量(百万)",
                    position="right",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    axisline_opts=opts.AxisLineOpts(is_show=True),
                    axislabel_opts=opts.LabelOpts(formatter="{value} 百万"),
                )
            )
        )
        return line
    
    def create_heatmap_chart(self):
        """创建热力图"""
        # 生成热力图数据
        dates = sorted(self.data['date'].unique())
        stocks = self.data['stock'].unique()
        
        heatmap_data = []
        for i, date in enumerate(dates):
            for j, stock in enumerate(stocks):
                stock_data = self.data[(self.data['date'] == date) & (self.data['stock'] == stock)]
                if not stock_data.empty:
                    change = stock_data['change'].iloc[0]
                    heatmap_data.append([i, j, change])
        
        heatmap = (
            HeatMap()
            .add_xaxis(dates)
            .add_yaxis(
                "涨跌幅热力图",
                stocks.tolist(),
                heatmap_data,
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="个股涨跌幅热力图"),
                visualmap_opts=opts.VisualMapOpts(
                    min_=-10, max_=10, is_calculable=True, orient="horizontal", pos_left="center"
                ),
            )
        )
        return heatmap
    
    def create_stock_cards_html(self):
        """生成个股卡片HTML"""
        latest_data = self.data[self.data['date'] == self.data['date'].max()]
        
        cards_html = []
        status_colors = {
            '上涨': '#ff4d4f',
            '下跌': '#52c41a', 
            '横盘': '#faad14',
            '突破': '#1890ff',
            '回调': '#722ed1'
        }
        
        theme_colors = {
            '白酒': '#cf1322',
            '新能源': '#389e0d',
            '汽车': '#096dd9',
            '光伏': '#d46b08',
            '医药': '#531dab'
        }
        
        for _, row in latest_data.iterrows():
            card_html = f'''
            <div class="stock-card" style="border-left: 4px solid {status_colors.get(row['status'], '#666')};">
                <div class="stock-header">
                    <h4>{row['stock']}</h4>
                    <span class="theme-tag" style="background: {theme_colors.get(row['theme'], '#666')};">
                        {row['theme']}
                    </span>
                </div>
                <div class="stock-info">
                    <p>价格: {row['price']}</p>
                    <p class="change {'positive' if row['change'] > 0 else 'negative'}">
                        涨跌: {row['change']}%
                    </p>
                    <p>成交量: {row['volume']:,}</p>
                    <p>状态: <span style="color: {status_colors.get(row['status'], '#666')}">
                        {row['status']}
                    </span></p>
                </div>
            </div>
            '''
            cards_html.append(card_html)
        
        return '\n'.join(cards_html)
    
    def generate_html(self):
        """生成完整的HTML页面"""
        # 创建图表
        sentiment_chart = self.create_market_sentiment_chart()
        heatmap_chart = self.create_heatmap_chart()
        stock_cards = self.create_stock_cards_html()
        
        # 读取模板
        html_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票市场分析仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            display: grid;
            grid-template-columns: 250px 1fr;
            grid-template-rows: auto 1fr auto;
            grid-template-areas: 
                "sidebar header"
                "sidebar main"
                "sidebar footer";
            min-height: 100vh;
        }
        
        .sidebar {
            grid-area: sidebar;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-right: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .sidebar h2 {
            color: white;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .nav-item {
            display: block;
            padding: 12px 16px;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 8px;
            transition: background 0.3s;
        }
        
        .nav-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .nav-item.active {
            background: rgba(255, 255, 255, 0.3);
            font-weight: bold;
        }
        
        .header {
            grid-area: header;
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .timeline {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .date-picker {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
        }
        
        .main {
            grid-area: main;
            padding: 20px;
            overflow-y: auto;
        }
        
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .chart {
            width: 100%;
            height: 400px;
        }
        
        .stock-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .stock-card {
            background: white;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        
        .stock-card:hover {
            transform: translateY(-2px);
        }
        
        .stock-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .stock-header h4 {
            margin: 0;
            flex: 1;
        }
        
        .theme-tag {
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }
        
        .stock-info p {
            margin: 4px 0;
            color: #666;
        }
        
        .change.positive {
            color: #ff4d4f;
            font-weight: bold;
        }
        
        .change.negative {
            color: #52c41a;
            font-weight: bold;
        }
        
        .footer {
            grid-area: footer;
            background: rgba(255, 255, 255, 0.9);
            padding: 15px 20px;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 左侧导航栏 -->
        <aside class="sidebar">
            <h2>📈 Bandit</h2>
            <a href="#" class="nav-item active">📊 大盘情绪</a>
            <a href="#" class="nav-item">🏆 连板天梯</a>
            <a href="#" class="nav-item">💰 资金流向</a>
            <a href="#" class="nav-item">🔥 热门题材</a>
            <a href="#" class="nav-item">📋 个股排名</a>
            <a href="#" class="nav-item">⚡ 实时监控</a>
        </aside>
        
        <!-- 顶部时间轴 -->
        <header class="header">
            <div class="timeline">
                <h3>市场分析仪表板</h3>
                <input type="date" class="date-picker" value="{{current_date}}">
                <span>至</span>
                <input type="date" class="date-picker" value="{{current_date}}">
                <button onclick="updateCharts()">应用</button>
            </div>
        </header>
        
        <!-- 主要内容区 -->
        <main class="main">
            <!-- 大盘情绪图表 -->
            <div class="chart-container">
                <h3>大盘情绪分析</h3>
                <div id="sentiment-chart" class="chart"></div>
            </div>
            
            <!-- 热力图 -->
            <div class="chart-container">
                <h3>个股涨跌幅热力图</h3>
                <div id="heatmap-chart" class="chart"></div>
            </div>
            
            <!-- 个股卡片 -->
            <div class="chart-container">
                <h3>题材个股表现</h3>
                <div class="stock-grid">
                    {{stock_cards}}
                </div>
            </div>
        </main>
        
        <!-- 页脚 -->
        <footer class="footer">
            <p>© 2024 Bandit分析系统 | 最后更新: {{current_time}}</p>
        </footer>
    </div>
    
    <script>
        // 初始化图表
        function initCharts() {
            // 大盘情绪图表
            var sentimentChart = echarts.init(document.getElementById('sentiment-chart'));
            sentimentChart.setOption({{sentiment_chart_option}});
            
            // 热力图
            var heatmapChart = echarts.init(document.getElementById('heatmap-chart'));
            heatmapChart.setOption({{heatmap_chart_option}});
            
            // 窗口调整时重绘图表
            window.addEventListener('resize', function() {
                sentimentChart.resize();
                heatmapChart.resize();
            });
        }
        
        // 更新图表数据
        function updateCharts() {
            // 这里可以添加AJAX请求来更新数据
            console.log('更新图表数据...');
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', initCharts);
    </script>
</body>
</html>
        '''
        
        # 替换模板中的变量
        html_content = html_template
        html_content = html_content.replace('{{current_date}}', datetime.now().strftime('%Y-%m-%d'))
        html_content = html_content.replace('{{current_time}}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        html_content = html_content.replace('{{stock_cards}}', stock_cards)
        html_content = html_content.replace('{{sentiment_chart_option}}', sentiment_chart.dump_options())
        html_content = html_content.replace('{{heatmap_chart_option}}', heatmap_chart.dump_options())
        
        # 写入HTML文件
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return self.html_file
    
    def open_in_browser(self):
        """在浏览器中打开生成的HTML"""
        webbrowser.open('file://' + os.path.abspath(self.html_file))
        print(f"仪表板已生成: {os.path.abspath(self.html_file)}")

def main():
    """主函数"""
    print("正在生成股票市场分析仪表板...")
    
    # 创建仪表板实例
    dashboard = StockDashboard()
    
    # 生成HTML
    html_file = dashboard.generate_html()
    
    # 在浏览器中打开
    dashboard.open_in_browser()
    
    print("仪表板生成完成!")

if __name__ == "__main__":
    main()
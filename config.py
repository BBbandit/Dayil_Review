# 配置文件

# 数据源配置
DATA_SOURCES = {
    'csv': {
        'path': 'data/stock_data.csv',
        'encoding': 'utf-8'
    },
    'api': {
        'url': 'https://api.example.com/stock-data',
        'api_key': 'your_api_key_here'
    }
}

# 图表配置
CHART_CONFIG = {
    'width': '100%',
    'height': '400px',
    'theme': 'dark',
    'background_color': '#ffffff'
}

# 颜色配置
COLOR_CONFIG = {
    'status_colors': {
        '上涨': '#ff4d4f',      # 红色
        '下跌': '#52c41a',      # 绿色
        '横盘': '#faad14',      # 黄色
        '突破': '#1890ff',      # 蓝色
        '回调': '#722ed1'       # 紫色
    },
    'theme_colors': {
        '白酒': '#cf1322',      # 深红
        '新能源': '#389e0d',    # 深绿
        '汽车': '#096dd9',      # 深蓝
        '光伏': '#d46b08',      # 橙色
        '医药': '#531dab',      # 深紫
        '科技': '#c41d7f',      # 玫红
        '金融': '#08979c'       # 青蓝
    }
}

# 界面配置
UI_CONFIG = {
    'auto_open_browser': True,
    'refresh_interval': 300,  # 5分钟
    'default_date_range': 30  # 默认显示30天数据
}
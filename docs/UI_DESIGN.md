# UI 设计规范与实现指南

## 🎨 整体设计风格

### 设计主题
- **主题**: 深色主题 (近黑背景 + 高对比文字 + 彩色状态)
- **背景色**: `#0f1115` / `#111318`
- **面板色**: `#151922` / `#1a1f2b`
- **文本色**: 
  - 主文本: `#e5e7eb`
  - 次要文本: `#9aa3b2`
- **强调色**: 橙色 `#ff9f0a` (用于当前导航与提示按钮)
- **涨跌色**: 
  - 上涨: 红色 `#ef4444`
  - 下跌: 绿色 `#22c55e`
- **中性色热度**: 从 `#133015`→`#0b1b2d` (冷) 到 `#3b0b0b` (热)

### 布局结构
- **左侧导航**: 固定纵向导航栏，宽度 ~200px
- **右侧内容**: 横向多日对比的可滚动区域 (列=日期)
- **顶部功能区**: 日期滚动条/面包屑导航

### 交互规范
- **列结构**: 每列代表一个日期
- **内容承载**: 指标热力图/题材榜/行业榜/连板个股卡片
- **悬停提示**: 显示维度名、统计口径、数值、分位/同比/环比
- **详情交互**: 点击卡片 → 右侧抽屉展示详细图表
- **筛选功能**: 日期区间、市场选择、成交额门槛、涨跌幅阈值

## 📊 页面功能模块

### 1. 大盘情绪 (/dashboard)

#### 布局优化
```html
<div class="dashboard-container">
    <!-- 左侧导航栏保持不变 -->
    <aside class="sidebar">...</aside>
    
    <!-- 右侧主区域 -->
    <main class="main-content">
        <!-- 顶部KPI区域 -->
        <div class="kpi-stats-grid">
            <div class="kpi-stat">总成交额</div>
            <div class="kpi-stat">涨跌家数</div>
            <div class="kpi-stat">开盘涨停</div>
            <div class="kpi-stat">收盘涨停</div>
            <div class="kpi-stat">上证上涨率</div>
            <div class="kpi-stat">深证上涨率</div>
            <div class="kpi-stat">创业板上涨率</div>
        </div>
        
        <!-- 下部两列布局 -->
        <div class="dashboard-columns">
            <!-- 左侧表格 -->
            <div class="market-summary-table">
                <table>
                    <thead><tr><th>指标</th><th>日期1</th><th>日期2</th></tr></thead>
                    <tbody>...</tbody>
                </table>
            </div>
            
            <!-- 右侧热力图 -->
            <div class="heatmap-container">
                <div id="industry-heatmap" class="chart"></div>
            </div>
        </div>
    </main>
</div>
```

#### KPI显示规则
- **数值上升**: 绿色 `#22c55e`
- **数值下降**: 红色 `#ef4444`  
- **数值为0**: 灰色 `#9ca3af`

#### 热力图配置
```javascript
visualMap: {
    min: -8,
    max: 8,
    inRange: {
        color: ['#dc2626', '#ef4444', '#9ca3af', '#22c55e', '#16a34a']
    }
}
```

### 2. 连板天梯 (/ladder)

#### 顶部统计条
```html
<div class="top-stats-bar">
    <div class="stat-item" data-filter="6+">6板以上 <span class="count">2</span></div>
    <div class="stat-item" data-filter="5">5板 <span class="count">3</span></div>
    <div class="stat-item" data-filter="4">4板 <span class="count">5</span></div>
    <div class="stat-item" data-filter="3">3板 <span class="count">8</span></div>
    <div class="stat-item" data-filter="2">2板 <span class="count">12</span></div>
    <div class="stat-item" data-filter="1">1板 <span class="count">25</span></div>
    <div class="stat-item" data-filter="跌停">跌停 <span class="count">5</span></div>
</div>
```

#### 题材热度聚合
```html
<div class="theme-aggregation">
    <div class="theme-tag" data-theme="人工智能">人工智能 (5)</div>
    <div class="theme-tag" data-theme="新能源汽车">新能源汽车 (3)</div>
    <div class="theme-tag" data-theme="光伏">光伏 (4)</div>
</div>
```

#### 股票卡片增强
```html
<div class="stock-card" data-board-level="5" data-themes="人工智能,芯片">
    <div class="board-badge">5板</div>
    <h4>科大讯飞</h4>
    <div class="stock-code">002230</div>
    <div class="stock-info">
        <span class="change positive">+9.98%</span>
        <span class="volume">15.2亿</span>
        <span class="turnover">8.5%</span>
    </div>
    <div class="theme-tags">
        <span class="theme-tag">人工智能</span>
        <span class="theme-tag">芯片</span>
    </div>
    <div class="market-tag">中小板</div>
</div>
```

### 3. 题材热度 (/themes)

#### 表现墙卡片
```html
<div class="theme-performance-wall">
    <div class="theme-card" data-theme="人工智能" data-change="3.5" data-heat="85">
        <div class="theme-header">
            <h5>人工智能</h5>
            <span class="heat-score">🔥85</span>
        </div>
        <div class="change-indicator positive">+3.5%</div>
        <div class="theme-tags">
            <span class="tag hot">热门</span>
            <span class="tag volume">爆量</span>
        </div>
        <div class="hover-info">
            领涨股: 科大讯飞 +10%, 海康威视 +8.5%
        </div>
    </div>
</div>
```

### 4. 行业追踪 (/industry)

#### 行业排名卡片
```html
<div class="industry-rank-cards">
    <div class="industry-card rank-1">
        <div class="rank-badge">#1</div>
        <h5>半导体</h5>
        <div class="change positive">+4.2%</div>
        <div class="leaders">
            <span>中芯国际 +10%</span>
            <span>韦尔股份 +8.5%</span>
        </div>
        <div class="metrics">
            <span>人气: 92</span>
            <span>成交: 280亿</span>
        </div>
    </div>
</div>
```

## 🎨 样式规范增强

### 颜色体系扩展
```css
:root {
    /* 现有颜色变量保持 */
    --green-up: #22c55e;      /* 上涨 */
    --green-up-dark: #16a34a; /* 深绿 */
    --red-down: #ef4444;      /* 下跌 */
    --red-down-dark: #dc2626; /* 深红 */
    --gray-neutral: #9ca3af;  /* 中性 */
    
    /* 新增排名颜色 */
    --rank-1: #fbbf24;        /* 第一名 */
    --rank-2: #94a3b8;        /* 第二名 */
    --rank-3: #b45309;        /* 第三名 */
    
    /* 新增标签颜色 */
    --tag-hot: #ef4444;       /* 热门标签 */
    --tag-volume: #8b5cf6;    /* 爆量标签 */
    --tag-new: #06b6d4;       /* 新题材标签 */
}
```

### 交互效果增强
```css
/* 悬停效果增强 */
.kpi-stat:hover, .stat-item:hover, .theme-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 点击效果 */
.stat-item:active, .theme-tag:active {
    transform: translateY(1px);
}

/* 选中状态 */
.stat-item.active, .theme-tag.active {
    background: var(--accent);
    color: #000;
    font-weight: bold;
}

/* 排名样式 */
.rank-1 { border-left-color: var(--rank-1); }
.rank-2 { border-left-color: var(--rank-2); }
.rank-3 { border-left-color: var(--rank-3); }
```

## 📈 大盘情绪多折线对比图

### 图例项目（8条折线）
| 指标名称 | 颜色 | 图标 | 说明 |
|---------|------|------|------|
| 收盘上涨率 | `#3498db` (蓝色) | ● | 收盘时上涨股票比例 |
| 盘中上涨率 | `#27ae60` (绿色) | ● | 盘中最高上涨股票比例 |
| 上证上涨率 | `#f39c12` (黄色) | ● | 上证指数成分股上涨比例 |
| 深证上涨率 | `#e74c3c` (红色) | ● | 深证指数成分股上涨比例 |
| 创业板上涨率 | `#e67e22` (橙色) | ● | 创业板指数成分股上涨比例 |
| 上日强势票上涨率 | `#3498db80` (浅蓝色) | ● | 前日强势股票今日上涨比例 |
| 上日妖股上涨率 | `#e83e8c` (粉色) | ● | 前日妖股今日上涨比例 |
| 上日弱势票上涨率 | `#9b59b6` (紫色) | ● | 前日弱势股票今日上涨比例 |

### 坐标轴配置
- **X轴**: 日期（YYYYMMDD格式），浅灰色轴线，白色标签
- **Y轴**: 0-100百分比值，浅灰色轴线，细灰色虚线网格

### 折线样式
```javascript
{
    type: 'line',
    smooth: true,           // 启用曲线过渡
    symbol: 'circle',       // 圆点标记
    symbolSize: 6,          // 标记点大小
    lineStyle: {
        width: 2,           // 线条宽度
        opacity: 0.8        // 线条透明度
    }
}
```

## 🌐 API 接口规范

### 基础接口格式
所有API返回统一格式：
```json
{
    "code": 200,
    "message": "success",
    "data": {},
    "timestamp": 1736112000
}
```

### 1. 大盘情绪接口

#### 获取KPI统计数据
**Endpoint**: `GET /api/market/kpi`
**参数**: 
- `date` (可选): 指定日期，格式YYYYMMDD，默认最新日期

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "total_turnover": 12500.5,      // 总成交额（亿元）
        "advance_decline_count": 3200,  // 涨跌家数（上涨家数）
        "open_limitup": 45,             // 开盘涨停
        "close_limitup": 38,            // 收盘涨停
        "sh_advance_rate": 62.5,        // 上证上涨率
        "sz_advance_rate": 58.3,        // 深证上涨率
        "cyb_advance_rate": 55.8,       // 创业板上涨率
        "date": "20250905"              // 数据日期
    }
}
```

#### 获取多折线对比数据
**Endpoint**: `GET /api/market/trend`
**参数**:
- `start_date`: 开始日期，格式YYYYMMDD
- `end_date`: 结束日期，格式YYYYMMDD
- `indicators` (可选): 指定指标，逗号分隔

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "dates": ["20250901", "20250902", "20250903", "20250904", "20250905"],
        "indicators": {
            "close_advance_rate": [65.2, 62.8, 58.3, 61.5, 62.5],
            "intraday_advance_rate": [68.7, 65.2, 60.1, 63.8, 64.2],
            "sh_advance_rate": [63.5, 60.8, 56.2, 59.3, 60.1],
            "sz_advance_rate": [59.8, 57.3, 53.1, 56.2, 57.5],
            "cyb_advance_rate": [56.3, 54.1, 50.2, 53.1, 54.8],
            "prev_strong_advance_rate": [62.1, 59.8, 55.3, 58.2, 59.5],
            "prev_hot_advance_rate": [58.7, 56.2, 52.1, 54.8, 56.3],
            "prev_weak_advance_rate": [51.2, 49.8, 46.3, 48.7, 50.2]
        }
    }
}
```

#### 获取热力图数据
**Endpoint**: `GET /api/market/heatmap`
**参数**:
- `date`: 日期，格式YYYYMMDD

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "date": "20250905",
        "industries": [
            {
                "name": "半导体",
                "change": 4.2,
                "heat_score": 92,
                "turnover": 280.5
            },
            {
                "name": "新能源汽车", 
                "change": 3.8,
                "heat_score": 88,
                "turnover": 320.2
            }
        ]
    }
}
```

### 2. 连板天梯接口

#### 获取连板统计
**Endpoint**: `GET /api/ladder/stats`
**参数**:
- `date`: 日期，格式YYYYMMDD

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "date": "20250905",
        "board_stats": {
            "6+": 2,
            "5": 3,
            "4": 5,
            "3": 8,
            "2": 12,
            "1": 25,
            "跌停": 5
        },
        "total_count": 56
    }
}
```

#### 获取题材聚合
**Endpoint**: `GET /api/ladder/themes`
**参数**:
- `date`: 日期，格式YYYYMMDD
- `min_count` (可选): 最小出现次数，默认2

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "date": "20250905",
        "themes": [
            {"name": "人工智能", "count": 5, "stocks": ["002230", "002415"]},
            {"name": "新能源汽车", "count": 3, "stocks": ["002594", "300750"]},
            {"name": "光伏", "count": 4, "stocks": ["601012", "300274"]}
        ]
    }
}
```

#### 获取连板个股列表
**Endpoint**: `GET /api/ladder/stocks`
**参数**:
- `date`: 日期，格式YYYYMMDD
- `board_level` (可选): 板数过滤
- `theme` (可选): 题材过滤
- `market` (可选): 市场过滤

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "date": "20250905",
        "stocks": [
            {
                "ticker": "002230",
                "name": "科大讯飞",
                "board_level": 5,
                "change": 9.98,
                "turnover": 8.5,
                "amount": 15.2,
                "themes": ["人工智能", "芯片"],
                "market": "中小板",
                "is_one_word": false,
                "is_recap": false
            }
        ]
    }
}
```

### 3. 题材热度接口

#### 获取题材表现墙
**Endpoint**: `GET /api/themes/wall`
**参数**:
- `date`: 日期，格式YYYYMMDD
- `min_heat` (可选): 最小热度值，默认60

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "date": "20250905",
        "themes": [
            {
                "name": "人工智能",
                "change": 3.5,
                "heat_score": 85,
                "limitup_count": 8,
                "is_hot": true,
                "is_high_volume": true,
                "leaders": [
                    {"ticker": "002230", "name": "科大讯飞", "change": 10.0},
                    {"ticker": "002415", "name": "海康威视", "change": 8.5}
                ]
            }
        ]
    }
}
```

#### 获取题材榜单
**Endpoint**: `GET /api/themes/ranking`
**参数**:
- `date`: 日期，格式YYYYMMDD
- `sort_by` (可选): 排序字段，默认heat_score
- `sort_order` (可选): 排序顺序，desc/asc

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "date": "20250905",
        "ranking": [
            {
                "name": "人工智能",
                "change": 3.5,
                "heat_score": 85,
                "limitup_count": 8,
                "stock_count": 15,
                "strength": 92,
                "streak_days": 3
            }
        ]
    }
}
```

#### 获取题材趋势
**Endpoint**: `GET /api/themes/trend`
**参数**:
- `theme_name`: 题材名称
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "theme": "人工智能",
        "trends": {
            "dates": ["20250901", "20250902", "20250903", "20250904", "20250905"],
            "changes": [2.1, 1.8, 3.2, 2.8, 3.5],
            "heat_scores": [75, 78, 82, 80, 85],
            "limitup_counts": [5, 6, 7, 6, 8]
        }
    }
}
```

### 4. 行业追踪接口

#### 获取行业排名
**Endpoint**: `GET /api/industry/ranking`
**参数**:
- `date`: 日期，格式YYYYMMDD
- `top_n` (可选): 返回前N名，默认20

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "date": "20250905",
        "industries": [
            {
                "name": "半导体",
                "rank": 1,
                "change": 4.2,
                "strength_score": 95,
                "amount": 280.5,
                "net_main_inflow": 12.8,
                "advances": 25,
                "declines": 8,
                "leaders": [
                    {"ticker": "688981", "name": "中芯国际", "change": 10.0},
                    {"ticker": "603501", "name": "韦尔股份", "change": 8.5}
                ]
            }
        ]
    }
}
```

#### 获取行业名次变化
**Endpoint**: `GET /api/industry/trend`
**参数**:
- `industry_name`: 行业名称
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "industry": "半导体",
        "trend": {
            "dates": ["20250901", "20250902", "20250903", "20250904", "20250905"],
            "ranks": [3, 2, 2, 1, 1],
            "changes": [2.8, 3.2, 3.8, 4.0, 4.2]
        }
    }
}
```

### 5. 通用接口

#### 获取日期范围
**Endpoint**: `GET /api/dates/range`
**响应格式**:
```json
{
    "code": 200,
    "data": {
        "min_date": "20240101",
        "max_date": "20250905",
        "available_dates": ["20250901", "20250902", "20250903", "20250904", "20250905"]
    }
}
```

#### 搜索接口
**Endpoint**: `GET /api/search`
**参数**:
- `q`: 搜索关键词
- `type` (可选): 搜索类型(stock/theme/industry)

**响应格式**:
```json
{
    "code": 200,
    "data": {
        "stocks": [
            {"ticker": "002230", "name": "科大讯飞", "board_level": 5}
        ],
        "themes": [
            {"name": "人工智能", "heat_score": 85}
        ],
        "industries": [
            {"name": "半导体", "rank": 1}
        ]
    }
}
```

## 🔧 实现优先级

1. **高优先级**: KPI统计条、过滤功能、基础交互
2. **中优先级**: 图表集成、详细面板、排序功能  
3. **低优先级**: 动画效果、高级过滤、数据导出

所有增强功能将在现有UI基础上进行，保持一致的视觉风格和用户体验。
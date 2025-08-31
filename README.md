# 股票市场分析仪表板 - 详细设计文档

## 🎨 整体风格与布局

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

### 1) 连板天梯 (Ladder Board)

#### 结构设计
**A. 多日情绪矩阵 (顶部)**
- 按日期为列，按指标为行
- 指标包含:
  - 连板高度 (当日最高几连板)
  - 一字板数量
  - 首板数量
  - 晋级成功率 (1→2、2→3…)
  - 炸板率、封板率
  - 涨停数、跌停数
  - 昨日涨停表现
  - 今日涨跌停家数
  - 上证/深成/创业板涨跌幅

**B. 连板个股卡片瀑布流 (底部)**
- 按日期分列显示
- 卡片字段:
  - 股票名称、代码
  - 连板数、属性标签 (反包/断板回封/一字/低位/换手等)
  - 涨停时间、首次涨停/回封次数
  - 成交额、换手率、流通市值
  - 所属题材TopN (紫色标签)、所属行业

#### 数据接口
```
GET /api/ladder/heatmap?start=YYYY-MM-DD&end=YYYY-MM-DD&market=ALL
GET /api/ladder/stocks?date=YYYY-MM-DD&min_limitups=1
```

### 2) 大盘情绪热力图 (Market Sentiment)

#### 结构设计
**A. 分层热力带**
- 顶部: 日期刻度 + 情绪灯 (红点/绿点标识强势日/冰点日)
- 中部: 多行热力带指标，色阶深红(差)→深绿(优)

**B. 指数/情绪对比条**
- 底部对照色块显示指数表现

#### 常见指标行
- 首板封板率
- 晋级成功率 (1→2/2→3/3→4…)
- 炸板率
- 涨停家数/跌停家数
- 昨日涨停溢价
- 连板高度
- 涨跌比
- 上涨家数>下跌家数比值

#### 数据接口
```
GET /api/sentiment/heatmap?start=YYYY-MM-DD&end=YYYY-MM-DD
```

### 3) 题材追踪 (Theme Tracking)

#### 结构设计
- **题材榜单网格**: 按日期分列，每列显示热门题材胶囊卡片
- **卡片内容**:
  - 题材名称 (算力、CPO、DRAM、PEEK材料等)
  - 涨跌幅% (红绿显示)
  - 热度值 (0-100)
  - 上榜标识 (首上榜/连板题材/回流等，紫色Badge)
  - 龙头标识 (1-2个龙头股简称)
  - 入选次数/连日上榜数

#### 数据接口
```
GET /api/themes/daily?date=YYYY-MM-DD&top=50
GET /api/themes/detail?name=主题名称&date=YYYY-MM-DD
```

### 4) 行业追踪 (Industry Tracking)

#### 结构设计
- **行业排名卡片**: 按日期分列，排序显示
- **卡片字段**:
  - 行业名称、排名标识
  - 当日涨跌幅
  - 强度评分 (综合涨幅/换手/连板/领涨家数)
  - 成交额、主力净流入
  - 上涨家数/下跌家数
  - 领涨个股 (1-3个，附涨幅)

#### 数据接口
```
GET /api/industries/rank?date=YYYY-MM-DD&limit=20
GET /api/industries/detail?name=行业名称&date=YYYY-MM-DD
```

## 🗃️ 数据模型设计

### 核心数据表

#### 1. market_sentiment_daily
```sql
date, highest_limitup, first_boards, limitups, limitdowns, 
sealed_ratio, break_ratio, p1to2_success, p2to3_success, 
yesterday_limitups_roi, sh_change, sz_change, cyb_change
```

#### 2. limitup_events
```sql
date, ticker, stock_name, board_level(1/2/3…), first_time, 
refill_counts, turnover_rate, amount, mkt_cap_freefloat,
is_one_word, is_recap(反包), themes(数组), industries(数组)
```

#### 3. theme_daily
```sql
date, theme_name, chg_pct, heat_score, is_new, 
streak_days, leaders(数组)
```

#### 4. industry_daily
```sql
date, industry_name, rank, chg_pct, strength_score, 
amount, net_main_inflow, advances, declines, leaders(数组)
```

#### 5. index_daily
```sql
date, sh, sz, cyb, northbound_flow, total_turnover
```

## 📈 可视化技术方案

### PyEcharts 应用
- **热力图**: `HeatMap` + `visualMap` (连板天梯/情绪矩阵)
- **词云图**: `WordCloud` (题材分析)
- **雷达图**: `Radar` (行业强度分析)
- **矩形树图**: `TreeMap` (成分股分布)
- **桑基图**: `Sankey` (题材↔行业↔个股关系)

### Plotly 应用
- **时序图表**: `go.Scatter` + `range slider` (指数/强度/资金)
- **分布散点**: `go.Scatter` (换手率 vs 成交额)
- **K线图**: `go.Candlestick` (个股与行业指数)

### 嵌入方式
```python
# Echarts 嵌入
chart.render_embed()
chart.load_javascript()

# Plotly 嵌入
plotly.offline.plot(fig, include_plotlyjs='cdn', output_type='div')
```

## 🚀 后端架构

### 页面路由
```
/                   # 首页仪表板
/ladder            # 连板天梯
/sentiment         # 大盘情绪热力
/themes            # 题材追踪  
/industries        # 行业追踪
/stock/<ticker>    # 个股详情
```

### API 接口
```
GET /api/ladder/heatmap
GET /api/ladder/stocks
GET /api/sentiment/heatmap
GET /api/themes/daily
GET /api/themes/detail
GET /api/industries/rank
GET /api/industries/detail
```

### 响应格式
```json
{
  "ok": true,
  "data": {...},
  "ts": 1735680000
}
```

## 🧩 前端组件清单

### 核心组件
- **SidebarNav**: 左侧导航 (图标+文字，支持展开/收起)
- **TopBar**: 顶部工具条 (日期选择、市场筛选、搜索)
- **ScrollableColumns**: 日期列容器 (横向滚动，固定列宽)
- **SentimentHeatmap**: 情绪热力图组件
- **ThemeChipsColumn**: 题材胶囊网格
- **IndustryRankCardsColumn**: 行业排名卡片列
- **LimitUpCard**: 连板个股卡片
- **RightDrawer**: 详情侧滑抽屉

### 详情抽屉标签页
- **概览**: 基本信息总览
- **时序**: Plotly 折线图表
- **成分**: 成分股分析
- **关系**: 关联关系图谱
- **新闻**: 相关新闻资讯

## 🎨 设计系统 (Design Tokens)

```css
--bg: #0f1115
--panel: #151922
--text: #e5e7eb
--muted: #9aa3b2
--accent: #ff9f0a
--red: #ef4444
--green: #22c55e
--chip-bg: #1f2430
--badge-purple: #8b5cf6
--badge-cyan: #06b6d4
--grid-border: #262c3a
--hover: rgba(255,255,255,.06)
--shadow: 0 6px 20px rgba(0,0,0,.25)
```

## 📦 技术栈

### 前端技术
- **HTML5/CSS3**: 现代Web标准
- **JavaScript ES6+**: 交互逻辑
- **PyEcharts**: 数据可视化
- **Plotly**: 高级图表
- **响应式设计**: 移动端适配

### 后端技术
- **Python 3.8+**: 主开发语言
- **Flask/FastAPI**: Web框架
- **Pandas**: 数据处理
- **NumPy**: 数值计算

### 开发工具
- **Git**: 版本控制
- **Docker**: 容器化部署
- **Jinja2**: 模板引擎

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js (可选，用于前端构建)
- 现代浏览器支持

### 安装运行
```bash
# 克隆项目
git clone <repository-url>
cd stock-dashboard

# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py

# 访问应用
打开 http://localhost:5000
```

### 开发模式
```bash
# 开启调试模式
export FLASK_DEBUG=1
python main.py

# 自动重新加载
flask run --reload
```

## 📋 开发计划

### Phase 1 - 基础功能 (当前)
- [x] 项目框架搭建
- [x] 基础可视化组件
- [x] 示例数据集成
- [x] 响应式布局

### Phase 2 - 核心功能
- [ ] 实时数据接入
- [ ] 高级图表交互
- [ ] 详情抽屉实现
- [ ] 筛选过滤功能

### Phase 3 - 高级功能
- [ ] 移动端适配
- [ ] 数据持久化
- [ ] 用户偏好设置
- [ ] 性能优化

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 技术支持

- 文档: [项目Wiki](../../wiki)
- 问题: [GitHub Issues](../../issues)
- 讨论: [GitHub Discussions](../../discussions)

---

**注意**: 本项目为股票市场分析工具，不构成投资建议。投资有风险，入市需谨慎。
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 开发命令

### 应用程序运行
```bash
# 使用模拟数据（默认）
python main_enhanced.py

# 使用数据库数据（强制模式）
python main_enhanced.py --database
```

### 测试和验证
```bash
# 运行完整测试套件
python -m pytest test/ -v

# 运行特定测试文件
python -m pytest test/test_database.py -v
python -m pytest test/test_database_logic.py -v

# 运行单元测试（unittest格式）
python test/test_database.py
python test/test_database_logic.py

# 代码质量检查
pylint main_enhanced.py database.py database_config.py
python -m py_compile main_enhanced.py  # 语法检查
```

### 演示脚本
```bash
# 数据库操作演示
python demo/database_demo.py

# akshare数据演示
python demo/akshare_demo.py

# 数据加载器演示
python demo/akshare_data_loader.py
```

### 数据库操作
```bash
# 执行MySQL迁移脚本（需要MySQL服务运行在3309端口）
mysql -u root -p -P 3309 < docs/MYSQL_MIGRATION_SCRIPT.sql

# 测试数据库连接
python -c "from database import StockDatabase; db = StockDatabase(); print('连接成功' if db.connect() else '连接失败')"
```

## 🏗️ 架构概览

### 核心组件
- **main_enhanced.py**: 主应用程序，包含4个功能模块（连板天梯、大盘情绪、题材追踪、行业追踪）
- **database.py**: MySQL CRUD操作，使用PyMySQL连接器，端口3309
- **database_config.py**: 数据库配置、表结构定义和验证规则
- **config.py**: 应用程序配置（颜色主题、数据源设置）

### 数据流架构
1. **数据源层**: akshare API / 模拟数据 → database.py (PyMySQL连接器)
2. **数据处理层**: `_convert_db_data()` 方法处理 PyMySQL Decimal/datetime 类型转换
3. **业务逻辑层**: EnhancedStockDashboard 处理数据并生成HTML模板
4. **展示层**: PyEcharts/Plotly 渲染图表 → 输出到 output/ 目录

### 关键特性
- **强制数据库模式**: main_enhanced.py 第40行强制使用数据库连接
- **数据类型安全**: 自动处理 PyMySQL 的 Decimal/datetime 到 Python 原生类型转换
- **模块化设计**: 4个独立功能模块，支持热切换
- **响应式界面**: 深色主题设计，移动端友好
- **完整CRUD**: MySQL 数据库完整操作接口

## 🔧 技术栈
- **Python 3.8+** with PyEcharts 2.0.3, Plotly 5.18.0, Pandas 2.1.4
- **MySQL** on port 3309 with PyMySQL 1.1.0 connector
- **akshare** for real-time stock data integration
- **HTML5/CSS3/JavaScript** with responsive dark theme
- **Jinja2** 3.1.2 for template rendering

## 📊 数据模型

### 主要数据表结构
- `market_sentiment`: 市场情绪指标（日期、涨停数、封板率等）
- `limitup_events`: 连板个股数据（代码、名称、板数、题材等）
- `theme_daily`: 题材热度数据（题材名称、涨幅、热度评分等）
- `industry_daily`: 行业排名数据（行业名称、排名、资金流入等）

### 数据库配置
- **默认端口**: 3309
- **数据库名**: stock_analysis
- **测试模式**: test_mode=True 使用测试配置
- **连接池**: 支持连接池配置（pool_size=5）

## ⚡ 开发工作流

1. **环境设置**: `pip install -r requirements.txt`
2. **数据库准备**: 确保MySQL运行在3309端口，执行迁移脚本
3. **开发测试**: 使用 `python -m pytest` 运行测试套件
4. **代码质量**: 运行 `pylint` 进行代码规范检查
5. **功能验证**: 使用演示脚本验证数据库和akshare功能

## ⚠️ 注意事项
- **数据库依赖**: 应用程序强制使用数据库模式，必须配置MySQL 3309端口
- **类型转换**: HTML模板渲染前必须调用 `_convert_db_data()` 进行数据类型转换
- **测试模式**: 数据库测试使用 test_mode=True 配置
- **连接管理**: 所有数据库操作包含在 try-catch 块中，确保资源释放
- **敏感信息**: database_config.py 包含数据库密码，切勿提交到版本控制
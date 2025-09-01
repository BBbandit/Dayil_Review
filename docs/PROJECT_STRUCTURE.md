# 项目结构说明

## 📁 新的项目结构

```
stock_analysis/
├── main_enhanced.py          # 主应用程序 - 增强版仪表板
├── main.py                   # 主应用程序 - 基础版
├── database.py               # 数据库操作类
├── database_config.py        # 数据库配置
├── config.py                 # 应用配置
├── requirements.txt          # Python依赖
├── README.md                 # 项目说明文档
├── DATABASE_SETUP.md         # 数据库设置指南
├── AKSHARE_INTEGRATION_SUMMARY.md  # akshare集成总结
├── PROJECT_STRUCTURE.md      # 本项目结构说明
│
├── demo/                     # 演示脚本目录
│   ├── __init__.py
│   ├── database_demo.py      # 数据库CRUD操作演示
│   ├── akshare_demo.py       # akshare数据获取演示
│   └── akshare_data_loader.py # 数据加载到数据库
│
├── test/                     # 测试用例目录
│   ├── __init__.py
│   ├── test_database.py      # 数据库完整测试
│   └── test_database_logic.py # 数据库逻辑测试
│
├── output/                   # 生成的HTML输出
│   ├── stock_dashboard.html
│   └── stock_dashboard_enhanced.html
│
├── templates/                # HTML模板
├── static/                   # 静态资源
│   ├── css/
│   └── js/
└── .gitignore               # Git忽略文件
```

## 🚀 使用说明

### 运行主应用程序
```bash
# 使用模拟数据
python main_enhanced.py

# 使用数据库数据（需要配置MySQL）
python main_enhanced.py --database
```

### 运行演示脚本
```bash
# 数据库操作演示
python demo/database_demo.py

# akshare数据获取演示
python demo/akshare_demo.py

# 数据加载到数据库
python demo/akshare_data_loader.py
```

### 运行测试用例
```bash
# 完整数据库测试（需要MySQL连接）
python test/test_database.py

# 逻辑测试（无需数据库连接）
python test/test_database_logic.py
```

## 🔧 配置说明

### 数据库配置
编辑 `database_config.py` 文件：
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3309,
    'database': 'stock_analysis',
    'user': 'root',
    'password': '123456',  # 修改为你的MySQL密码
    'charset': 'utf8mb4',
    'autocommit': True
}
```

### 安装依赖
```bash
pip install -r requirements.txt
```

## 📊 功能模块

### 核心功能
- **main_enhanced.py**: 完整的4模块仪表板
  - 连板天梯 (Ladder Board)
  - 大盘情绪 (Market Sentiment)
  - 题材追踪 (Theme Tracking)
  - 行业追踪 (Industry Tracking)

### 数据库操作
- **database.py**: 完整的CRUD操作
  - 市场情绪数据管理
  - 连板个股数据管理
  - 题材数据管理
  - 行业数据管理
  - 批量插入功能

### 数据来源
- **akshare集成**: 实时股票数据获取
  - 涨停板数据
  - 概念板块数据
  - 行业板块数据
  - 指数数据

## 🧪 测试覆盖

### 测试类型
1. **单元测试**: 数据库逻辑验证
2. **集成测试**: 数据库连接和操作
3. **功能测试**: 完整业务流程
4. **演示测试**: 数据获取和展示

### 测试命令
```bash
# 运行所有测试
python -m unittest discover test

# 运行特定测试
python -m unittest test.test_database_logic
python -m unittest test.test_database
```

## 🔄 开发工作流

1. **开发新功能**: 在相应模块添加代码
2. **编写测试**: 在test目录添加测试用例
3. **测试验证**: 运行相关测试
4. **演示验证**: 运行演示脚本确认功能
5. **集成测试**: 运行完整应用程序

## 📈 部署说明

### 生产环境
1. 配置生产数据库
2. 设置定时数据获取任务
3. 部署Web服务器（如果需要）
4. 配置监控和日志

### 开发环境
1. 安装Python依赖
2. 配置开发数据库
3. 运行测试套件
4. 使用演示脚本验证

---

此结构使项目更加模块化，便于维护和扩展。
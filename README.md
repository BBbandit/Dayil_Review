# 股票市场分析仪表板

## 📖 文档

所有项目文档已移动到 `docs/` 目录：

- **[详细设计文档](docs/README.md)** - 项目功能设计和架构说明
- **[数据库设置指南](docs/DATABASE_SETUP.md)** - MySQL数据库安装和配置
- **[akshare集成总结](docs/AKSHARE_INTEGRATION_SUMMARY.md)** - 实时数据获取功能说明
- **[项目结构说明](docs/PROJECT_STRUCTURE.md)** - 项目目录结构和文件说明

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用程序
```bash
# 使用模拟数据
python main_enhanced.py

# 使用数据库数据（需要配置MySQL）
python main_enhanced.py --database
```

### 演示和测试
```bash
# 运行演示脚本
python demo/akshare_demo.py
python demo/database_demo.py

# 运行测试用例
python test/test_database_logic.py
```

## 📁 项目结构

```
stock_analysis/
├── main_enhanced.py          # 主应用程序
├── database.py               # 数据库操作类
├── database_config.py        # 数据库配置
├── config.py                 # 应用配置
├── requirements.txt          # Python依赖
├── README.md                 # 本项目说明
├── DEVELOPMENT.md            # 开发指南
│
├── docs/                     # 文档目录
│   ├── README.md             # 详细设计文档
│   ├── DATABASE_SETUP.md     # 数据库设置指南
│   ├── AKSHARE_INTEGRATION_SUMMARY.md  # akshare集成
│   └── PROJECT_STRUCTURE.md  # 项目结构说明
│
├── demo/                     # 演示脚本
│   ├── database_demo.py      # 数据库CRUD演示
│   ├── akshare_demo.py       # akshare数据演示
│   └── akshare_data_loader.py # 数据加载器
│
├── test/                     # 测试用例
│   ├── test_database.py      # 完整数据库测试
│   └── test_database_logic.py # 逻辑测试
│
├── output/                   # 生成的HTML输出
├── templates/                # HTML模板
└── static/                   # 静态资源
```

## 📊 功能特性

- ✅ **4大功能模块**: 连板天梯、大盘情绪、题材追踪、行业追踪
- ✅ **实时数据**: 使用 akshare 获取最新股票数据
- ✅ **数据库支持**: MySQL CRUD 操作和批量插入
- ✅ **响应式设计**: 暗色主题和现代化UI
- ✅ **完整测试**: 单元测试和集成测试覆盖

## 🔧 技术支持

查看 [开发指南](DEVELOPMENT.md) 了解详细开发信息。

---

**注意**: 本项目为股票市场分析工具，不构成投资建议。
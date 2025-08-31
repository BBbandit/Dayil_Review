# MySQL数据库设置指南

## 🐬 数据库配置

### 1. 安装MySQL

#### Windows
1. 下载MySQL Installer: https://dev.mysql.com/downloads/installer/
2. 选择"Server only"安装
3. 配置端口为 `3309`
4. 设置root密码

#### macOS
```bash
# 使用Homebrew安装
brew install mysql

# 启动MySQL服务
brew services start mysql

# 配置端口
sudo vi /usr/local/etc/my.cnf
# 添加: port = 3309
```

#### Linux (Ubuntu)
```bash
# 安装MySQL
sudo apt update
sudo apt install mysql-server

# 修改配置文件
sudo vi /etc/mysql/mysql.conf.d/mysqld.cnf
# 修改: port = 3309

# 重启服务
sudo systemctl restart mysql
```

### 2. 配置数据库连接

编辑 `database_config.py` 文件:

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3309,
    'database': 'stock_analysis',
    'user': 'root',
    'password': 'your_password_here',  # 修改为你的密码
    'charset': 'utf8mb4',
    'autocommit': True
}
```

### 3. 安装Python依赖

```bash
pip install -r requirements.txt
```

## 🚀 快速开始

### 1. 检查数据库连接

```bash
python database_demo.py
```

### 2. 运行测试

```bash
python test_database.py
```

### 3. 使用数据库数据运行应用

```bash
python main_enhanced.py --database
```

## 📊 数据库表结构

### 1. 市场情绪表 (market_sentiment)
```sql
CREATE TABLE market_sentiment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    highest_limitup INT NOT NULL,        -- 最高连板数
    first_boards INT NOT NULL,           -- 首板数量
    limitups INT NOT NULL,               -- 涨停数量
    limitdowns INT NOT NULL,             -- 跌停数量
    sealed_ratio DECIMAL(5,3) NOT NULL,  -- 封板率
    break_ratio DECIMAL(5,3) NOT NULL,   -- 炸板率
    p1to2_success DECIMAL(5,3) NOT NULL, -- 1进2成功率
    p2to3_success DECIMAL(5,3) NOT NULL, -- 2进3成功率
    yesterday_limitups_roi DECIMAL(5,2) NOT NULL, -- 昨日涨停表现
    sh_change DECIMAL(5,2) NOT NULL,     -- 上证涨跌幅
    sz_change DECIMAL(5,2) NOT NULL,     -- 深证涨跌幅
    cyb_change DECIMAL(5,2) NOT NULL,    -- 创业板涨跌幅
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 2. 连板个股表 (limitup_events)
```sql
CREATE TABLE limitup_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    ticker VARCHAR(10) NOT NULL,         -- 股票代码
    stock_name VARCHAR(50) NOT NULL,     -- 股票名称
    board_level INT NOT NULL,            -- 连板数
    first_time VARCHAR(5) NOT NULL,      -- 首次涨停时间
    refill_counts INT NOT NULL,          -- 回封次数
    turnover_rate DECIMAL(5,2) NOT NULL, -- 换手率
    amount BIGINT NOT NULL,              -- 成交额
    mkt_cap_freefloat BIGINT NOT NULL,   -- 流通市值
    is_one_word BOOLEAN DEFAULT FALSE,   -- 是否一字板
    is_recap BOOLEAN DEFAULT FALSE,      -- 是否反包
    themes JSON NOT NULL,                -- 题材标签
    industries JSON NOT NULL,            -- 行业标签
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_ticker (ticker),
    INDEX idx_stock_name (stock_name)
);
```

### 3. 题材表 (theme_daily)
```sql
CREATE TABLE theme_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    theme_name VARCHAR(50) NOT NULL,     -- 题材名称
    chg_pct DECIMAL(5,2) NOT NULL,       -- 涨跌幅
    heat_score INT NOT NULL,             -- 热度评分
    is_new BOOLEAN DEFAULT FALSE,        -- 是否新题材
    streak_days INT NOT NULL,            -- 连续上榜天数
    leaders JSON NOT NULL,               -- 龙头个股
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_theme_date (date, theme_name),
    INDEX idx_date (date),
    INDEX idx_theme_name (theme_name)
);
```

### 4. 行业表 (industry_daily)
```sql
CREATE TABLE industry_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    industry_name VARCHAR(50) NOT NULL,  -- 行业名称
    rank INT NOT NULL,                   -- 排名
    chg_pct DECIMAL(5,2) NOT NULL,       -- 涨跌幅
    strength_score INT NOT NULL,         -- 强度评分
    amount BIGINT NOT NULL,              -- 成交额
    net_main_inflow BIGINT NOT NULL,     -- 主力净流入
    advances INT NOT NULL,               -- 上涨家数
    declines INT NOT NULL,               -- 下跌家数
    leaders JSON NOT NULL,               -- 领涨个股
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_industry_date (date, industry_name),
    INDEX idx_date (date),
    INDEX idx_industry_name (industry_name)
);
```

## 🔧 CRUD操作接口

### 1. 市场情绪数据操作
```python
# 创建数据
db.create_market_sentiment(data)

# 读取数据
db.get_market_sentiment(date=None)

# 更新数据
db.update_market_sentiment(date, data)

# 删除数据
db.delete_market_sentiment(date)
```

### 2. 连板个股数据操作
```python
# 创建数据
db.create_limitup_event(data)

# 读取数据
db.get_limitup_events(date=None, ticker=None)

# 更新数据
db.update_limitup_event(event_id, data)

# 删除数据
db.delete_limitup_event(event_id)
```

### 3. 批量操作
```python
# 批量插入数据
success_count = db.batch_insert_data(data_type, data_list)
```

## 🧪 测试数据

### 生成测试数据
```bash
python database_demo.py
```

### 运行单元测试
```bash
python test_database.py
```

## 🔍 常见问题

### 1. 连接失败
- 检查MySQL服务是否运行
- 确认端口3309是否开放
- 验证用户名密码是否正确

### 2. 表不存在
- 运行 `database_demo.py` 自动创建表
- 或手动执行SQL创建表

### 3. 性能优化
- 为常用查询字段创建索引
- 使用连接池管理连接
- 批量操作减少数据库交互

## 📈 性能监控

### 查看数据库状态
```sql
-- 查看连接数
SHOW STATUS LIKE 'Threads_connected';

-- 查看查询缓存
SHOW STATUS LIKE 'Qcache%';

-- 查看表大小
SELECT 
    table_name AS `Table`, 
    round(((data_length + index_length) / 1024 / 1024), 2) `Size in MB` 
FROM information_schema.TABLES 
WHERE table_schema = 'stock_analysis'
ORDER BY (data_length + index_length) DESC;
```

## 🔒 安全建议

1. **不要使用root用户**：创建专用数据库用户
2. **限制访问IP**：只允许应用服务器访问
3. **定期备份**：设置自动备份策略
4. **监控日志**：关注慢查询和错误日志
5. **使用连接池**：避免频繁创建连接

## 📚 相关资源

- [MySQL官方文档](https://dev.mysql.com/doc/)
- [Python MySQL Connector](https://dev.mysql.com/doc/connector-python/en/)
- [数据库设计最佳实践](https://www.databasestar.com/database-design-best-practices/)
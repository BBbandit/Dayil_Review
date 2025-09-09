# MySQL 数据库配置与操作指南

## 🗄️ 数据库配置

### 连接配置
```python
# database_config.py
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3309,  # 指定端口3309
    'database': 'stock_analysis',
    'user': 'root',
    'password': '123456',  # 请根据实际情况修改
    'charset': 'utf8mb4',
    'autocommit': True
}

# 测试数据库配置
TEST_DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3309,
    'database': 'stock_analysis',
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4',
    'autocommit': True
}
```

### 连接池配置
```python
POOL_CONFIG = {
    'pool_name': 'stock_pool',
    'pool_size': 5,
    'pool_reset_session': True
}
```

## 📊 数据表结构

### 1. 市场情绪表 (market_sentiment)
```sql
CREATE TABLE market_sentiment (
    date DATE PRIMARY KEY,
    highest_limitup INT,
    first_boards INT,
    limitups INT,
    limitdowns INT,
    sealed_ratio DECIMAL(5,4),
    break_ratio DECIMAL(5,4),
    p1to2_success DECIMAL(5,4),
    p2to3_success DECIMAL(5,4),
    yesterday_limitups_roi DECIMAL(6,3),
    sh_change DECIMAL(6,3),
    sz_change DECIMAL(6,3),
    cyb_change DECIMAL(6,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**字段说明**:
- `date`: 交易日期 (主键)
- `highest_limitup`: 最高连板数
- `first_boards`: 首板数量
- `limitups`: 涨停数量
- `limitdowns`: 跌停数量
- `sealed_ratio`: 封板率
- `break_ratio`: 破板率
- `p1to2_success`: 1进2成功率
- `p2to3_success`: 2进3成功率
- `yesterday_limitups_roi`: 昨日涨停今日收益率

### 2. 连板事件表 (limitup_events)
```sql
CREATE TABLE limitup_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    stock_name VARCHAR(50) NOT NULL,
    board_level INT,
    first_time TIME,
    refill_counts INT,
    turnover_rate DECIMAL(6,3),
    amount DECIMAL(15,2),
    mkt_cap_freefloat DECIMAL(15,2),
    is_one_word BOOLEAN,
    is_recap BOOLEAN,
    themes TEXT,
    industries TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_ticker (ticker),
    INDEX idx_board_level (board_level),
    INDEX idx_stock_name (stock_name)
);
```

### 3. 题材热度表 (theme_daily)
```sql
CREATE TABLE theme_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    theme_name VARCHAR(50) NOT NULL,
    chg_pct DECIMAL(6,3),
    heat_score INT,
    is_new BOOLEAN,
    streak_days INT,
    leaders TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date_theme (date, theme_name),
    INDEX idx_date (date),
    INDEX idx_theme_name (theme_name),
    INDEX idx_heat_score (heat_score)
);
```

### 4. 行业排名表 (industry_daily)
```sql
CREATE TABLE industry_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    industry_name VARCHAR(50) NOT NULL,
    rank INT,
    chg_pct DECIMAL(6,3),
    strength_score INT,
    amount DECIMAL(15,2),
    net_main_inflow DECIMAL(15,2),
    advances INT,
    declines INT,
    leaders TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date_industry (date, industry_name),
    INDEX idx_date (date),
    INDEX idx_industry_name (industry_name),
    INDEX idx_rank (rank)
);
```

## 🔍 数据验证规则

### 市场情绪表验证
```python
VALIDATION_RULES = {
    'market_sentiment': {
        'sealed_ratio': {'min': 0, 'max': 1},
        'break_ratio': {'min': 0, 'max': 1},
        'p1to2_success': {'min': 0, 'max': 1},
        'p2to3_success': {'min': 0, 'max': 1}
    },
    'limitup_events': {
        'board_level': {'min': 1, 'max': 10},
        'turnover_rate': {'min': 0, 'max': 100}
    }
}
```

## ⚙️ 数据库操作接口

### CRUD 操作示例

#### 插入数据
```python
def insert_market_sentiment(self, data):
    """插入市场情绪数据"""
    sql = """
    INSERT INTO market_sentiment 
    (date, highest_limitup, first_boards, limitups, limitdowns, 
     sealed_ratio, break_ratio, p1to2_success, p2to3_success,
     yesterday_limitups_roi, sh_change, sz_change, cyb_change)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        highest_limitup = VALUES(highest_limitup),
        first_boards = VALUES(first_boards),
        limitups = VALUES(limitups),
        limitdowns = VALUES(limitdowns),
        sealed_ratio = VALUES(sealed_ratio),
        break_ratio = VALUES(break_ratio),
        p1to2_success = VALUES(p1to2_success),
        p2to3_success = VALUES(p2to3_success),
        yesterday_limitups_roi = VALUES(yesterday_limitups_roi),
        sh_change = VALUES(sh_change),
        sz_change = VALUES(sz_change),
        cyb_change = VALUES(cyb_change)
    """
    self.execute(sql, data)
```

#### 查询数据
```python
def get_market_sentiment(self, start_date, end_date):
    """获取时间段内的市场情绪数据"""
    sql = """
    SELECT * FROM market_sentiment 
    WHERE date BETWEEN %s AND %s 
    ORDER BY date DESC
    """
    return self.query(sql, (start_date, end_date))
```

#### 批量插入
```python
def batch_insert_limitup_events(self, data_list):
    """批量插入连板事件数据"""
    sql = """
    INSERT INTO limitup_events 
    (date, ticker, stock_name, board_level, first_time, refill_counts,
     turnover_rate, amount, mkt_cap_freefloat, is_one_word, is_recap,
     themes, industries)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    self.executemany(sql, data_list)
```

## 🚀 数据库迁移

### 迁移脚本执行
```bash
# 执行MySQL迁移脚本（需要先启动MySQL服务）
mysql -u root -p -P 3309 < docs/MYSQL_MIGRATION_SCRIPT.sql
```

### 迁移脚本内容
主要的迁移操作包括：
1. 创建数据库 `stock_analysis`
2. 创建所有数据表
3. 创建必要的索引
4. 插入初始测试数据
5. 设置字符集和排序规则

## 🔧 连接管理

### 连接建立
```python
def connect(self):
    """建立数据库连接"""
    try:
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            charset='utf8mb4',
            autocommit=True
        )
        if self.connection.open:
            print(f"成功连接到MySQL数据库 (端口: {self.port})")
            return True
    except Error as e:
        print(f"数据库连接错误: {e}")
        return False
```

### 连接断开
```python
def disconnect(self):
    """断开数据库连接"""
    if self.connection and self.connection.open:
        self.connection.close()
        print("数据库连接已关闭")
```

## 📊 数据类型处理

### Python 类型转换
由于 PyMySQL 返回 Decimal 和 datetime 类型，需要进行转换：

```python
def _convert_db_data(self, data):
    """转换数据库返回的数据类型"""
    if isinstance(data, dict):
        return {k: self._convert_value(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [self._convert_db_data(item) for item in data]
    return data

def _convert_value(self, value):
    """转换单个值"""
    if isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    elif isinstance(value, date):
        return value.strftime('%Y-%m-%d')
    return value
```

## ⚠️ 注意事项

1. **端口配置**: 确保 MySQL 服务运行在 3309 端口
2. **字符集**: 使用 utf8mb4 支持中文和特殊字符
3. **时区设置**: 确保数据库和服务器的时区一致
4. **连接池**: 生产环境建议使用连接池管理连接
5. **错误处理**: 所有数据库操作应包含在 try-catch 块中
6. **资源释放**: 使用完毕后及时关闭连接和游标

## 🧪 测试模式

测试时使用 `test_mode=True` 参数：
```python
db = StockDatabase(test_mode=True)
```

这将使用测试数据库配置，避免影响生产数据。
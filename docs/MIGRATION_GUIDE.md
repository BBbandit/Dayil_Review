# MySQL 表结构规范化迁移指南

## 🎯 迁移目标

将从 akshare 获取的数据规范化存储到 MySQL 中，确保数据格式符合网页展示需求。

## 📋 迁移内容

### 1. 表结构优化
- 规范数据类型（TINYINT, SMALLINT, DECIMAL等）
- 添加时间戳字段（created_at, updated_at）
- 优化索引配置
- 添加字段注释

### 2. 数据规范化
- 数值类型精度统一
- JSON字段格式标准化
- 字段命名规范化

## 🚀 迁移步骤

### 步骤1: 备份现有数据
```bash
# 连接到MySQL
mysql -u root -p -P 3309

# 执行备份
USE stock_analysis;
SOURCE docs/MYSQL_MIGRATION_SCRIPT.sql;
```

### 步骤2: 执行迁移脚本
```sql
-- 在MySQL中执行迁移脚本
SOURCE docs/MYSQL_MIGRATION_SCRIPT.sql;
```

### 步骤3: 验证迁移结果
```sql
-- 验证表结构
SHOW CREATE TABLE market_sentiment;
SHOW CREATE TABLE limitup_events;

-- 验证数据完整性
SELECT COUNT(*) FROM market_sentiment;
SELECT COUNT(*) FROM limitup_events;

-- 验证索引
SHOW INDEX FROM market_sentiment;
SHOW INDEX FROM limitup_events;
```

### 步骤4: 更新应用程序
```bash
# 确保应用程序使用新的字段格式
# 主要检查 database.py 中的数据处理逻辑
```

## 📊 迁移前后对比

### 迁移前问题
- 数据类型不统一
- 缺少时间戳字段
- 索引配置不完整
- 字段注释缺失

### 迁移后改进
- ✅ 数据类型规范化
- ✅ 添加创建/更新时间戳
- ✅ 优化查询性能索引
- ✅ 完整的字段注释
- ✅ 更好的数据完整性

## ⚠️ 注意事项

1. **备份重要**: 迁移前务必备份数据
2. **测试环境**: 先在测试环境验证迁移脚本
3. **应用程序兼容**: 确保应用程序适配新的表结构
4. **数据验证**: 迁移后验证数据完整性和一致性

## 🔧 故障排除

### 常见问题
1. **数据类型转换错误**: 检查数据是否符合新的数据类型要求
2. **唯一约束冲突**: 检查是否有重复数据
3. **索引创建失败**: 检查索引名称是否冲突

### 解决方案
- 查看 MySQL 错误日志
- 使用 `SHOW WARNINGS;` 查看详细错误信息
- 逐步执行迁移脚本，分步验证

## 📞 支持

如遇迁移问题，请参考：
- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [表结构规范文档](MYSQL_TABLE_STRUCTURE.md)
- [迁移脚本说明](MYSQL_MIGRATION_SCRIPT.sql)
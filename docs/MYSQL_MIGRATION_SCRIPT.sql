-- MySQL 表结构规范化迁移脚本
-- 执行顺序：1. 备份数据 → 2. 修改表结构 → 3. 恢复数据

-- ==================== 备份现有数据 ====================
CREATE TABLE market_sentiment_backup AS SELECT * FROM market_sentiment;
CREATE TABLE limitup_events_backup AS SELECT * FROM limitup_events;
CREATE TABLE theme_daily_backup AS SELECT * FROM theme_daily;
CREATE TABLE industry_daily_backup AS SELECT * FROM industry_daily;

-- ==================== 修改表结构 ====================

-- 1. 市场情绪表结构调整
ALTER TABLE market_sentiment 
MODIFY COLUMN highest_limitup TINYINT NOT NULL COMMENT '最高连板数',
MODIFY COLUMN first_boards SMALLINT NOT NULL COMMENT '首板数量',
MODIFY COLUMN limitups SMALLINT NOT NULL COMMENT '涨停总数',
MODIFY COLUMN limitdowns SMALLINT NOT NULL COMMENT '跌停总数',
MODIFY COLUMN sealed_ratio DECIMAL(5,3) NOT NULL COMMENT '封板率',
MODIFY COLUMN break_ratio DECIMAL(5,3) NOT NULL COMMENT '炸板率',
MODIFY COLUMN p1to2_success DECIMAL(5,3) NOT NULL COMMENT '1进2成功率',
MODIFY COLUMN p2to3_success DECIMAL(5,3) NOT NULL COMMENT '2进3成功率',
MODIFY COLUMN yesterday_limitups_roi DECIMAL(5,2) NOT NULL COMMENT '昨日涨停表现',
MODIFY COLUMN sh_change DECIMAL(5,2) NOT NULL COMMENT '上证涨跌幅(%)',
MODIFY COLUMN sz_change DECIMAL(5,2) NOT NULL COMMENT '深证涨跌幅(%)',
MODIFY COLUMN cyb_change DECIMAL(5,2) NOT NULL COMMENT '创业板涨跌幅(%)',
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
ADD UNIQUE INDEX uk_date (date);

-- 2. 连板个股表结构调整
ALTER TABLE limitup_events 
MODIFY COLUMN board_level TINYINT NOT NULL COMMENT '连板数',
MODIFY COLUMN refill_counts TINYINT NOT NULL DEFAULT 0 COMMENT '回封次数',
MODIFY COLUMN turnover_rate DECIMAL(5,2) NOT NULL COMMENT '换手率(%)',
MODIFY COLUMN amount BIGINT NOT NULL COMMENT '成交额(元)',
MODIFY COLUMN mkt_cap_freefloat BIGINT NOT NULL COMMENT '流通市值(元)',
MODIFY COLUMN is_one_word BOOLEAN DEFAULT FALSE COMMENT '是否一字板',
MODIFY COLUMN is_recap BOOLEAN DEFAULT FALSE COMMENT '是否反包',
MODIFY COLUMN themes JSON NOT NULL COMMENT '题材概念',
MODIFY COLUMN industries JSON NOT NULL COMMENT '所属行业',
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
ADD UNIQUE INDEX uk_date_ticker (date, ticker),
ADD INDEX idx_board_level (board_level);

-- 3. 题材日报表结构调整
ALTER TABLE theme_daily 
MODIFY COLUMN chg_pct DECIMAL(5,2) NOT NULL COMMENT '涨跌幅(%)',
MODIFY COLUMN heat_score TINYINT NOT NULL COMMENT '热度评分',
MODIFY COLUMN is_new BOOLEAN DEFAULT FALSE COMMENT '是否新题材',
MODIFY COLUMN streak_days TINYINT NOT NULL COMMENT '连续上榜天数',
MODIFY COLUMN leaders JSON NOT NULL COMMENT '龙头个股',
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
ADD INDEX idx_heat_score (heat_score);

-- 4. 行业日报表结构调整
ALTER TABLE industry_daily 
MODIFY COLUMN `rank` TINYINT NOT NULL COMMENT '排名',
MODIFY COLUMN chg_pct DECIMAL(5,2) NOT NULL COMMENT '涨跌幅(%)',
MODIFY COLUMN strength_score TINYINT NOT NULL COMMENT '强度评分',
MODIFY COLUMN amount BIGINT NOT NULL COMMENT '成交额(元)',
MODIFY COLUMN net_main_inflow BIGINT NOT NULL COMMENT '主力净流入(元)',
MODIFY COLUMN advances SMALLINT NOT NULL COMMENT '上涨家数',
MODIFY COLUMN declines SMALLINT NOT NULL COMMENT '下跌家数',
MODIFY COLUMN leaders JSON NOT NULL COMMENT '领涨个股',
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
ADD INDEX idx_rank (`rank`);

-- ==================== 恢复数据 ====================
-- 注意：需要根据新的表结构调整数据插入语句

-- 插入市场情绪数据
INSERT INTO market_sentiment (
    date, highest_limitup, first_boards, limitups, limitdowns,
    sealed_ratio, break_ratio, p1to2_success, p2to3_success,
    yesterday_limitups_roi, sh_change, sz_change, cyb_change
)
SELECT 
    date, highest_limitup, first_boards, limitups, limitdowns,
    sealed_ratio, break_ratio, p1to2_success, p2to3_success,
    yesterday_limitups_roi, sh_change, sz_change, cyb_change
FROM market_sentiment_backup;

-- 插入连板个股数据
INSERT INTO limitup_events (
    date, ticker, stock_name, board_level, first_time, refill_counts,
    turnover_rate, amount, mkt_cap_freefloat, is_one_word, is_recap,
    themes, industries
)
SELECT 
    date, ticker, stock_name, board_level, first_time, refill_counts,
    turnover_rate, amount, mkt_cap_freefloat, is_one_word, is_recap,
    themes, industries
FROM limitup_events_backup;

-- 插入题材数据
INSERT INTO theme_daily (
    date, theme_name, chg_pct, heat_score, is_new, streak_days, leaders
)
SELECT 
    date, theme_name, chg_pct, heat_score, is_new, streak_days, leaders
FROM theme_daily_backup;

-- 插入行业数据
INSERT INTO industry_daily (
    date, industry_name, `rank`, chg_pct, strength_score, amount,
    net_main_inflow, advances, declines, leaders
)
SELECT 
    date, industry_name, `rank`, chg_pct, strength_score, amount,
    net_main_inflow, advances, declines, leaders
FROM industry_daily_backup;

-- ==================== 清理备份 ====================
-- 确认数据迁移成功后执行
-- DROP TABLE market_sentiment_backup;
-- DROP TABLE limitup_events_backup;
-- DROP TABLE theme_daily_backup;
-- DROP TABLE industry_daily_backup;

-- ==================== 验证脚本 ====================
-- 验证表结构
SHOW CREATE TABLE market_sentiment;
SHOW CREATE TABLE limitup_events;
SHOW CREATE TABLE theme_daily;
SHOW CREATE TABLE industry_daily;

-- 验证数据完整性
SELECT COUNT(*) FROM market_sentiment;
SELECT COUNT(*) FROM limitup_events;
SELECT COUNT(*) FROM theme_daily;
SELECT COUNT(*) FROM industry_daily;

-- 验证索引
SHOW INDEX FROM market_sentiment;
SHOW INDEX FROM limitup_events;
SHOW INDEX FROM theme_daily;
SHOW INDEX FROM industry_daily;
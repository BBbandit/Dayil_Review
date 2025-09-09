# 批处理脚本管理

## 文件说明

### 1. update_database.bat
**基础数据库更新脚本**
- 功能: 执行涨停数据同步
- 同步天数: 最近5天数据
- 日志: 控制台输出

### 2. update_database_advanced.bat  
**高级数据库更新脚本**
- 功能: 执行涨停数据同步（带详细日志）
- 同步天数: 最近5天数据
- 日志: 自动保存到 logs/ 目录，按日期时间命名
- 错误处理: 完善的错误检测和状态报告

### 3. test_batch.bat
**环境测试脚本**
- 功能: 测试Python环境和数据库连接
- 用途: 验证批处理环境是否正常

## 使用方法

### 手动运行
1. 双击任意 `.bat` 文件即可运行
2. 高级版本会自动创建日志文件

### Windows计划任务设置

#### 方法一: 使用任务计划程序（GUI）
1. 打开"任务计划程序"
2. 创建基本任务
3. 名称: "股票数据库自动更新"
4. 触发器: 每天 15:30 (收盘后)
5. 操作: "启动程序"
6. 程序/脚本: `E:\Shares\dayil_review\batch_management\update_database_advanced.bat`
7. 起始于: `E:\Shares\dayil_review\batch_management`

#### 方法二: 使用命令行创建计划任务
```cmd
schtasks /create /tn "股票数据库更新" /tr "E:\Shares\dayil_review\batch_management\update_database_advanced.bat" /sc daily /st 15:30 /ru System
```

#### 方法三: 使用PowerShell创建计划任务
```powershell
$action = New-ScheduledTaskAction -Execute 'E:\Shares\dayil_review\batch_management\update_database_advanced.bat'
$trigger = New-ScheduledTaskTrigger -Daily -At '15:30'
Register-ScheduledTask -TaskName '股票数据库更新' -Action $action -Trigger $trigger -Description '自动更新股票数据库数据'
```

## 计划任务推荐设置

### 更新时间安排
- **周一至周五**: 15:30 (收盘后立即更新)
- **周末**: 不需要更新

### 执行账户
- 推荐使用 `SYSTEM` 账户运行，避免权限问题
- 或者使用有足够权限的用户账户

### 错误处理
- 脚本会自动检测执行状态
- 失败时会生成错误日志
- 可以通过Windows事件查看器监控任务执行情况

## 日志查看

### 高级版本日志位置
```
batch_management/logs/
├── update_20250909_1530.log  # 按日期时间命名
├── update_20250910_1530.log
└── ...
```

### 日志内容包含
- 开始和结束时间
- Python环境信息
- 同步详细结果
- 错误信息（如果有）

## 环境要求

- Python环境: `D:\Anaconda\Anaconda\envs\qmt_env\python.exe`
- 数据库: MySQL运行在3309端口
- 网络: 需要互联网连接访问akshare数据

## 故障排除

1. **Python环境问题**: 运行 `test_batch.bat` 测试环境
2. **数据库连接问题**: 检查MySQL服务是否运行
3. **网络问题**: 检查是否能访问akshare API
4. **权限问题**: 确保执行账户有足够权限

## 注意事项

- 确保MySQL服务在计划任务时间点正在运行
- 如果akshare API访问受限，可能需要配置代理
- 定期清理日志文件，避免占用过多磁盘空间
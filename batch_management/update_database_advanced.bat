@echo off
echo ========================================
echo   股票数据库高级更新批处理脚本
echo ========================================
echo.

REM 设置路径
set PYTHON_PATH=D:\Anaconda\Anaconda\envs\qmt_env\python.exe
set PROJECT_DIR=%~dp0..
set LOG_DIR=%~dp0logs
set LOG_FILE=%LOG_DIR%\update_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%.log

REM 创建日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 切换到项目目录
cd /d "%PROJECT_DIR%"

REM 记录开始时间
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "datetime=%%a"
set START_TIME=%datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%

echo [%date% %time%] 开始执行数据库更新... > "%LOG_FILE%"
echo Python解释器: %PYTHON_PATH% >> "%LOG_FILE%"
echo 项目目录: %PROJECT_DIR% >> "%LOG_FILE%"
echo.

echo 正在同步涨停数据...
echo 正在同步涨停数据... >> "%LOG_FILE%"

REM 执行数据同步并记录输出
"%PYTHON_PATH%" -c "
from data_access_layer.limitup_sync_api import sync_limitup_data
import sys

try:
    print('开始同步最近5天涨停数据...')
    result = sync_limitup_data(5)
    print(f'同步完成: {result}')
    
    if result.get('status') == 'success':
        print('✅ 数据同步成功')
        sys.exit(0)
    else:
        print(f'❌ 数据同步失败: {result}')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ 同步过程中发生错误: {e}')
    sys.exit(1)
" >> "%LOG_FILE%" 2>&1

REM 检查执行结果
if %errorlevel% equ 0 (
    echo ✅ 数据库更新成功完成 >> "%LOG_FILE%"
    echo.
    echo ✅ 数据库更新成功完成
    echo 详细日志请查看: %LOG_FILE%
) else (
    echo ❌ 数据库更新失败 >> "%LOG_FILE%"
    echo.
    echo ❌ 数据库更新失败
    echo 错误详情请查看: %LOG_FILE%
)

REM 记录结束时间
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "datetime=%%a"
set END_TIME=%datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%

echo [%date% %time%] 脚本执行完毕 >> "%LOG_FILE%"
echo 开始时间: %START_TIME% >> "%LOG_FILE%"
echo 结束时间: %END_TIME% >> "%LOG_FILE%"

echo.
echo 开始时间: %START_TIME%
echo 结束时间: %END_TIME%
echo.

pause
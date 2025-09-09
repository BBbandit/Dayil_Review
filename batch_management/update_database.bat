@echo off
echo ========================================
echo   股票数据库更新批处理脚本
echo ========================================
echo.

REM 设置Python解释器路径
set PYTHON_PATH=D:\Anaconda\Anaconda\envs\qmt_env\python.exe

REM 设置项目根目录
set PROJECT_DIR=%~dp0..

REM 切换到项目目录
cd /d "%PROJECT_DIR%"

echo [%date% %time%] 开始执行数据库更新...
echo Python解释器: %PYTHON_PATH%
echo 项目目录: %PROJECT_DIR%
echo.

REM 执行数据同步
echo 正在同步涨停数据...
"%PYTHON_PATH%" -c "from data_access_layer.limitup_sync_api import sync_limitup_data; result = sync_limitup_data(5); print(f'同步结果: {result}')"

REM 检查同步结果
if %errorlevel% neq 0 (
    echo ❌ 数据同步失败
    exit /b 1
)

echo.
echo ✅ 数据库更新完成
echo [%date% %time%] 脚本执行完毕
echo.

pause
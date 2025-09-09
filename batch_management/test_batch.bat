@echo off
echo ========================================
echo   批处理脚本测试
echo ========================================
echo.

set PYTHON_PATH=D:\Anaconda\Anaconda\envs\qmt_env\python.exe
set PROJECT_DIR=%~dp0..

cd /d "%PROJECT_DIR%"

echo 测试Python环境...
"%PYTHON_PATH%" --version

if %errorlevel% neq 0 (
    echo ❌ Python环境测试失败
    pause
    exit /b 1
)

echo.
echo 测试数据库连接...
"%PYTHON_PATH%" -c "from database import StockDatabase; db = StockDatabase(); print('连接成功' if db.connect() else '连接失败'); db.close()"

echo.
echo ✅ 环境测试完成
echo.

pause
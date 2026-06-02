@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动标准通爬虫...
echo.

:: 检查 Python 版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 检查依赖
echo 检查依赖...
pip install -q -r requirements.txt 2>nul

:: 启动应用
echo 启动 Web 界面...
echo 浏览器将自动打开，如果没有请手动访问 http://localhost:8501
echo.
streamlit run app.py --server.headless true
pause

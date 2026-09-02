@echo off
chcp 65001 >nul
title MOD Forge V0.1.0
cd /d "%~dp0.."

echo ============================================
echo   MOD Forge V0.1.0 预览版
echo ============================================
echo.

REM 检查 Python
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+ 并加入 PATH。
    echo 下载: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖（缺失时自动安装）
python -c "import fastapi, uvicorn, openai, dotenv, httpx, yaml, PIL" >nul 2>nul
if errorlevel 1 (
    echo [提示] 首次运行，正在安装依赖（约 1-2 分钟）...
    pip install -r requirements.txt -q
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络后重试。
        pause
        exit /b 1
    )
)

echo [启动] 服务运行中，浏览器打开 http://127.0.0.1:8000
echo [停止] 直接关闭本窗口或按 Ctrl+C
echo.
start "" http://127.0.0.1:8000
python server_app\server.py
pause

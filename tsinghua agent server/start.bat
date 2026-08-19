@echo off
REM 启动清小搭接入服务
REM 用法：双击，或在命令行执行 start.bat
cd /d "%~dp0"
if exist ..\venv\Scripts\python.exe (
    ..\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001
) else (
    python -m uvicorn main:app --host 0.0.0.0 --port 8001
)
pause
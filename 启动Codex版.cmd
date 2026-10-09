@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PYTHON_EXE="

rem 1. Codex 自带 Python
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" set "PYTHON_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

rem 2. 系统 Python
if not defined PYTHON_EXE (
  where python >nul 2>nul && set "PYTHON_EXE=python"
)
if not defined PYTHON_EXE (
  where py >nul 2>nul && set "PYTHON_EXE=py"
)

if not defined PYTHON_EXE (
  echo [错误] 未找到 Python。请安装 Python 3.10+ 并勾选 "Add to PATH"，或先启动一次 Codex。
  pause
  exit /b 1
)

echo 使用 Python: %PYTHON_EXE%
"%PYTHON_EXE%" "scripts\start_local.py" %*
if errorlevel 1 pause
endlocal

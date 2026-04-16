@echo off
REM Simulink MCP Server Startup Script
REM This script ensures MATLAB shared engine is running and starts the MCP server

cd /d "%~dp0"

echo ========================================
echo Simulink MCP Server
echo ========================================
echo.

REM Check if MATLAB is running
tasklist /FI "IMAGENAME eq MATLAB.exe" 2>NUL | find /I /N "MATLAB.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] MATLAB is running
) else (
    echo [WARNING] MATLAB is not running
    echo Please start MATLAB and run: matlab.engine.shareEngine('SimulinkMCP'^)
    echo.
    pause
    exit /b 1
)

REM Set environment variables (allow overrides)
if "%MATLAB_PATH%"=="" set MATLAB_PATH=C:\Program Files\MATLAB\R2025a
if "%SIMULINK_MCP_LOG_LEVEL%"=="" set SIMULINK_MCP_LOG_LEVEL=WARNING

echo [OK] Environment configured
echo   MATLAB_PATH=%MATLAB_PATH%
echo   SIMULINK_MCP_LOG_LEVEL=%SIMULINK_MCP_LOG_LEVEL%
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start MCP server
echo Starting MCP server...
echo.
python -m simulink_mcp_server.mcp_server

echo.
echo MCP server stopped.
pause
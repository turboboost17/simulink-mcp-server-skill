@echo off
REM Start MATLAB with Shared Engine
REM This script launches MATLAB and creates the shared engine named 'SimulinkMCP'

echo ========================================
echo Starting MATLAB with Shared Engine
echo ========================================
echo.

set MATLAB_PATH=C:\Program Files\MATLAB\R2025a
set MATLAB_EXE=%MATLAB_PATH%\bin\matlab.exe

if not exist "%MATLAB_EXE%" (
    echo [ERROR] MATLAB not found at: %MATLAB_EXE%
    echo Please update MATLAB_PATH in this script
    pause
    exit /b 1
)

echo Starting MATLAB...
echo.
echo MATLAB will start and create a shared engine named 'SimulinkMCP'
echo Keep MATLAB running while using the MCP server
echo.

REM Start MATLAB with command to create shared engine
start "MATLAB - SimulinkMCP" "%MATLAB_EXE%" -r "matlab.engine.shareEngine('SimulinkMCP'); disp('Shared engine SimulinkMCP started successfully');"

echo.
echo [OK] MATLAB started
echo.
echo The shared engine 'SimulinkMCP' should now be available
echo You can now start the MCP server with: start_mcp_server.bat
echo.
pause

# Simulink MCP Server Startup Script
# This script ensures MATLAB shared engine is running and starts the MCP server

$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Simulink MCP Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if MATLAB is running
$matlabProcess = Get-Process -Name "MATLAB" -ErrorAction SilentlyContinue

if ($matlabProcess) {
    Write-Host "[OK] MATLAB is running" -ForegroundColor Green
} else {
    Write-Host "[WARNING] MATLAB is not running" -ForegroundColor Yellow
    Write-Host "Please start MATLAB and run: matlab.engine.shareEngine('SimulinkMCP')" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Set environment variables (allow overrides)
if (-not $env:MATLAB_PATH) {
    $env:MATLAB_PATH = "C:\Program Files\MATLAB\R2025a"
}
if (-not $env:SIMULINK_MCP_LOG_LEVEL) {
    $env:SIMULINK_MCP_LOG_LEVEL = "WARNING"
}
if (-not $env:SIMULINK_MCP_MODE) {
    $env:SIMULINK_MCP_MODE = "full"
}

Write-Host "[OK] Environment configured" -ForegroundColor Green
Write-Host "  MATLAB_PATH=$env:MATLAB_PATH" -ForegroundColor Gray
Write-Host "  SIMULINK_MCP_LOG_LEVEL=$env:SIMULINK_MCP_LOG_LEVEL" -ForegroundColor Gray
Write-Host "  SIMULINK_MCP_MODE=$env:SIMULINK_MCP_MODE" -ForegroundColor Gray
Write-Host ""

# Activate virtual environment and start server
Write-Host "Starting MCP server..." -ForegroundColor Yellow
Write-Host ""

try {
    & .\.venv\Scripts\Activate.ps1
    python -m simulink_mcp_server.mcp_server
} catch {
    Write-Host ""
    Write-Host "Error starting MCP server: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "MCP server stopped." -ForegroundColor Yellow
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
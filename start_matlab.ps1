# Start MATLAB with Shared Engine
# This script launches MATLAB and creates the shared engine named 'SimulinkMCP'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting MATLAB with Shared Engine" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$MatlabPath = "C:\Program Files\MATLAB\R2025a"
$MatlabExe = Join-Path $MatlabPath "bin\matlab.exe"

if (-not (Test-Path $MatlabExe)) {
    Write-Host "[ERROR] MATLAB not found at: $MatlabExe" -ForegroundColor Red
    Write-Host "Please update MatlabPath in this script" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "Starting MATLAB..." -ForegroundColor Yellow
Write-Host ""
Write-Host "MATLAB will start and create a shared engine named 'SimulinkMCP'" -ForegroundColor White
Write-Host "Keep MATLAB running while using the MCP server" -ForegroundColor Yellow
Write-Host ""

# Start MATLAB with command to create shared engine
$startupCommand = "matlab.engine.shareEngine('SimulinkMCP'); disp('Shared engine SimulinkMCP started successfully');"

try {
    Start-Process -FilePath $MatlabExe -ArgumentList "-r", $startupCommand -WindowStyle Normal
    Write-Host "[OK] MATLAB started" -ForegroundColor Green
    Write-Host ""
    Write-Host "The shared engine 'SimulinkMCP' should now be available" -ForegroundColor Green
    Write-Host "You can now start the MCP server with: .\start_mcp_server.ps1" -ForegroundColor Cyan
} catch {
    Write-Host "[ERROR] Failed to start MATLAB: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

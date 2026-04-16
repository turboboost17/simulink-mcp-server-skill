# Install MATLAB Engine for Python
# Run this script as Administrator

Write-Host "Installing MATLAB Engine for Python..." -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $ProjectRoot) {
    $ProjectRoot = $PSScriptRoot
}

$MatlabPath = "C:\Program Files\MATLAB\R2025a"
$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$enginePath = Join-Path $MatlabPath "extern\engines\python"

# Check administrator
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "✗ ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run:" -ForegroundColor Yellow
    Write-Host "  cd `"$ProjectRoot`"" -ForegroundColor Cyan
    Write-Host "  .\install_matlab_engine.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Check paths
if (-not (Test-Path $MatlabPath)) {
    Write-Host "✗ MATLAB not found at: $MatlabPath" -ForegroundColor Red
    Write-Host "  Please update the MatlabPath variable in this script" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $venvPython)) {
    Write-Host "✗ Python virtual environment not found at: $venvPython" -ForegroundColor Red
    Write-Host "  Please run 'uv sync' first to create the virtual environment" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $enginePath)) {
    Write-Host "✗ MATLAB Engine source not found at: $enginePath" -ForegroundColor Red
    exit 1
}

Write-Host "MATLAB Path: $MatlabPath" -ForegroundColor Gray
Write-Host "Python Path: $venvPython" -ForegroundColor Gray
Write-Host "Engine Source: $enginePath" -ForegroundColor Gray
Write-Host ""

# Check if already installed
Write-Host "Checking if MATLAB Engine is already installed..." -ForegroundColor Yellow
$installed = & $venvPython -c "try:`n    import matlab.engine`n    print('true')`nexcept:`n    print('false')" 2>$null

if ($installed -eq "true") {
    Write-Host "✓ MATLAB Engine is already installed" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verifying installation..." -ForegroundColor Yellow
    & $venvPython -c "import matlab.engine; print(f'MATLAB Engine version: {matlab.engine.__version__ if hasattr(matlab.engine, \"__version__\") else \"unknown\"}')"
    Write-Host ""
    Write-Host "Installation verified successfully!" -ForegroundColor Green
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 0
}

# Install
Write-Host "Installing MATLAB Engine..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

try {
    Push-Location $enginePath
    & $venvPython setup.py install
    $exitCode = $LASTEXITCODE
    Pop-Location
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "✓ MATLAB Engine installed successfully!" -ForegroundColor Green
        
        # Verify
        Write-Host ""
        Write-Host "Verifying installation..." -ForegroundColor Yellow
        $verifyResult = & $venvPython -c "import matlab.engine; print('SUCCESS')" 2>&1
        
        if ($verifyResult -match "SUCCESS") {
            Write-Host "✓ Installation verified!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Cyan
            Write-Host "1. Start MATLAB" -ForegroundColor White
            Write-Host "2. Run: matlab.engine.shareEngine('SimulinkMCP')" -ForegroundColor Cyan
            Write-Host "3. Test connection: .\.venv\Scripts\python.exe test_connection.py" -ForegroundColor White
        } else {
            Write-Host "⚠ Installation completed but verification failed" -ForegroundColor Yellow
            Write-Host "   Output: $verifyResult" -ForegroundColor Gray
        }
    } else {
        Write-Host "✗ Installation failed with exit code: $exitCode" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Installation failed with error:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

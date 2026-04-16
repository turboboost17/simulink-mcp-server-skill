# Simulink MCP Server - Automated Installation Script
# Run this script to install all dependencies and configure the MCP server

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Simulink MCP Server - Installation" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

# Load configuration
$ConfigFile = Join-Path $ProjectRoot "config.local.ps1"
if (Test-Path $ConfigFile) {
    Write-Host "Loading custom configuration from config.local.ps1..." -ForegroundColor Cyan
    . $ConfigFile
} else {
    # Load default configuration
    $ConfigFile = Join-Path $ProjectRoot "config.ps1"
    if (Test-Path $ConfigFile) {
        . $ConfigFile
    }
    # Set defaults if config not loaded
    if (-not $SHARED_ENGINE_NAME) { $SHARED_ENGINE_NAME = "SimulinkMCP" }
    if (-not $MCP_SERVER_NAME) { $MCP_SERVER_NAME = "simulink-mcp-server" }
}

Write-Host ""

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to find MATLAB installation
function Find-MatlabInstallation {
    # Use configured path if provided
    if ($MATLAB_PATH -and (Test-Path $MATLAB_PATH)) {
        return $MATLAB_PATH
    }
    
    # Try environment variable
    if ($env:MATLAB_PATH -and (Test-Path $env:MATLAB_PATH)) {
        return $env:MATLAB_PATH
    }
    
    # Common installation paths (newest first)
    $commonPaths = @(
        "C:\Program Files\MATLAB\R2025a",
        "C:\Program Files\MATLAB\R2024b",
        "C:\Program Files\MATLAB\R2024a",
        "C:\Program Files\MATLAB\R2023b",
        "C:\Program Files\MATLAB\R2023a"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    
    # Try to find any MATLAB installation
    $matlabRoot = "C:\Program Files\MATLAB"
    if (Test-Path $matlabRoot) {
        $versions = Get-ChildItem $matlabRoot -Directory | Sort-Object Name -Descending
        if ($versions.Count -gt 0) {
            return $versions[0].FullName
        }
    }
    
    return $null
}

# Step 1: Check prerequisites
Write-Host "[1/8] Checking prerequisites..." -ForegroundColor Yellow

# Check MATLAB installation
$MatlabPath = Find-MatlabInstallation
if ($MatlabPath) {
    Write-Host "  ✓ MATLAB found at $MatlabPath" -ForegroundColor Green
} else {
    Write-Host "  ✗ MATLAB not found" -ForegroundColor Red
    Write-Host "    Please install MATLAB or set MATLAB_PATH environment variable" -ForegroundColor Red
    Write-Host "    Example: `$env:MATLAB_PATH = 'C:\Program Files\MATLAB\R2025a'" -ForegroundColor Yellow
    exit 1
}

# Check UV
try {
    $uvVersion = uv --version 2>$null
    Write-Host "  ✓ UV package manager found: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ UV not found" -ForegroundColor Red
    Write-Host "    Install UV from: https://docs.astral.sh/uv/" -ForegroundColor Red
    Write-Host "    Run: powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Yellow
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version 2>$null
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Python not found in PATH (UV will install it)" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Create virtual environment
Write-Host "[2/8] Creating Python virtual environment..." -ForegroundColor Yellow
Set-Location $ProjectRoot

try {
    uv sync --no-prune
    Write-Host "  ✓ Virtual environment created and dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Failed to create virtual environment" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Check administrator privileges for MATLAB Engine
Write-Host "[3/8] Checking for MATLAB Engine installation..." -ForegroundColor Yellow

$venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

# Test if MATLAB Engine is already installed
$engineInstalled = & $venvPython -c "try:`n    import matlab.engine`n    print('true')`nexcept:`n    print('false')" 2>$null

if ($engineInstalled -eq "true") {
    Write-Host "  ✓ MATLAB Engine already installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ MATLAB Engine not installed" -ForegroundColor Yellow
    Write-Host "    MATLAB Engine requires Administrator privileges to install" -ForegroundColor Yellow
    
    if (-not (Test-Administrator)) {
        Write-Host ""
        Write-Host "  ✗ This script is NOT running as Administrator" -ForegroundColor Red
        Write-Host ""
        Write-Host "To install MATLAB Engine, please:" -ForegroundColor Yellow
        Write-Host "1. Open Command Prompt as Administrator" -ForegroundColor Yellow
        Write-Host "2. Run the following commands:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   cd `"$MatlabPath\extern\engines\python`"" -ForegroundColor Cyan
        Write-Host "   $venvPython setup.py install" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Then re-run this script to continue." -ForegroundColor Yellow
        exit 1
    }
    
    # Install MATLAB Engine
    Write-Host "  → Installing MATLAB Engine for Python..." -ForegroundColor Yellow
    $enginePath = Join-Path $MatlabPath "extern\engines\python"
    
    if (-not (Test-Path $enginePath)) {
        Write-Host "  ✗ MATLAB Engine source not found at $enginePath" -ForegroundColor Red
        exit 1
    }
    
    try {
        Push-Location $enginePath
        & $venvPython setup.py install 2>&1 | Out-Null
        Pop-Location
        Write-Host "  ✓ MATLAB Engine installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to install MATLAB Engine" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 4: Verify MATLAB Engine
Write-Host "[4/8] Verifying MATLAB Engine installation..." -ForegroundColor Yellow

try {
    $testResult = & $venvPython -c "import matlab.engine; print('success')" 2>&1
    if ($testResult -match "success") {
        Write-Host "  ✓ MATLAB Engine verified" -ForegroundColor Green
    } else {
        throw "Import failed"
    }
} catch {
    Write-Host "  ✗ MATLAB Engine verification failed" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 5: Check MATLAB shared engine
Write-Host "[5/8] Checking MATLAB shared engine status..." -ForegroundColor Yellow

$matlabRunning = Get-Process -Name "MATLAB" -ErrorAction SilentlyContinue

if ($matlabRunning) {
    Write-Host "  ✓ MATLAB is running" -ForegroundColor Green
    
    # Try to find the shared engine
    $engineCheck = & $venvPython -c @"
import matlab.engine
try:
    engines = matlab.engine.find_matlab()
    if '$SHARED_ENGINE_NAME' in engines:
        print('found')
    else:
        print('notfound')
        print('Available engines:', engines)
except:
    print('error')
"@ 2>&1
    
    if ($engineCheck -match "found") {
        Write-Host "  ✓ Shared engine '$SHARED_ENGINE_NAME' is running" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Shared engine '$SHARED_ENGINE_NAME' not found" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Please start the shared engine in MATLAB:" -ForegroundColor Yellow
        Write-Host "  1. Open MATLAB" -ForegroundColor Yellow
        Write-Host "  2. Run: matlab.engine.shareEngine('$SHARED_ENGINE_NAME')" -ForegroundColor Cyan
        Write-Host ""
    }
} else {
    Write-Host "  ⚠ MATLAB is not running" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  To use the MCP server, you need to:" -ForegroundColor Yellow
    Write-Host "  1. Start MATLAB" -ForegroundColor Yellow
    Write-Host "  2. Run: matlab.engine.shareEngine('$SHARED_ENGINE_NAME')" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""

# Step 6: Create VS Code configuration
Write-Host "[6/8] Creating MCP config for VS Code..." -ForegroundColor Yellow

# Preferred: VS Code MCP config file
$vscodeDir = Join-Path $ProjectRoot ".vscode"
$mcpConfigFile = Join-Path $vscodeDir "mcp.json"

if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
}

$venvPythonEscaped = $venvPython -replace '\\', '\\'
$projectRootEscaped = $ProjectRoot -replace '\\', '\\'
$matlabPathEscaped = $MatlabPath -replace '\\', '\\'

$mcpJsonContent = @"
{
    "servers": {
        "$MCP_SERVER_NAME": {
            "type": "stdio",
            "command": "$venvPythonEscaped",
            "args": ["-m", "simulink_mcp_server.mcp_server"],
            "cwd": "$projectRootEscaped",
            "env": {
                "MATLAB_PATH": "$matlabPathEscaped",
                "SIMULINK_MCP_LOG_LEVEL": "WARNING"
            }
        }
    }
}
"@

try {
        $mcpJsonContent | Out-File -FilePath $mcpConfigFile -Encoding UTF8
        $relativeMcpConfig = $mcpConfigFile -replace [regex]::Escape($ProjectRoot), "."
        Write-Host "  ✓ VS Code MCP config created at $relativeMcpConfig" -ForegroundColor Green
        Write-Host "    Tip: Copy config/mcp.json.example into other workspaces" -ForegroundColor Gray
} catch {
        Write-Host "  ✗ Failed to create VS Code MCP config" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
}

Write-Host ""

# Step 7: Test connection
Write-Host "[7/8] Testing MATLAB Engine connection..." -ForegroundColor Yellow

if ($matlabRunning) {
    try {
        $testOutput = & $venvPython test_connection.py 2>&1
        if ($testOutput -match "Test Complete" -or $testOutput -match "Successfully connected") {
            Write-Host "  ✓ Connection test passed" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Connection test had warnings (see details above)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ✗ Connection test failed" -ForegroundColor Red
        Write-Host "    Run test_connection.py manually for details" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Skipped (MATLAB not running)" -ForegroundColor Yellow
}

Write-Host ""

# Step 8: Summary
Write-Host "[8/8] Installation Summary" -ForegroundColor Yellow
Write-Host ""
Write-Host "✓ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start MATLAB and run: matlab.engine.shareEngine('SimulinkMCP')" -ForegroundColor White
Write-Host "2. Reload VS Code window (Ctrl+Shift+P → 'Reload Window')" -ForegroundColor White
Write-Host "3. Open a Simulink model in MATLAB" -ForegroundColor White
Write-Host "4. Ask GitHub Copilot: 'What model am I currently editing?'" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - Quick Reference: QUICK_REFERENCE.md" -ForegroundColor White
Write-Host "  - Full Install Guide: INSTALL.md" -ForegroundColor White
Write-Host "  - Function List: FUNCTION_ADDITIONS.md" -ForegroundColor White
Write-Host ""
Write-Host "Test scripts:" -ForegroundColor Cyan
Write-Host "  - Test connection: .\.venv\Scripts\python.exe test_connection.py" -ForegroundColor White
Write-Host "  - Test functions: .\.venv\Scripts\python.exe test_interactive_functions.py" -ForegroundColor White
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan

# Pause so user can read the output
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

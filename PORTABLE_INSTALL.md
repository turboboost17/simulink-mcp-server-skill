# Portable Installation Guide

This guide explains how to install the Simulink MCP Server on any Windows machine with MATLAB installed.

## 📦 Quick Install (Automatic)

The installation script now **automatically detects** MATLAB and uses **relative paths**. Just run:

```powershell
.\install.ps1
```

The script will:
- ✅ Auto-detect MATLAB installation (R2025a, R2024b, R2024a, R2023b, R2023a)
- ✅ Use relative paths for all project files
- ✅ Create portable VS Code configuration

## 🔧 Custom Configuration

For non-standard installations, create a `config.local.ps1` file:

```powershell
# Copy the template
Copy-Item config.ps1 config.local.ps1

# Edit config.local.ps1 with your settings
notepad config.local.ps1
```

### Configuration Options

```powershell
# MATLAB Installation Path (leave empty for auto-detection)
$MATLAB_PATH = "C:\Program Files\MATLAB\R2025a"

# Shared Engine Name (must match in MATLAB)
$SHARED_ENGINE_NAME = "SimulinkMCP"

# Python Version for UV (leave empty for default)
$PYTHON_VERSION = "3.12"

# VS Code Settings Location
# Default: ".vscode\settings.json" (workspace)
# User settings: "$env:APPDATA\Code\User\settings.json" (global)
$VSCODE_SETTINGS = ""

# MCP Server Name in Copilot Chat
$MCP_SERVER_NAME = "simulink-mcp-server"
```

## 📂 Installing on Another Computer

### Method 1: Copy Entire Folder

1. **Copy the entire project folder** to the new computer
2. **Delete** the `.venv` folder (it's machine-specific)
3. **Run** `.\install.ps1` on the new machine
4. **Start MATLAB** and run: `matlab.engine.shareEngine('SimulinkMCP')`
5. **Reload VS Code**

### Method 2: Git Clone (Recommended)

1. **Clone the repository**:
   ```powershell
   git clone <your-repo-url> simulink-mcp-server
   cd simulink-mcp-server
   ```

2. **Create custom config** (if needed):
   ```powershell
   Copy-Item config.ps1 config.local.ps1
   # Edit config.local.ps1 if you have non-standard MATLAB location
   ```

3. **Run installer**:
   ```powershell
   .\install.ps1
   ```

4. **Start MATLAB engine**:
   ```matlab
   matlab.engine.shareEngine('SimulinkMCP')
   ```

5. **Reload VS Code**: `Ctrl+Shift+P` → "Reload Window"

### Method 3: Zip Archive

1. **On source computer**, create zip excluding:
   - `.venv/` folder
   - `.vscode/` folder (will be regenerated)
   - `__pycache__/` folders
   - `*.pyc` files

2. **On target computer**:
   ```powershell
   # Extract zip
   Expand-Archive simulink-mcp-server.zip -DestinationPath .
   
   # Run installer
   cd simulink-mcp-server
   .\install.ps1
   ```

## 🔍 MATLAB Auto-Detection

The installer searches for MATLAB in this order:

1. **`$MATLAB_PATH`** variable in `config.local.ps1`
2. **`$env:MATLAB_PATH`** environment variable
3. **Common paths**:
   - `C:\Program Files\MATLAB\R2025a`
   - `C:\Program Files\MATLAB\R2024b`
   - `C:\Program Files\MATLAB\R2024a`
   - `C:\Program Files\MATLAB\R2023b`
   - `C:\Program Files\MATLAB\R2023a`
4. **Any version** in `C:\Program Files\MATLAB\` (newest first)

### Setting MATLAB Path Permanently

**Option 1: Environment Variable** (system-wide):
```powershell
# Set for current session
$env:MATLAB_PATH = "C:\Program Files\MATLAB\R2025a"

# Set permanently (requires admin)
[System.Environment]::SetEnvironmentVariable("MATLAB_PATH", "C:\Program Files\MATLAB\R2025a", "Machine")
```

**Option 2: Config File** (project-specific):
```powershell
# Edit config.local.ps1
$MATLAB_PATH = "C:\Program Files\MATLAB\R2025a"
```

## 📁 What Gets Installed Where

```
simulink-mcp-server/
├── .venv/                    # Virtual environment (machine-specific)
│   └── Scripts/python.exe    # Python interpreter
├── .vscode/                  # VS Code settings (generated)
│   └── mcp.json              # MCP server configuration
├── src/                      # Source code (portable)
├── config.ps1                # Default config (portable)
├── config.local.ps1          # Your custom config (gitignored)
├── install.ps1               # Installer script (portable)
└── pyproject.toml            # Dependencies (portable)
```

**Portable files** (can be copied/committed):
- All `.py` files in `src/`
- `install.ps1`, `start_matlab.ps1`, `start_mcp_server.ps1`
- `config.ps1`, `pyproject.toml`, `uv.lock`
- Documentation files (`.md`)

**Machine-specific files** (regenerate on each machine):
- `.venv/` folder
- `.vscode/mcp.json` (auto-generated with correct paths)
- `.vscode/settings.json` (optional; Copilot-specific config, contains absolute paths)
- `config.local.ps1` (optional, for custom paths)

## 🚀 Deployment Scenarios

### Scenario 1: Team with Same MATLAB Version

All team members have MATLAB R2025a installed in default location:

1. **Commit to Git**:
   - Include: `config.ps1` (with empty `$MATLAB_PATH`)
   - Exclude: `.venv/`, `config.local.ps1`

2. **Team members run**:
   ```powershell
   git clone <repo>
   cd simulink-mcp-server
   .\install.ps1
   ```

3. **Auto-detection works** - no config needed!

### Scenario 2: Team with Different MATLAB Versions

Team members have R2025a, R2024b, R2023b:

1. **Commit to Git**: Same as Scenario 1

2. **Each team member creates** `config.local.ps1`:
   ```powershell
   Copy-Item config.ps1 config.local.ps1
   # Edit if MATLAB not auto-detected
   ```

3. **Run installer**: Auto-detects or uses custom config

### Scenario 3: Non-Standard MATLAB Location

MATLAB installed in `D:\Software\MATLAB\R2025a`:

1. **Create** `config.local.ps1`:
   ```powershell
   $MATLAB_PATH = "D:\Software\MATLAB\R2025a"
   ```

2. **Run installer**:
   ```powershell
   .\install.ps1
   ```

3. **Installer uses** specified path

### Scenario 4: Global VS Code Settings

Want MCP server available in all VS Code windows:

1. **Edit** `config.local.ps1`:
   ```powershell
   $VSCODE_SETTINGS = "$env:APPDATA\Code\User\settings.json"
   ```

2. **Run installer** - updates global settings

3. **MCP server available** in all workspaces

## 🔒 Security Considerations

### `.gitignore` Recommendations

Add to `.gitignore`:
```gitignore
# Machine-specific
.venv/
.vscode/
config.local.ps1
__pycache__/
*.pyc
*.pyo

# MATLAB temp files
*.asv
*.slxc
slprj/
```

### What to Share

**Safe to share**:
- Source code (`src/`)
- Install scripts
- Default config (`config.ps1`)
- Documentation

**Do NOT share**:
- `.venv/` folder (contains machine-specific binaries)
- `config.local.ps1` (may contain machine-specific paths)
- `.vscode/mcp.json` (contains absolute paths)
- `.vscode/settings.json` (optional; contains absolute paths)

## 🐛 Troubleshooting

### "MATLAB not found"

**Solution 1**: Let installer find it
```powershell
# Run installer - it searches multiple locations
.\install.ps1
```

**Solution 2**: Set environment variable
```powershell
$env:MATLAB_PATH = "C:\YourPath\MATLAB\R2025a"
.\install.ps1
```

**Solution 3**: Use config file
```powershell
# Create config.local.ps1
$MATLAB_PATH = "C:\YourPath\MATLAB\R2025a"
```

### "Shared engine not found"

Check the engine name matches in both places:

**In MATLAB**:
```matlab
matlab.engine.shareEngine('SimulinkMCP')
```

**In config**:
```powershell
$SHARED_ENGINE_NAME = "SimulinkMCP"  # Must match!
```

### "Python not found"

UV will install Python automatically. If it fails:
```powershell
# Install UV first
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Run installer again
.\install.ps1
```

### "VS Code doesn't see MCP server"

1. **Check settings file was created**:
   ```powershell
   Get-Content .vscode\settings.json
   ```

2. **Reload VS Code**: `Ctrl+Shift+P` → "Reload Window"

3. **Check paths are correct** in settings.json

4. **Run test**:
   ```powershell
   .venv\Scripts\python.exe -m simulink_mcp_server.mcp_server
   ```

## 📋 Installation Checklist

- [ ] MATLAB installed (any version R2023a or newer)
- [ ] UV package manager installed
- [ ] Project folder copied/cloned
- [ ] Deleted `.venv/` folder (if copied from another machine)
- [ ] Created `config.local.ps1` (if non-standard setup)
- [ ] Run `.\install.ps1`
- [ ] Started MATLAB with `matlab.engine.shareEngine('SimulinkMCP')`
- [ ] Reloaded VS Code
- [ ] Tested with Copilot: "What model am I working on?"

## 🎯 Summary

The Simulink MCP Server is now **fully portable**:

✅ Auto-detects MATLAB installation
✅ Uses relative paths for all project files
✅ Supports custom configurations via `config.local.ps1`
✅ Works with any MATLAB version (R2023a+)
✅ Can be installed workspace-wide or user-wide
✅ Easy to deploy across teams
✅ Git-friendly (excludes machine-specific files)

**Just copy the folder and run `.\install.ps1` - it works!**

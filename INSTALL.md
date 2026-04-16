# Simulink MCP Server - Installation Guide

Complete step-by-step installation instructions for Windows.

## Prerequisites

- **MATLAB R2025a** (or compatible version) with Simulink installed
- **Python 3.10+** (Python 3.12 recommended)
- **UV Package Manager** (https://docs.astral.sh/uv/)
- **VS Code** with GitHub Copilot extension (or Claude Desktop/Cline)
- **Administrator access** (required for MATLAB Engine installation)

## Quick Start

Run the automated installation script:

```powershell
.\install.ps1
```

This will:
1. ✅ Check all prerequisites
2. ✅ Create Python virtual environment with UV
3. ✅ Install MATLAB Engine for Python
4. ✅ Install MCP SDK and dependencies
5. ✅ Configure VS Code settings
6. ✅ Test the installation

## Manual Installation

If you prefer to install manually or the automated script fails, follow these steps:

### Step 1: Install UV Package Manager

```powershell
# Install UV using the official installer
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### Step 2: Set Up Python Environment

```powershell
# Navigate to project directory
cd E:\Documents\MATLAB\MCP\simulink-mcp-server

# Create virtual environment and install dependencies
uv sync --no-prune
```

This creates a `.venv` folder with Python 3.12 and installs all required packages from `pyproject.toml`.

### Step 3: Install MATLAB Engine for Python

**IMPORTANT:** This step requires administrator privileges.

#### Option A: Automated (Recommended)

```powershell
# Run as Administrator
.\install_matlab_engine.ps1
```

#### Option B: Manual Installation

1. Open **Command Prompt as Administrator**
2. Run these commands:

```cmd
cd "C:\Program Files\MATLAB\R2025a\extern\engines\python"
E:\Documents\MATLAB\MCP\simulink-mcp-server\.venv\Scripts\python.exe setup.py install
```

Verify the installation:

```powershell
.\.venv\Scripts\python.exe -c "import matlab.engine; print('MATLAB Engine installed successfully!')"
```

### Step 4: Start MATLAB with Shared Engine

**Before using the MCP server**, you must start MATLAB and create a shared engine named `SimulinkMCP`:

```matlab
% In MATLAB Command Window:
matlab.engine.shareEngine('SimulinkMCP')
```

**Keep MATLAB running** with this shared engine while using the MCP server.

> **Tip:** Add this to your MATLAB startup script (`startup.m`) to run automatically:
> ```matlab
> try
>     matlab.engine.shareEngine('SimulinkMCP');
>     disp('Shared engine "SimulinkMCP" started successfully');
> catch ME
>     warning('Failed to start shared engine: %s', ME.message);
> end
> ```

### Step 5: Configure VS Code

#### Recommended: `.vscode/mcp.json`

1. Copy [config/mcp.json.example](config/mcp.json.example) into your project as `.vscode/mcp.json`.
2. Replace the placeholders for your installation.
3. Reload VS Code (`Ctrl+Shift+P` → "Reload Window").

This starts the server with:
- `python -m simulink_mcp_server.mcp_server`

#### Optional: Copilot settings

If you need a Copilot-specific configuration, copy
[config/copilot.settings.json.example](config/copilot.settings.json.example) into `.vscode/settings.json`.

### Step 6: Test the Installation

1. **Test MATLAB Engine Connection:**

```powershell
.\.venv\Scripts\python.exe test_connection.py
```

Expected output:
```
✓ MATLAB Engine Python package is available
✓ Shared engine 'SimulinkMCP' found
✓ Successfully connected to MATLAB engine
✓ Simulink is available
```

2. **Test Interactive Functions:**

Open a Simulink model in MATLAB, then run:

```powershell
.\.venv\Scripts\python.exe test_interactive_functions.py
```

Expected output:
```
Current model: <your_model_name>
Current block: <selected_block>
✓ Interactive function tests complete!
```

3. **Test VS Code Integration:**

   a. Reload VS Code: `Ctrl+Shift+P` → "Reload Window"
   
   b. Open GitHub Copilot Chat: `Ctrl+Shift+I`
   
   c. Try these commands:
   - "What model am I currently editing?"
   - "What block do I have selected?"
   - "Find all Gain blocks in this model"

## Troubleshooting

### Issue: "MATLAB Engine not found"

**Solution:**
- Ensure you ran the installation as Administrator
- Check that MATLAB is installed at `C:\Program Files\MATLAB\R2025a`
- Verify Python version is 3.9-3.12 (MATLAB Engine compatibility)

### Issue: "Shared engine 'SimulinkMCP' not found"

**Solution:**
```matlab
% In MATLAB:
matlab.engine.shareEngine('SimulinkMCP')

% Verify it's running:
matlab.engine.find_matlab()
% Should show 'SimulinkMCP' in the list
```

### Issue: "Module 'mcp' not found"

**Solution:**
```powershell
# Reinstall dependencies
uv sync --refresh --no-prune
```

### Issue: VS Code doesn't recognize the MCP server

**Solution:**
1. Check `.vscode/mcp.json` has correct absolute paths
   - If using Copilot-specific config: check `.vscode/settings.json`
2. Reload VS Code window: `Ctrl+Shift+P` → "Reload Window"  
3. Check Output panel: View → Output → "GitHub Copilot Chat"
4. Verify MATLAB shared engine is running

### Issue: Permission denied during MATLAB Engine installation

**Solution:**
- Must run Command Prompt **as Administrator**
- Close all Python processes before installation
- Try disabling antivirus temporarily

## Updating

To update the MCP server:

```powershell
# Update dependencies
uv sync --upgrade --no-prune

# Re-test installation
.\.venv\Scripts\python.exe test_connection.py
```

## Uninstalling

```powershell
# Remove virtual environment
Remove-Item -Recurse -Force .venv

# Remove VS Code configuration
# Delete `.vscode/mcp.json` (or remove this server from it)
```

## Next Steps

After successful installation:

1. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common workflows
2. Review [FUNCTION_ADDITIONS.md](FUNCTION_ADDITIONS.md) for available functions
3. Try the examples in [examples/demo.py](examples/demo.py)
4. Start asking GitHub Copilot to interact with your Simulink models!

## Support

If you encounter issues:

1. Run the diagnostic script: `.\test_connection.py`
2. Check MATLAB and Python versions are compatible
3. Verify all paths in VS Code settings are correct
   - If using VS Code MCP config: check `.vscode/mcp.json`
   - If using Copilot-specific config: check `.vscode/settings.json`
4. Ensure MATLAB shared engine is running
5. Review VS Code Output panel for error messages

## Version Compatibility

| Component | Tested Version | Minimum Version |
|-----------|----------------|-----------------|
| MATLAB | R2025a | R2020b+ |
| Simulink | 25.1 | 10.2+ |
| Python | 3.12.12 | 3.10 |
| UV | 0.9.2 | 0.4.0 |
| MCP SDK | 1.17.0 | 1.0.0 |

---

**Installation complete!** 🎉 You can now use natural language to interact with Simulink through VS Code.

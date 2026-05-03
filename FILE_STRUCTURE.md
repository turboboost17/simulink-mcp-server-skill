# Simulink MCP Server - File Structure & Purpose

This document explains what each file does and why it exists.

## 📁 Core Source Files

### `.agents/`
Portable agent customization assets.

- **`skills/`**
  - Adapted plaintext MATLAB, Simulink, and Model-Based Design skills for agent workflows.
  - Uses the portable `.agents/skills/<skill-name>/SKILL.md` convention.
  - Keeps execution mapped to this server's local MCP tools.

See `docs/MATHWORKS_AGENTIC_TOOLKIT_REVIEW.md` and
`docs/MATHWORKS_MATLAB_AGENTIC_TOOLKIT_REVIEW.md` for import and compatibility
notes.

### `src/simulink_mcp_server/`
Main server implementation directory.

- **`mcp_server.py`** ⭐ MCP ENTRYPOINT
  - Runs the MCP stdio JSON-RPC loop
  - Registers tools and routes requests to the implementation in `server.py`
  - This is the process VS Code connects to

- **`server.py`** ⭐ IMPLEMENTATION
  - Manages MATLAB Engine connection with shared engine 'SimulinkMCP'
  - Implements MATLAB/Simulink operations used by MCP tools

- **`__init__.py`**
  - Python package initialization
  - Makes the directory a Python package

## 📁 Installation Scripts

### Main Installer
- **`install.ps1`** ⭐ RUN THIS FIRST
  - Automated installation wizard
  - Checks prerequisites (MATLAB, Python, UV)
  - Creates virtual environment
  - Installs MATLAB Engine (if admin)
  - Creates VS Code MCP config (`.vscode/mcp.json`)
  - Runs diagnostic tests

### Component Installers
- **`install_matlab_engine.ps1`**
  - Standalone MATLAB Engine installer
  - Must be run as Administrator
  - Use this if main installer couldn't install engine

## 📁 Startup Scripts

### Starting MATLAB
- **`start_matlab.ps1`** / **`start_matlab.bat`**
  - Launches MATLAB with the command:
    ```matlab
    matlab.engine.shareEngine('SimulinkMCP')
    ```
  - Creates the shared engine that the MCP server connects to
  - Must run this before using the MCP server

### Starting MCP Server
- **`start_mcp_server.ps1`** / **`start_mcp_server.bat`**
  - Checks MATLAB is running
  - Sets environment variables (MATLAB_PATH, SIMULINK_MCP_LOG_LEVEL)
  - Activates Python virtual environment
  - Runs: `python -m simulink_mcp_server.mcp_server`
  - Use this for standalone testing (not needed for VS Code integration)

## 📁 Test Scripts

- **`test_connection.py`** ⭐ DIAGNOSTICS
  - Tests MATLAB installation
  - Tests Python Engine availability
  - Tests shared engine connection
  - Tests Simulink availability
  - Run this when troubleshooting: `.\.venv\Scripts\python.exe test_connection.py`

- **`test_interactive_functions.py`**
  - Tests all 29 interactive Simulink functions
  - Requires an open Simulink model
  - Verifies context awareness (bdroot, gcb, gcs, etc.)
  - Run: `.\.venv\Scripts\python.exe test_interactive_functions.py`

## 📁 Documentation

### User Guides
- **`GETTING_STARTED.md`** ⭐ START HERE
  - Quick 5-minute setup guide
  - Your first tasks tutorial
  - Common workflows
  - Perfect for new users

- **`INSTALL.md`**
  - Detailed installation instructions
  - Manual installation steps
  - Troubleshooting guide
  - Version compatibility matrix

- **`QUICK_REFERENCE.md`**
  - Daily command reference
  - Common workflows
  - Natural language examples
  - Best practices

### Technical Documentation
- **`FUNCTION_ADDITIONS.md`**
  - Complete documentation of all 29 functions
  - Usage examples for each function
  - Before/after comparison
  - Test results

- **`README.md`** ⭐ MAIN README
  - Project overview
  - Quick start
  - Feature list
  - Installation summary
  - Complete function list

- **`VSCODE_SETUP.md`**
  - VS Code configuration details
  - GitHub Copilot Chat setup
  - Claude Desktop setup
  - Cline extension setup
  - Configuration examples

- **`docs/ENTERPRISE_DEPLOYMENT.md`**
  - Non-UV, locked, and offline wheelhouse installation guidance
  - Corporate MCP registry notes
  - `SIMULINK_MCP_MODE` deployment profiles

- **`docs/SIMULINK_FUNCTION_GAPS.md`**
  - Public, sanitized list of unimplemented Simulink API candidates
  - Replaces local saved MathWorks HTML exports for self-evaluation workflows

- **`docs/RELEASE_PROCESS.md`**
  - Versioned release, checksum, SBOM, and registry promotion process

## 📁 Configuration Files

### Python Environment
- **`pyproject.toml`**
  - Python project configuration
  - Dependencies (mcp, matlab-engine-for-python)
  - Project metadata
  - UV package manager configuration

- **`.python-version`**
  - Specifies Python version for UV (3.12.12)

- **`uv.lock`**
  - Dependency lock file (auto-generated)
  - Ensures reproducible installations

### VS Code Configuration
- **`config/mcp.json.example`** ⭐ TEMPLATE
  - Portable MCP config template you can copy into other workspaces

- **`config/mcp.readonly.json.example`**, **`config/mcp.open.json.example`**, **`config/mcp.full.json.example`**
  - Mode-specific MCP config templates for registry and agent policy scoping

- **`.vscode/mcp.json`** ⭐ AUTO-GENERATED (workspace-local)
  - Created by `install.ps1` in this workspace
  - Contains absolute paths to the Python interpreter and project folder
  - Used by VS Code MCP hosts

- **`config/copilot.settings.json.example`** (optional template)
  - Copilot-specific configuration template (`github.copilot.chat.mcpServers`)

### Git Configuration
- **`.gitignore`**
  - Specifies files Git should ignore
  - Excludes .venv, __pycache__, .pyc, etc.

## 📁 Examples

- **`examples/demo.py`**
  - Programmatic usage examples
  - Shows how to use MCP functions directly in Python
  - Demonstrates creating models, adding blocks, etc.
  - For advanced users who want to script Simulink operations

## 📁 Tests

- **`tests/test_basic.py`**
  - Unit tests for basic functionality
  - Run with: `uv run --extra dev pytest tests/`

## 📁 Build Artifacts (Auto-generated)

- **`.venv/`** - Virtual environment directory (created by `uv sync`)
  - Tip: use `uv sync --no-prune` to avoid uninstalling the manually-installed MATLAB Engine package
- **`.git/`** - Git repository data

## 🔄 Typical File Usage Flow

### First Time Setup
1. Run `install.ps1` → Creates `.venv/`, writes `.vscode/mcp.json`
2. Run `install_matlab_engine.ps1` (as Admin) → Installs MATLAB Engine
3. Read `GETTING_STARTED.md` → Learn how to use

### Daily Usage
1. Run `start_matlab.ps1` → Starts MATLAB with shared engine
2. Open VS Code → Reload window
3. Use GitHub Copilot Chat → Uses MCP server via `.vscode/mcp.json` (or Copilot settings, if configured)

### Troubleshooting
1. Run `test_connection.py` → Diagnose connection issues
2. Read `INSTALL.md` → Check detailed troubleshooting
3. Run `test_interactive_functions.py` → Test specific functions

## 📋 Files You Can Safely Delete

These files are not needed for normal operation:

- ~~`main.py`~~ - Removed (was duplicate entry point)
- ~~`find_mujoco.py`~~ - Removed (was temporary test script)
- ~~`matlab_engine_temp/`~~ - Removed (was temporary build directory)
- ~~`vscode-user-settings-example.json`~~ - Removed (info in VSCODE_SETUP.md)
- ~~`claude_desktop_config.json`~~ - Removed (info in VSCODE_SETUP.md)
- ~~`cline-config.json`~~ - Removed (info in VSCODE_SETUP.md)

## 📋 Files You Should NOT Delete

### Critical for Operation
- `src/simulink_mcp_server/mcp_server.py` - MCP entrypoint
- `src/simulink_mcp_server/server.py` - Implementation
- `.venv/` - Python virtual environment
- `pyproject.toml` - Dependency specification

### Critical for Installation
- `install.ps1` - Main installer
- `install_matlab_engine.ps1` - Engine installer
- `uv.lock` - Dependency lock file

### Critical for Usage
- All documentation files (*.md)
- All startup scripts (start_*.ps1, start_*.bat)
- All test scripts (test_*.py)

## 🎯 Quick Command Reference

```powershell
# Installation
.\install.ps1

# Start MATLAB with shared engine
.\start_matlab.ps1

# Test connection
.\.venv\Scripts\python.exe test_connection.py

# Test functions (with open model)
.\.venv\Scripts\python.exe test_interactive_functions.py

# Run example
.\.venv\Scripts\python.exe examples\demo.py

# Run tests
uv run --extra dev pytest tests/

# Update dependencies
uv sync --upgrade --no-prune
```

## 📊 File Count Summary
Need help? Start with [GETTING_STARTED.md](GETTING_STARTED.md) for a complete walkthrough.

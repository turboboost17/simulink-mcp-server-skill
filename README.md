# Simulink MCP Server

A Model Context Protocol (MCP) server that provides VS Code agents with comprehensive MATLAB and Simulink functionality through a shared MATLAB engine connection using `matlab.engine.shareEngine`.

## 🚀 Quick Start (5 Minutes)

```powershell
# 1. Run automated installer
.\install.ps1

# 2. Start MATLAB with shared engine
.\start_matlab.ps1
# Or manually in MATLAB: matlab.engine.shareEngine('SimulinkMCP')

# 3. Reload VS Code (Ctrl+Shift+P → "Reload Window")

# 4. Open a Simulink model in MATLAB

# 5. Ask GitHub Copilot: 
#    "What model am I currently editing?"
#    "Create a 10x10 magic square in MATLAB"
#    "Calculate eigenvalues of my matrix A"
```

**📖 Complete walkthrough:** [GETTING_STARTED.md](GETTING_STARTED.md)
**🔧 Detailed installation:** [INSTALL.md](INSTALL.md)

## Features

### 🆕 MATLAB Code Execution (NEW!)
- **Execute Code**: Run arbitrary MATLAB code snippets
- **Workspace Variables**: Get/set/list/clear workspace variables
- **Expression Evaluation**: Evaluate MATLAB expressions and get results
- **Script Execution**: Run MATLAB .m script files
- **Function Calls**: Call built-in or custom MATLAB functions
- **Single Context**: Unified workspace for both Simulink and MATLAB operations

### Interactive Context Awareness ⭐
- **Query current state**: Get active model, selected blocks, current subsystem
- **Smart search**: Find blocks by type, name, or properties
- **Model status**: Check for unsaved changes, loaded models
- **Visual feedback**: Highlight blocks with color coding

### Core Simulink Operations
- **Model Management**: Create, load, save Simulink models
- **Block Operations**: Add blocks, connect blocks, create subsystems  
- **Parameter Control**: Get/set block parameters
- **Bus Operations**: Create bus elements, bus selectors
- **Simulation**: Run simulations with configurable parameters
- **Layout & Cleanup**: Auto-arrange blocks, route signal lines

### Engine Management
- **Shared Engine**: Uses `matlab.engine.shareEngine('SimulinkMCP')` for multi-process access
- **Fallback Mode**: Gracefully handles disconnections
- **Connection Management**: Automatic reconnection and error handling

## What's New

### Version 0.2.0 - Release Hardening
- MIT license, security policy, third-party notices, and MathWorks trademark attribution
- `SIMULINK_MCP_MODE` with `readonly`, `open`, and `full` tool exposure modes
- Non-UV and offline wheelhouse installation guidance for enterprise review
- Sanitized `.github` Copilot instructions and skills for public repo use
- Function-gap markdown that replaces local saved MathWorks HTML exports
- CI and release workflows for tests, type checking, audit, SBOM, wheels, source distributions, checksums, and GitHub release artifacts
- Total MCP tools: 43

## Installation

### Automated Installation (Recommended)

The installer now **auto-detects MATLAB** and uses **portable paths**:

```powershell
.\install.ps1
```

This script will:
- ✅ Auto-detect MATLAB installation (R2025a → R2023a)
- ✅ Create virtual environment with UV
- ✅ Install MATLAB Engine for Python
- ✅ Configure VS Code with relative paths
- ✅ Test the installation

### Portable Installation

To install on **another computer**, see **[PORTABLE_INSTALL.md](PORTABLE_INSTALL.md)** for:
- ✅ Auto-detection of MATLAB versions
- ✅ Custom configuration via `config.local.ps1`
- ✅ Team deployment strategies
- ✅ Non-standard MATLAB locations

**Quick portable install**:
```powershell
# Copy project folder to new computer
# Delete .venv folder
# Run installer - it auto-detects everything!
.\install.ps1
```

### Manual Installation

See [INSTALL.md](INSTALL.md) for step-by-step manual installation instructions.

### Prerequisites
- **MATLAB** (R2023a or newer) with Simulink
- **Python 3.10+** (installed by UV automatically)
- **UV package manager** ([install](https://docs.astral.sh/uv/)) for the automated installer, or standard `venv`/`pip` for non-UV environments
- **VS Code** with GitHub Copilot extension
- **Administrator access** (for MATLAB Engine installation only)

## VS Code Integration

### Prerequisites
1. Start MATLAB and create a shared engine:
   ```matlab
   matlab.engine.shareEngine('SimulinkMCP')
   ```
2. Run the installer (`.\install.ps1`) to set up `.venv/` and install the MATLAB Engine.

### Recommended: VS Code `.vscode/mcp.json`
Copy [config/mcp.json.example](config/mcp.json.example) into your *project* as `.vscode/mcp.json`, then replace the placeholders.

This repo’s MCP entrypoint is:
- `python -m simulink_mcp_server.mcp_server`

For review-only use, start from
[config/mcp.readonly.json.example](config/mcp.readonly.json.example). For trusted
local editing, use [config/mcp.full.json.example](config/mcp.full.json.example).

### Optional: Copilot-specific settings
If you need a Copilot-specific configuration, copy
[config/copilot.settings.json.example](config/copilot.settings.json.example) into `.vscode/settings.json`.

## Available Tools

### Interactive Context Functions (NEW!)
Get information about your current position and selection in the Simulink Editor:

- `simulink_get_current_model()` - Get active model name (bdroot)
- `simulink_get_current_block()` - Get selected block path (gcb)
- `simulink_get_current_block_handle()` - Get selected block handle (gcbh)
- `simulink_get_current_system()` - Get active system/subsystem (gcs)
- `simulink_get_selected_blocks()` - Get all selected blocks
- `simulink_find_blocks(model_name, criteria)` - Find blocks matching criteria

### Engine Management
- `connect_simulink_engine()` - Connect to shared MATLAB engine

### Model Operations
- `simulink_new_model(model_name)` - Create new Simulink model
- `simulink_load_model(file_path)` - Load model from file
- `simulink_save_model(model_name, file_path?)` - Save model to file
- `simulink_run_simulation(model_name, stop_time?)` - Run simulation
- `simulink_model_is_loaded(model_name)` - Check if model is in memory (NEW!)
- `simulink_model_is_dirty(model_name)` - Check for unsaved changes (NEW!)

### Block Operations  
- `simulink_add_block(model_name, block_type, block_name, position?)` - Add block to model
- `simulink_delete_block(block_path)` - Delete block from model (NEW!)
- `simulink_replace_block(model_name, old_type, new_type)` - Replace blocks (NEW!)
- `simulink_list_blocks(model_name, block_type?)` - List blocks in model
- `simulink_highlight_block(block_path, color?)` - Highlight block (NEW!)

### Connection Operations
- `simulink_connect_blocks(model_name, source_block, source_port, dest_block, dest_port)` - Connect blocks
- `simulink_delete_line(model_name, source_block, source_port, dest_block, dest_port)` - Delete line (NEW!)

### Parameter Management
- `simulink_get_param(model_name, block_name, parameter)` - Get block parameter
- `simulink_set_param(model_name, block_name, parameter, value)` - Set block parameter

### Hierarchy & Layout
- `simulink_create_subsystem(model_name, blocks, subsystem_name)` - Create subsystem from blocks
- `simulink_expand_subsystem(subsystem_path)` - Replace subsystem with contents (NEW!)
- `simulink_arrange_system(system_path)` - Auto-layout blocks (NEW!)
- `simulink_route_line(line_handle)` - Auto-route signal line (NEW!)

### Advanced Features
- `simulink_add_bus_element(model_name, bus_object_name, element_name, data_type, dimensions)` - Add bus element
- `simulink_create_bus_selector(model_name, bus_signal_block, selected_signals, selector_name)` - Create bus selector

**Subtotal: 28 Simulink and engine tools**

### MATLAB Code Execution (NEW!)
- `matlab_execute_code(code, capture_output?)` - Execute arbitrary MATLAB code
- `matlab_eval_expression(expression)` - Evaluate expression and get result
- `matlab_get_workspace_variable(variable_name)` - Get variable from workspace
- `matlab_set_workspace_variable(variable_name, value)` - Set workspace variable
- `matlab_list_workspace_variables()` - List all variables in workspace
- `matlab_clear_workspace(variables?)` - Clear variables (all if empty)
- `matlab_run_script(script_path)` - Run MATLAB .m script file
- `matlab_call_function(function_name, *args, nargout?)` - Call MATLAB function

**Total: 8 MATLAB functions**

### MATLAB Code Quality
- `matlab_check_code(script_path)` - Run MATLAB static code analysis
- `matlab_run_tests(script_path)` - Run MATLAB tests
- `matlab_detect_toolboxes()` - List installed MATLAB products and versions

**Total: 3 code quality tools**

### Async Execution & Performance
- `matlab_execute_async(code)` - Start long-running MATLAB code asynchronously
- `matlab_check_task(task_id)` - Check async task status
- `matlab_cancel_task(task_id)` - Cancel async task
- `matlab_perf_summary()` - Summarize recent MATLAB execution timings

**Total: 4 async/performance tools**

**Grand total: 43 MCP tools**

## Usage Examples

See [GETTING_STARTED.md](GETTING_STARTED.md) for a complete walkthrough.

### MATLAB Code Execution (NEW!)
```python
# Execute code and capture output
matlab_execute_code("disp('Hello from MATLAB!')")
# Returns: {'status': 'success', 'output': 'Hello from MATLAB!\n'}

# Evaluate mathematical expression
matlab_eval_expression("2^10 + sqrt(144)")
# Returns: {'status': 'success', 'value': 1036.0, 'type': 'float'}

# Create and manipulate variables
matlab_set_workspace_variable("my_matrix", [[1, 2], [3, 4]])
matlab_get_workspace_variable("my_matrix")
# Returns: {'status': 'success', 'value': [[1, 2], [3, 4]], 'type': 'array'}

# Call MATLAB functions
matlab_call_function("magic", 5, nargout=1)
# Returns: {'status': 'success', 'result': [[17,24,1,8,15],...]}

# Run analysis code
code = """
x = 1:100;
y = sin(x/10);
mean_y = mean(y);
std_y = std(y);
fprintf('Mean: %.4f, Std: %.4f\\n', mean_y, std_y);
"""
matlab_execute_code(code)

# List workspace variables
matlab_list_workspace_variables()
# Returns: {'status': 'success', 'variables': ['x', 'y', 'mean_y', ...]}
```

### Unified Simulink + MATLAB Workflow
```python
# 1. Create Simulink model
simulink_new_model("AnalysisModel")

# 2. Simulate and get results
simulink_run_simulation("AnalysisModel", 10.0)

# 3. Analyze simulation results in MATLAB
matlab_execute_code("""
% Load simulation output
out = evalin('base', 'out');
time = out.tout;
signals = out.yout;

% Perform analysis
peak_value = max(signals);
settling_time = time(find(abs(signals - peak_value) < 0.02, 1));

fprintf('Peak: %.4f, Settling time: %.4f\\n', peak_value, settling_time);
""")

# 4. Use analysis results to modify model
peak = matlab_get_workspace_variable("peak_value")
simulink_set_param("AnalysisModel", "Gain1", "Gain", str(peak['value']))
```

### Creating a Simple Model
```python
# Create new model
simulink_new_model("MyModel")

# Add source block
simulink_add_block("MyModel", "simulink/Sources/Constant", "Constant1", [30, 30, 60, 60])

# Add scope block  
simulink_add_block("MyModel", "simulink/Sinks/Scope", "Scope1", [120, 30, 150, 60])

# Connect blocks
simulink_connect_blocks("MyModel", "Constant1", 1, "Scope1", 1)

# Set constant value
simulink_set_param("MyModel", "Constant1", "Value", "5")

# Run simulation
simulink_run_simulation("MyModel", 10.0)

# Save model
simulink_save_model("MyModel")
```

### Interactive Context Queries
```python
# Get current model name
simulink_get_current_model()

# Get selected block
simulink_get_current_block()

# Find blocks by type
simulink_find_blocks("MyModel", {"BlockType": "Gain"})

# Highlight block
simulink_highlight_block("MyModel/Gain1", "green")

# Auto-arrange layout
simulink_arrange_system("MyModel")
```

### Working with Bus Signals
```python
# Create bus element
simulink_add_bus_element("MyModel", "MyBus", "signal1", "double", "1")
simulink_add_bus_element("MyModel", "MyBus", "signal2", "int32", "[1 3]")

# Create bus selector
simulink_create_bus_selector("MyModel", "BusCreator1", ["signal1", "signal2"], "BusSelector1")
```

## Scripts

### Installation
- `install.ps1` - Automated installation (recommended)
- `install_matlab_engine.ps1` - Install MATLAB Engine separately (as Admin)

### Starting
- `start_matlab.ps1` - Start MATLAB with shared engine 'SimulinkMCP'
- `start_mcp_server.ps1` - Start the MCP server (after MATLAB is running)

### Testing
- `test_connection.py` - Test MATLAB Engine connection
- `test_interactive_functions.py` - Test interactive Simulink functions

## Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Quick start guide (5 minutes)
- **[INSTALL.md](INSTALL.md)** - Detailed installation instructions
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands and workflows
- **[FUNCTION_ADDITIONS.md](FUNCTION_ADDITIONS.md)** - Complete function documentation
- **[VSCODE_SETUP.md](VSCODE_SETUP.md)** - VS Code configuration details

## Environment Variables

- `MATLAB_PATH` - Path to MATLAB installation (default: `C:/Program Files/MATLAB/R2025a`)
- `SIMULINK_MCP_LOG_LEVEL` - Logging level (`WARNING` by default; set to `INFO`/`DEBUG` to troubleshoot)
- `SIMULINK_MCP_MODE` - Tool exposure mode: `readonly`, `open`, or `full` (`full` by default for backward compatibility)

### Tool Exposure Modes

| Mode | Intended use | Tool surface |
|------|--------------|--------------|
| `readonly` | Ask/review agents | Inspect current context, find/list blocks, read parameters/status, read workspace variables, code check, toolbox detection |
| `open` | Review agents that can open models | `readonly` plus model loading and editor highlighting |
| `full` | Trusted local development | All 43 tools, including MATLAB execution, model edits, save, simulation, async tasks |

See [docs/ENTERPRISE_DEPLOYMENT.md](docs/ENTERPRISE_DEPLOYMENT.md) for corporate registry and offline install guidance.

## Troubleshooting

See [GETTING_STARTED.md](GETTING_STARTED.md#troubleshooting) for common issues.

### Quick Diagnostics

```powershell
# Test MATLAB Engine connection
.\.venv\Scripts\python.exe test_connection.py

# Test interactive functions (requires open model)
.\.venv\Scripts\python.exe test_interactive_functions.py

# Check shared engine status (in MATLAB)
matlab.engine.find_matlab()
```

### Common Issues

**"Shared engine not found"**
- Start MATLAB and run: `matlab.engine.shareEngine('SimulinkMCP')`

**"No model currently open"**
- Open a Simulink model in MATLAB before querying

**VS Code doesn't see MCP server**
- Reload VS Code window: `Ctrl+Shift+P` → "Reload Window"
- Check `.vscode/mcp.json` has correct paths

## Development

### Running Tests
```bash
# Install dev dependencies
uv sync --extra dev --no-prune

# Run tests
uv run --extra dev pytest tests/
```

Without UV:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -m "not integration"
```

### Development Mode
```bash
uv run python -m simulink_mcp_server.mcp_server
```

### Building Package
```bash
uv build
```

## Project Structure

```
simulink-mcp-server/
├── src/
│   └── simulink_mcp_server/
│       ├── __init__.py
│       ├── server.py          # MATLAB/Simulink functions + engine management
│       └── mcp_server.py      # MCP stdio server exposing tools
├── tests/
│   └── test_basic.py
├── examples/
│   └── demo.py
├── config/
│   ├── mcp.json.example       # Template for VS Code `.vscode/mcp.json`
│   └── copilot.settings.json.example  # Optional Copilot settings template
├── install.ps1                # Automated installer
├── install_matlab_engine.ps1  # MATLAB Engine installer
├── start_matlab.ps1           # Start MATLAB with shared engine
├── start_mcp_server.ps1       # Start MCP server
├── test_connection.py         # Connection diagnostics
├── test_interactive_functions.py  # Function tests
├── GETTING_STARTED.md         # Quick start guide
├── INSTALL.md                 # Detailed installation
├── QUICK_REFERENCE.md         # Command reference
├── FUNCTION_ADDITIONS.md      # Function documentation
├── README.md                  # This file
└── pyproject.toml             # Python dependencies
```

## Version Compatibility

| Component | Tested Version | Minimum Version |
|-----------|----------------|-----------------|
| MATLAB | R2025a | R2020b+ |
| Simulink | 25.1 | 10.2+ |
| Python | 3.12.12 | 3.10 |
| UV | 0.9.2 | 0.4.0 |
| MCP SDK | 1.17.0 | 1.17.0 |

## Contributing

This project uses:
- **UV** or standard `venv`/`pip` for Python package management
- **MCP SDK** for protocol implementation
- **MATLAB Engine API** for MATLAB/Simulink interaction

## License

This project is released under the MIT License. See [LICENSE](LICENSE).

MATLAB and Simulink are registered trademarks of The MathWorks, Inc. This
project is not affiliated with, sponsored by, or endorsed by The MathWorks, Inc.

---

**Ready to start?** Run `.\install.ps1` and see [GETTING_STARTED.md](GETTING_STARTED.md)!

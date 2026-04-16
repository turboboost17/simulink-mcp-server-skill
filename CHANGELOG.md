# Changelog - Simulink MCP Server

## Version 2.0 - MATLAB Code Execution Integration (Current)

### 🆕 New Features

#### MATLAB Code Execution (8 New Functions)
Added comprehensive MATLAB scripting capabilities to complement Simulink visual modeling:

- **`matlab_execute_code(code, capture_output)`** - Execute arbitrary MATLAB code snippets
- **`matlab_eval_expression(expression)`** - Evaluate expressions and get results
- **`matlab_get_workspace_variable(variable_name)`** - Retrieve workspace variables
- **`matlab_set_workspace_variable(variable_name, value)`** - Set workspace variables
- **`matlab_list_workspace_variables()`** - List all workspace variables with details
- **`matlab_clear_workspace(variables)`** - Clear specific or all variables
- **`matlab_run_script(script_path)`** - Run MATLAB .m script files
- **`matlab_call_function(function_name, *args, nargout)`** - Call MATLAB functions

#### Unified Workspace
- Single shared MATLAB workspace for both Simulink and MATLAB operations
- Variables persist across tool calls
- Seamless integration: simulate in Simulink → analyze in MATLAB → modify model based on results

### 🔧 Improvements

#### Data Type Handling
- Automatic conversion between Python and MATLAB types
- Support for scalars, arrays, matrices, and strings
- JSON serialization for complex MATLAB types
- Proper handling of MATLAB double, logical, char, and cell arrays

#### Error Handling
- Graceful error reporting for invalid code
- Variable existence checking before retrieval
- Script file validation before execution
- Function availability checking

### 📚 Documentation Updates

#### New Examples
- MATLAB code execution examples in README.md
- Unified Simulink + MATLAB workflows in QUICK_REFERENCE.md
- Comprehensive function documentation in FUNCTION_ADDITIONS.md
- Test script: `test_matlab_functions.py`

#### Updated Files
- README.md: Added MATLAB features section with examples
- QUICK_REFERENCE.md: Added MATLAB workflows and commands
- FUNCTION_ADDITIONS.md: Documented all 8 new MATLAB functions
- server.py: Updated console output to show 37 total functions

### 📊 Statistics

- **Total Functions**: 37 (29 Simulink + 8 MATLAB)
- **Lines of Code Added**: ~400 lines in server.py
- **Tool Definitions Added**: 8 new MCP tools in mcp_server.py
- **Test Coverage**: 10 test cases in test_matlab_functions.py

### 🎯 Use Cases Enabled

1. **Simulation Analysis**: Run Simulink simulation → analyze results in MATLAB
2. **Parametric Modeling**: Generate model parameters in MATLAB → create Simulink blocks
3. **Data Processing**: Process external data in MATLAB → feed into Simulink model
4. **Algorithm Validation**: Test algorithms in MATLAB → implement in Simulink
5. **Report Generation**: Extract Simulink data → process and visualize in MATLAB

---

## Version 1.0 - Interactive Context Awareness

### Initial Release Features

#### Interactive Context Functions (6 functions)
- `simulink_get_current_model()` - Get active model (bdroot)
- `simulink_get_current_block()` - Get selected block (gcb)
- `simulink_get_current_block_handle()` - Get block handle (gcbh)
- `simulink_get_current_system()` - Get active system (gcs)
- `simulink_get_selected_blocks()` - Get all selected blocks
- `simulink_find_blocks(model, criteria)` - Enhanced block search

#### Enhanced Editing Functions (10 functions)
- `simulink_delete_block(block_path)` - Delete blocks
- `simulink_delete_line()` - Delete connections
- `simulink_replace_block()` - Replace block types
- `simulink_highlight_block()` - Visual feedback
- `simulink_arrange_system()` - Auto-layout
- `simulink_route_line()` - Auto-route lines
- `simulink_expand_subsystem()` - Flatten hierarchy
- `simulink_model_is_loaded()` - Check model status
- `simulink_model_is_dirty()` - Check for unsaved changes

#### Core Simulink Functions (13 functions)
- Model management: new, load, save, simulate
- Block operations: add, list, connect
- Parameter operations: get, set
- Hierarchy: create subsystem
- Bus operations: add element, create selector

#### Infrastructure
- Shared MATLAB engine using `matlab.engine.shareEngine('SimulinkMCP')`
- Automated installation with `install.ps1`
- MATLAB Engine installer with `install_matlab_engine.ps1`
- Startup scripts: `start_matlab.ps1`, `start_mcp_server.ps1`
- Comprehensive documentation (7 markdown files)
- VS Code GitHub Copilot Chat integration

#### Testing
- `test_connection.py` - MATLAB Engine connection validation
- `test_interactive_functions.py` - All 29 Simulink functions validated

---

## Migration Guide

### From Version 1.0 to 2.0

No breaking changes! All existing Simulink functions work identically.

#### New Capabilities to Explore

1. **Execute MATLAB code during Simulink workflows**:
   ```python
   # Old way: Only Simulink operations
   simulink_run_simulation("MyModel", 10.0)
   # Results trapped in MATLAB workspace
   
   # New way: Combine with MATLAB analysis
   simulink_run_simulation("MyModel", 10.0)
   result = matlab_eval_expression("max(out.yout)")
   print(f"Peak value: {result['value']}")
   ```

2. **Store and retrieve analysis results**:
   ```python
   # Calculate in MATLAB
   matlab_set_workspace_variable("threshold", 95)
   
   # Use in Simulink
   threshold = matlab_get_workspace_variable("threshold")
   simulink_set_param("MyModel", "Saturation", "UpperLimit", str(threshold['value']))
   ```

3. **Run custom analysis scripts**:
   ```python
   # Run your existing .m files
   matlab_run_script("E:/Documents/MATLAB/my_analysis.m")
   
   # Get results
   results = matlab_get_workspace_variable("analysis_output")
   ```

#### Recommended Workflow Updates

**Before (Simulink only)**:
```python
simulink_new_model("Test")
simulink_add_block("Test", "simulink/Sources/Sine", "Sine1")
simulink_run_simulation("Test", 10)
# Results stay in MATLAB - no programmatic access
```

**After (Simulink + MATLAB)**:
```python
simulink_new_model("Test")
simulink_add_block("Test", "simulink/Sources/Sine", "Sine1")
simulink_run_simulation("Test", 10)

# Now analyze programmatically
matlab_execute_code("""
out = evalin('base', 'out');
freq = fft(out.yout);
dominant_freq = find(abs(freq) == max(abs(freq)));
fprintf('Dominant frequency: %d Hz\\n', dominant_freq);
""")
```

---

## Roadmap

### Planned for Version 2.1
- [ ] MATLAB figure export (save plots as PNG/PDF)
- [ ] Stateflow integration (query states, transitions)
- [ ] Data logging configuration
- [ ] Model coverage analysis integration

### Planned for Version 3.0
- [ ] Simulink Test integration
- [ ] Requirements Toolbox integration  
- [ ] Code generation support
- [ ] Model comparison and diff

### Community Requests
- [ ] Support for other MATLAB toolboxes (Control, DSP, etc.)
- [ ] Batch simulation with parameter sweeps
- [ ] Model refactoring suggestions
- [ ] Block library management

---

## Contributors

This project integrates patterns from several MATLAB MCP implementations:
- [WilliamCloudQi/matlab-mcp-server](https://github.com/WilliamCloudQi/matlab-mcp-server) - Node.js patterns
- [jigarbhoye04/MatlabMCP](https://github.com/jigarbhoye04/MatlabMCP) - FastMCP Python patterns
- [Tsuchijo/matlab-mcp](https://github.com/Tsuchijo/matlab-mcp) - Script execution patterns

Special thanks to the MCP community for excellent documentation and examples.

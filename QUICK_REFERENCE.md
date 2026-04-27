# Simulink MCP Server - Quick Reference Guide

## � MATLAB Code Execution (NEW!)

### Execute MATLAB Code
```python
# Run code and capture output
matlab_execute_code("disp('Hello!')")
matlab_execute_code("x = magic(5); disp(mean(x(:)))")

# Multi-line analysis
code = """
data = randn(1000, 1);
mu = mean(data);
sigma = std(data);
fprintf('Mean: %.4f, Std: %.4f\\n', mu, sigma);
"""
matlab_execute_code(code)
```

### Workspace Variables
```python
# Set variables
matlab_set_workspace_variable("A", [[1, 2], [3, 4]])
matlab_set_workspace_variable("threshold", 0.95)

# Get variables
result = matlab_get_workspace_variable("A")
# Returns: {'status': 'success', 'value': [[1,2],[3,4]], 'type': 'array'}

# List all variables
matlab_list_workspace_variables()

# Clear specific variables
matlab_clear_workspace(["A", "threshold"])

# Clear all
matlab_clear_workspace()
```

### Evaluate Expressions
```python
# Mathematical expressions
matlab_eval_expression("2^10")        # Returns: 1024.0
matlab_eval_expression("sqrt(144)")   # Returns: 12.0
matlab_eval_expression("pi * 2")      # Returns: 6.283...

# Using workspace variables
matlab_set_workspace_variable("x", 100)
matlab_eval_expression("x * 2 + 50")  # Returns: 250.0
```

### Call MATLAB Functions
```python
# Built-in functions
matlab_call_function("magic", 5, nargout=1)
matlab_call_function("eig", [[1,2],[3,4]], nargout=1)
matlab_call_function("sin", 0.5, nargout=1)

# Custom functions (if in MATLAB path)
matlab_call_function("myCustomFunction", arg1, arg2, nargout=2)
```

### Run Scripts
```python
# Run .m file
matlab_run_script("E:/Documents/MATLAB/my_analysis.m")
matlab_run_script("./scripts/process_data.m")
```

## 🔗 Unified Simulink + MATLAB Workflows

### Workflow: Simulate → Analyze → Modify
```python
# 1. Run Simulink simulation
simulink_run_simulation("MyModel", 10.0)

# 2. Analyze results in MATLAB
matlab_execute_code("""
out = evalin('base', 'out');
max_value = max(out.yout);
mean_value = mean(out.yout);
fprintf('Max: %.4f, Mean: %.4f\\n', max_value, mean_value);
""")

# 3. Use results to modify model
max_val = matlab_get_workspace_variable("max_value")
simulink_set_param("MyModel", "Saturation1", "UpperLimit", str(max_val['value']))

# 4. Re-simulate with new parameters
simulink_run_simulation("MyModel", 10.0)
```

### Workflow: Parametric Model Generation
```python
# 1. Create parameter matrix in MATLAB
matlab_execute_code("""
gains = [1, 2, 5, 10];
save('gains.mat', 'gains');
""")

# 2. Create Simulink model
simulink_new_model("ParametricModel")

# 3. Add blocks with parameters from MATLAB
gains = matlab_get_workspace_variable("gains")
for i, gain in enumerate(gains['value']):
    block_name = f"Gain{i+1}"
    simulink_add_block("ParametricModel", "simulink/Math Operations/Gain", 
                      block_name, [50+i*100, 50, 80+i*100, 80])
    simulink_set_param("ParametricModel", block_name, "Gain", str(gain))
```

## �🎯 Interactive Editing - Most Useful Commands

### "Where am I?" Commands
```
simulink_get_current_model()          → What model am I editing?
simulink_get_current_system()         → What system/subsystem am I in?
simulink_get_current_block()          → What block do I have selected?
simulink_get_selected_blocks()        → What blocks are selected?
```

### "Find things" Commands
```
simulink_find_blocks(model, {'BlockType': 'Gain'})           → Find all Gain blocks
simulink_find_blocks(model, {'Name': 'MyBlock'})             → Find blocks by name
simulink_find_blocks(model, {'BlockType': 'Sum', 'Inputs': '+++'})  → Complex search
simulink_list_blocks(model)                                   → List all blocks
simulink_list_blocks(model, 'Gain')                          → List Gains only
```

### "Modify selection" Commands
```
simulink_delete_block(block_path)                    → Delete current block
simulink_highlight_block(block_path, 'green')        → Highlight block
simulink_get_param(model, block, 'Gain')             → Get parameter
simulink_set_param(model, block, 'Gain', '5')        → Set parameter
```

### "Layout & Cleanup" Commands
```
simulink_arrange_system(system_path)         → Auto-layout blocks
simulink_route_line(line_handle)             → Clean up line routing
```

### "Model Status" Commands
```
simulink_model_is_dirty(model)       → Check for unsaved changes
simulink_model_is_loaded(model)      → Check if model is in memory
```

## 💡 Common Workflows

### Workflow 1: Work with Selected Block
```python
# Ask: "What block is selected and what's its gain value?"
1. current_block = simulink_get_current_block()
   → "mj_gettingStarted/Gain1"

2. model = simulink_get_current_model()
   → "mj_gettingStarted"

3. value = simulink_get_param(model, "Gain1", "Gain")
   → "2.5"

4. simulink_highlight_block(current_block, "green")
   → Visual confirmation
```

### Workflow 2: Find and Modify All Blocks of a Type
```python
# Ask: "Set all Gain blocks to value 10"
1. model = simulink_get_current_model()
2. gains = simulink_find_blocks(model, {'BlockType': 'Gain'})
3. For each gain:
   - simulink_set_param(model, gain_name, "Gain", "10")
   - simulink_highlight_block(gain, "yellow")
```

### Workflow 3: Clean Up Model
```python
# Ask: "Clean up my model layout"
1. system = simulink_get_current_system()
2. simulink_arrange_system(system)
3. Check: simulink_model_is_dirty(model)
4. simulink_save_model(model)
```

### Workflow 4: Add Block Next to Selection
```python
# Ask: "Add a Scope next to the selected block"
1. current = simulink_get_current_block()
2. pos = simulink_get_param(model, current, "Position")
   → Calculate new position offset
3. simulink_add_block(model, "simulink/Sinks/Scope", "Scope1", new_pos)
4. simulink_highlight_block("model/Scope1", "green")
```

## 🚀 VS Code Copilot Integration

### Natural Language Examples - Simulink

**Ask Copilot:**
```
"What model am I working on?"
→ Uses: simulink_get_current_model()

"What block do I have selected?"
→ Uses: simulink_get_current_block()

"Add a Gain block next to my selection"
→ Uses: simulink_get_current_block(), simulink_add_block()

"Find all PID Controller blocks"
→ Uses: simulink_get_current_model(), simulink_find_blocks()

"Arrange the layout of this system"
→ Uses: simulink_get_current_system(), simulink_arrange_system()

"Do I have unsaved changes?"
→ Uses: simulink_get_current_model(), simulink_model_is_dirty()

"Highlight all selected blocks in red"
→ Uses: simulink_get_selected_blocks(), simulink_highlight_block()

"Delete the current block"
→ Uses: simulink_get_current_block(), simulink_delete_block()
```

### Natural Language Examples - MATLAB (NEW!)

**Ask Copilot:**
```
"Create a 10x10 magic square and store it as variable M"
→ Uses: matlab_set_workspace_variable("M", magic(10))

"Calculate the eigenvalues of matrix A"
→ Uses: matlab_call_function("eig", A, nargout=1)

"What variables do I have in my workspace?"
→ Uses: matlab_list_workspace_variables()

"Show me the mean of variable x"
→ Uses: matlab_get_workspace_variable("x"), then calculate mean

"Run my analysis script"
→ Uses: matlab_run_script("path/to/script.m")

"Clear all workspace variables"
→ Uses: matlab_clear_workspace()

"Generate 1000 random numbers and plot histogram"
→ Uses: matlab_execute_code("data = randn(1000,1); histogram(data);")

"What's 2 to the power of 20?"
→ Uses: matlab_eval_expression("2^20")
```

### Natural Language Examples - Unified Workflows (NEW!)

**Ask Copilot:**
```
"Simulate my model and tell me the maximum output value"
→ Uses: simulink_run_simulation() + matlab_eval_expression("max(out.yout)")

"Create a model with gains from 1 to 10"
→ Uses: matlab_execute_code() to create array + simulink_add_block() in loop

"Analyze the FFT of my simulation results"
→ Uses: simulink_run_simulation() + matlab_execute_code("Y = fft(out.yout)")

"Set the saturation limit based on the previous simulation max"
→ Uses: matlab_get_workspace_variable("sim_max") + simulink_set_param()

"Run parameter sweep: simulate with gains [1, 5, 10, 20]"
→ Uses: matlab_set_workspace_variable() + loop with simulink_set_param() + simulink_run_simulation()
```

## 📋 Function Categories & Priorities

### ⭐⭐⭐ Critical (Use Daily) - Interactive Context
- `simulink_get_current_*` functions - Context awareness
- `matlab_execute_code` - Quick MATLAB operations
- `matlab_get/set_workspace_variable` - Data exchange
- `matlab_list_workspace_variables` - See what you have

### ⭐⭐ High Priority (Use Often) - Editing & Analysis
- `simulink_find_blocks` - Search functionality
- `simulink_highlight_block` - Visual feedback
- `simulink_arrange_system` - Layout cleanup
- `simulink_model_is_dirty` - Save status
- `matlab_eval_expression` - Quick calculations
- `matlab_call_function` - MATLAB function access

### ⭐ Medium Priority (Use Regularly) - Advanced
- `simulink_add_block` - Block creation
- `simulink_delete_block` - Block removal
- `simulink_set_param` / `get_param` - Configuration
- `simulink_connect_blocks` - Connections
- `simulink_save_model` - Persistence

### ⭐⭐⭐ Lower Priority (Specialized)
- `simulink_create_subsystem` - Hierarchy
- `simulink_add_bus_element` - Bus operations
- `simulink_replace_block` - Batch operations
- `simulink_expand_subsystem` - Flatten hierarchy

## 🔧 Testing & Debugging

### Test Connection
```bash
cd <path-to>\simulink-mcp-server
.\.venv\Scripts\python.exe test_connection.py
```

### Test Interactive Functions
```bash
cd <path-to>\simulink-mcp-server
.\.venv\Scripts\python.exe test_interactive_functions.py
```

### Check Server Status
1. Open VS Code
2. Press `Ctrl+Shift+P`
3. Select "Reload Window"
4. Open Copilot Chat (`Ctrl+Shift+I`)
5. Check Output panel: View → Output → "GitHub Copilot Chat"

## 🎨 Block Highlighting Colors
```
'red'      - Errors or warnings
'green'    - Success or current selection
'yellow'   - Modified or attention needed
'cyan'     - Information or secondary selection
'magenta'  - Special blocks
'none'     - Remove highlighting
```

## 📊 Model Status Checks

### Before Editing
```python
model = simulink_get_current_model()
if simulink_model_is_loaded(model):
    if simulink_model_is_dirty(model):
        print("⚠️ Model has unsaved changes")
```

### After Editing
```python
# Visual confirmation
simulink_highlight_block(modified_block, "green")

# Check status
if simulink_model_is_dirty(model):
    simulink_save_model(model)
```

## 🐛 Common Issues & Solutions

### Issue: "No model currently open"
**Solution:** Open a Simulink model first, then try again

### Issue: "No block currently selected"
**Solution:** Click on a block in the Simulink Editor to select it

### Issue: Block name has newlines
**Solution:** Parse the output - block name is on the line after "Current block:"

### Issue: "Model has unsaved changes"
**Solution:** Call `simulink_save_model(model)` to save

### Issue: Can't find my model
**Solution:** Make sure the model window is active/focused in MATLAB

## 📈 Performance Tips

1. **Cache model name**: Call `get_current_model()` once, reuse the result
2. **Batch operations**: Group multiple `set_param` calls together
3. **Use handles**: When possible, use block handles instead of paths
4. **Lazy highlighting**: Only highlight when user needs visual feedback
5. **Save periodically**: Use `is_dirty` to prompt for saves

## 🎓 Best Practices

### DO:
✅ Always check current context before operations
✅ Provide visual feedback with highlighting
✅ Check for unsaved changes before major operations
✅ Use meaningful block names
✅ Arrange layout after bulk additions

### DON'T:
❌ Assume a model is open without checking
❌ Modify blocks without user confirmation
❌ Delete blocks without highlighting first
❌ Skip error handling
❌ Forget to save after modifications

---

**Quick Start:**
1. Open a Simulink model in MATLAB
2. Reload VS Code window
3. Ask Copilot: "What model am I editing?"
4. Start building! 🚀

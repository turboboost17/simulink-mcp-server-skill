# Getting Started with Simulink MCP Server

Quick start guide to get up and running in 5 minutes.

## Installation (5 minutes)

### Step 1: Run the Installer (2 minutes)

Open PowerShell in the project directory and run:

```powershell
.\install.ps1
```

This will automatically:
- Check that MATLAB is installed
- Create Python virtual environment
- Install all dependencies
- Configure VS Code settings

**Note:** If you need to install MATLAB Engine as Administrator, the script will give you the exact commands to run.

### Step 2: Start MATLAB with Shared Engine (1 minute)

**Option A: Use the helper script**
```powershell
.\start_matlab.ps1
```

**Option B: Start MATLAB manually**
1. Open MATLAB
2. In the Command Window, run:
```matlab
matlab.engine.shareEngine('SimulinkMCP')
```

You should see: `Shared engine SimulinkMCP started successfully`

**Keep MATLAB running!** The MCP server needs the shared engine to work.

### Step 3: Reload VS Code (1 minute)

1. Press `Ctrl+Shift+P` in VS Code
2. Type "Reload Window" and press Enter
3. Wait for VS Code to reload

### Step 4: Test It! (1 minute)

1. **Open a Simulink model** in MATLAB (or create a new one)
2. **Click on a block** in the model to select it
3. **Open GitHub Copilot Chat** in VS Code (`Ctrl+Shift+I`)
4. **Ask:** "What model am I currently editing?"

You should get a response with your model name! 🎉

## Your First Tasks

### Task 1: Query Your Model

Open a Simulink model and try these questions in Copilot Chat:

```
What model am I currently editing?
```

```
What block do I have selected?
```

```
Find all Gain blocks in this model
```

```
Do I have unsaved changes?
```

### Task 2: Create a Simple Model

Ask Copilot:

```
Create a new Simulink model called "TestModel" with a Constant 
block connected to a Scope
```

Copilot will use the MCP server functions to:
1. Create a new model
2. Add a Constant block
3. Add a Scope block
4. Connect them together

### Task 3: Modify Parameters

Select a Gain block in your model and ask:

```
What is the gain value of my selected block?
```

```
Set the gain value to 10
```

```
Highlight this block in green
```

### Task 4: Layout and Organization

After adding several blocks:

```
Arrange the layout of this model to make it cleaner
```

```
Highlight all Gain blocks in yellow
```

## Common Workflows

### Interactive Editing Workflow

1. **Open model in MATLAB**
2. **Select a block**
3. **Ask Copilot:** "What is this block and what are its parameters?"
4. **Make changes:** "Set the parameter X to value Y"
5. **Visual feedback:** "Highlight this block in green"

### Model Creation Workflow

1. **Ask Copilot:** "Create a new model with [description]"
2. **Copilot creates model structure**
3. **Review in MATLAB**
4. **Ask for adjustments:** "Add a Scope after the Gain block"
5. **Fine-tune:** "Arrange the layout"

### Analysis Workflow

1. **Open existing model**
2. **Ask:** "List all blocks in this model"
3. **Ask:** "Find all PID Controller blocks"
4. **Ask:** "What are the parameters of block X?"
5. **Document:** "Create a summary of this model's structure"

## Troubleshooting

### Problem: "No model currently open"

**Solution:** 
- Open a Simulink model in MATLAB
- Make sure the model window is active (click on it)
- Try the query again

### Problem: "Shared engine not found"

**Solution:**
```matlab
% In MATLAB Command Window:
matlab.engine.shareEngine('SimulinkMCP')

% Verify:
matlab.engine.find_matlab()
% Should show 'SimulinkMCP' in the list
```

### Problem: Duplicate or hidden MATLAB shared engines

The MATLAB Engine API can report shared sessions such as `MATLAB_<pid>` in
addition to `SimulinkMCP`. These extra sessions may be headless MATLAB processes
started by VS Code, Python, or another agent, and they may not appear as visible
MATLAB desktop windows.

**Solution:**
1. Check shared engine names from this workspace:
   ```powershell
   .\.venv\Scripts\python.exe -c "import matlab.engine; print(matlab.engine.find_matlab())"
   ```
2. If more than `SimulinkMCP` appears, check the process IDs before stopping
   anything. Only stop the extra MATLAB process if you are sure it is not the
   intended shared engine.
3. Re-check that `SimulinkMCP` still responds:
   ```powershell
   .\.venv\Scripts\python.exe -c "import matlab.engine; eng=matlab.engine.connect_matlab('SimulinkMCP'); print(eng.eval('1+1', nargout=1))"
   ```

### Problem: Copilot doesn't recognize MCP server

**Solution:**
1. Check that `.vscode/mcp.json` exists and has the correct configuration
	- If you are using Copilot-specific config, also check `.vscode/settings.json`
2. Reload VS Code window: `Ctrl+Shift+P` → "Reload Window"
3. Check Output panel: View → Output → "GitHub Copilot Chat"

### Problem: "Connection failed"

**Solution:**
1. Ensure MATLAB is running
2. Verify shared engine is active: `matlab.engine.find_matlab()`
3. Run diagnostics: `.\.venv\Scripts\python.exe test_connection.py`

## Tips for Success

### 1. Keep MATLAB Running
The MCP server connects to MATLAB's shared engine. If you close MATLAB, the connection is lost.

### 2. Use Natural Language
Don't overthink it! Ask questions naturally:
- ✅ "What's the gain value of the selected block?"
- ✅ "Add a Scope after this Gain block"
- ✅ "Clean up the layout of this subsystem"

### 3. Be Specific About Context
The server knows your current context:
- "my selected block" → Uses `gcb` to get current selection
- "this model" → Uses `bdroot` to get active model
- "this subsystem" → Uses `gcs` to get current system

### 4. Visual Feedback is Your Friend
Use highlighting to confirm operations:
- "Highlight the blocks you found in yellow"
- "Show me which block you modified in green"

### 5. Check Model Status
Before saving or major changes:
- "Do I have unsaved changes?"
- "Is the model loaded?"

## Next Steps

### Learn More

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands and workflows
- **[FUNCTION_ADDITIONS.md](FUNCTION_ADDITIONS.md)** - Complete function documentation
- **[INSTALL.md](INSTALL.md)** - Detailed installation guide

### Try Advanced Features

```
Create a subsystem from blocks X, Y, and Z

Replace all Gain blocks with PID Controllers

Find all blocks with parameter 'SampleTime' set to 0.1

Create a bus selector for signals A, B, and C
```

### Customize

- Add the shared engine command to your MATLAB `startup.m`
- Create keyboard shortcuts in VS Code for common queries
- Experiment with complex natural language requests

## Support

If you run into issues:

1. **Check diagnostics:** `.\.venv\Scripts\python.exe test_connection.py`
2. **Review logs:** VS Code → View → Output → "GitHub Copilot Chat"
3. **Verify setup:** Make sure all installation steps completed successfully
4. **Test manually:** Try running test scripts to isolate the issue

---

**You're ready to go!** 🚀 Start asking Copilot about your Simulink models and watch the magic happen.

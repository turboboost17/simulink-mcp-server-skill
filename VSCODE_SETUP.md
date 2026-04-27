# VS Code Setup (Simulink MCP Server)

This repo ships MCP config templates you can copy into *any* other VS Code workspace.

## Recommended: `.vscode/mcp.json`

1. Copy [config/mcp.json.example](config/mcp.json.example) into your project as `.vscode/mcp.json`.
2. Replace:
   - `<PATH_TO_PYTHON_EXE>` with the Python interpreter that has this package installed (usually this repo’s `.venv\\Scripts\\python.exe`).
   - `<ABSOLUTE_PATH_TO_simulink-mcp-server>` with the path to this repo.
3. Reload VS Code (`Ctrl+Shift+P` → "Reload Window").

Notes:
- `SIMULINK_MCP_LOG_LEVEL` defaults to `WARNING` to keep VS Code from showing noisy stderr warnings.
- `SIMULINK_MCP_MODE` controls which tools are registered: `readonly`, `open`, or `full`.
- Use [config/mcp.readonly.json.example](config/mcp.readonly.json.example) for Ask/review agents and [config/mcp.full.json.example](config/mcp.full.json.example) for trusted editing agents.
- `PYTHONPATH` is intentionally not required; `uv sync --no-prune` installs the package so `python -m simulink_mcp_server.mcp_server` works.
   - `--no-prune` avoids uninstalling the manually-installed MATLAB Engine package.

## Optional: Copilot-specific settings

If you’re using a Copilot workflow that expects `github.copilot.chat.mcpServers`, copy
[config/copilot.settings.json.example](config/copilot.settings.json.example)
into your project’s `.vscode/settings.json` and fill in the placeholders.

## Troubleshooting

- If the server doesn’t connect: start MATLAB and run `matlab.engine.shareEngine('SimulinkMCP')`.
- If you want more logs: set `SIMULINK_MCP_LOG_LEVEL=INFO`.

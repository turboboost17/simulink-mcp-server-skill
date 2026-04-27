# Copilot Instructions - Simulink MCP Server

## Repository Context

This repository contains a local Model Context Protocol server for MATLAB and
Simulink. The server exposes Simulink model inspection/editing tools and MATLAB
execution tools through a shared MATLAB Engine session named `SimulinkMCP`.

## Architecture

- `src/simulink_mcp_server/server.py`: MATLAB Engine connection management and
  MATLAB/Simulink operation implementations.
- `src/simulink_mcp_server/mcp_server.py`: MCP stdio server, tool schemas, mode
  filtering, and tool dispatch.
- `config/`: example MCP client configurations.
- `docs/`: enterprise deployment, release, and Simulink tool-gap references.

## Implementation Rules

- Keep MCP protocol output on stdout only. Logs must go to stderr.
- Use `evalc()` when capturing MATLAB command-window output.
- Tool handlers must return `list[TextContent]` for MCP SDK 1.17+.
- Sanitize MATLAB identifiers, paths, and parameter names before interpolating
  them into MATLAB code. Values that are not identifiers should be quoted or
  escaped for their specific context.
- Prefer dedicated tools for frequent, safe, well-parameterized Simulink actions.
  Use `matlab_execute_code` for exploratory or complex MATLAB logic.
- Preserve `SIMULINK_MCP_MODE` behavior when adding tools. Decide whether each
  new tool belongs in `readonly`, `open`, or only `full` mode.

## Testing

- Unit tests in `tests/` must not require MATLAB unless marked with
  `@pytest.mark.integration`.
- Integration tests may require MATLAB, Simulink, and a shared engine session.
- Do not commit local `.venv`, `.vscode`, saved MathWorks HTML exports, logs, or
  generated MATLAB build artifacts.
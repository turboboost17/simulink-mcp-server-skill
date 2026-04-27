---
applyTo: "**"
---
# Simulink MCP Server Development Instructions

Use this guidance when changing the MCP server, docs, tests, or release files.

## Tool Exposure Modes

The server supports `SIMULINK_MCP_MODE`:

- `readonly`: inspection tools only.
- `open`: inspection tools plus model loading and editor highlighting.
- `full`: all tools, including MATLAB code execution and model mutation.

When adding a tool, update the mode allowlists in
`src/simulink_mcp_server/mcp_server.py`, docs, and tests.

## MATLAB Execution Safety

- Capture MATLAB output with `evalc()`.
- Keep logs on stderr; stdout is reserved for MCP JSON-RPC.
- Use timeouts or async execution for simulation, build, test, network, and SSH
  workflows.
- Avoid broad string interpolation into MATLAB code. Escape or sanitize every
  user-provided value according to whether it is an identifier, path, or literal.

## Release Hygiene

- Keep release instructions generic. Do not include private paths, hostnames,
  IP addresses, user names, license-server names, or proprietary model names.
- Do not commit saved MathWorks documentation HTML or asset folders.
- Keep `config/*.example` files as placeholders that users can copy into their
  own workspaces.
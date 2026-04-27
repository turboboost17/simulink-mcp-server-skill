# Enterprise Deployment

This guide is for organizations that review MCP servers before allowing them in
an internal registry or shared developer image.

## Recommended Review Summary

- Transport: local MCP stdio server.
- Network listener: none.
- Main external runtime: local MATLAB Engine for Python connecting to a local
  MATLAB session.
- Full-mode capability: local MATLAB code execution and Simulink model editing
  with the current user's permissions.
- Restriction control: `SIMULINK_MCP_MODE` filters exposed MCP tools.

## MCP Modes

Set `SIMULINK_MCP_MODE` in the MCP server environment:

| Mode | Intended Use | Exposes |
|---|---|---|
| `readonly` | Ask/review agents, model inventory, audits | Context, search, list, get-param, status, workspace reads, code check, toolbox detection |
| `open` | Review agents that may open models for inspection | `readonly` plus model load/open and editor highlighting |
| `full` | Trusted local development agents | All tools, including MATLAB code execution, model edits, save, simulation, async execution |

## Non-UV Install Path

Use standard Python tooling when UV is not approved:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install .
```

Install MATLAB Engine for Python from the local MATLAB installation using the
instructions for your MATLAB release. A common Windows flow is:

```powershell
cd "C:\Program Files\MATLAB\R2025a\extern\engines\python"
<repo>\.venv\Scripts\python.exe -m pip install .
```

If your MATLAB release still documents `setup.py install`, follow the MathWorks
instructions for that release.

## Locked Requirements

For a public release, generate a locked requirements file from a reviewed lock
source and store it with the release artifact:

```powershell
uv export --format requirements-txt --no-dev --output-file requirements.lock.txt
```

If UV is not allowed in the target environment, generate this file in a separate
reviewed build environment, then install from it with pip:

```powershell
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps .
```

## Offline Wheelhouse

Build or download wheels in a connected, reviewed environment:

```powershell
py -3.12 -m venv .build-venv
.\.build-venv\Scripts\python.exe -m pip install --upgrade pip build
.\.build-venv\Scripts\python.exe -m pip wheel --wheel-dir wheelhouse .
.\.build-venv\Scripts\python.exe -m build
```

Install on the target machine without internet access:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --find-links wheelhouse simulink-mcp-server
```

The MATLAB Engine package is normally installed from the local MATLAB tree and
is not redistributed in the wheelhouse.

## Internal MCP Registry Template

Use [registry/simulink-mcp-server.template.json](../registry/simulink-mcp-server.template.json)
as a starting point for an internal registry entry. Maintain separate entries or
profiles for `readonly`, `open`, and `full` if your registry supports policy
scoping by agent mode.
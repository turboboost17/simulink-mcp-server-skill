# Security Policy

## Supported Versions

Security fixes are provided for the latest released version of this project.
Pre-release branches and local forks should be reviewed by the organization
that deploys them.

## Security Model

This MCP server runs locally and connects to a local MATLAB session through the
MATLAB Engine for Python. In full mode it can execute MATLAB code, load and
save Simulink models, modify block parameters, run simulations, and call MATLAB
functions with the same file-system and network permissions as the user running
MATLAB.

That capability is intentional. Treat this server like a local development tool
that can run code, not like a read-only documentation service.

## Main Risks

- Prompt injection: model content, script output, comments, or documentation can
  contain instructions that try to influence an AI client into calling write or
  execution tools.
- Trusted-client boundary: only register this server with MCP clients and agent
  modes that your organization trusts to call local tools.
- Local data access: MATLAB code can read local files and environment variables
  according to the current user's permissions.
- Model mutation: full mode can change and save Simulink models.

## Agent Skill Imports

This repo includes adapted plaintext skills from the MathWorks MATLAB and
Simulink Agentic Toolkits under `.agents/skills/`. Upstream setup, plugin
delivery, bug-reporting, eval-fixture, and nonlocal tool implementation files
are not included. The imported skills are guidance only; execution behavior
comes from the MCP tools an agent chooses to call.

Do not add `.p` files or upstream tool implementation binaries to this
repository to satisfy skill references. If an upstream composite tool is useful,
implement a source-visible local replacement and cover it with tests and
`SIMULINK_MCP_MODE` classification.

## Deployment Controls

Use `SIMULINK_MCP_MODE` to reduce the exposed tool surface:

- `readonly`: exposes inspection tools only.
- `open`: exposes inspection tools plus model loading and editor highlighting.
- `full`: exposes all tools, including MATLAB code execution and model edits.

For Ask-only or review-only agent modes, prefer `SIMULINK_MCP_MODE=readonly`.
For trusted local development workflows, use `SIMULINK_MCP_MODE=full`.

VS Code and other MCP clients may also ask before allowing filesystem access
outside the current workspace. Keep those client-side approval prompts enabled
unless your organization has an equivalent policy control.

## Reporting Vulnerabilities

Please report security issues privately through the repository owner's preferred
security contact or private vulnerability reporting channel. Do not include
proprietary models, logs, license files, hostnames, usernames, or network paths
in public issues.
---
name: mcp-server-command-management
description: "Use when: adding, removing, reviewing, or scoping Simulink/MATLAB MCP tools; deciding whether a Simulink API should be a dedicated tool; updating tool coverage, MCP modes, or decision records."
argument-hint: "Describe the Simulink or MATLAB capability you want to expose or review"
---

# MCP Server Command Management

## Add A Dedicated Tool When

Add a tool when the operation is frequent, has a small stable parameter set,
benefits from validation or sanitization, and returns a useful result for an AI
client. Prefer dedicated tools for common Simulink operations such as model
navigation, parameter reads, block edits, layout, and simulation control.

Use `matlab_execute_code` when the operation is exploratory, one-off, multi-step,
or relies on internal APIs that may vary by MATLAB release.

## Mode Placement

Every tool must be assigned to one of these exposure levels:

- `readonly`: no model mutation, no arbitrary MATLAB evaluation, no save.
- `open`: readonly plus opening/loading models and visual editor highlighting.
- `full`: model edits, simulation, save, workspace writes, arbitrary MATLAB code,
  scripts, async execution, cancellation, and function calls.

Update the allowlists in `src/simulink_mcp_server/mcp_server.py` and the mode
tests whenever a tool is added or reclassified.

## Common Gotchas

- Do not force a `model/block` target when MATLAB also supports model-level
  parameters.
- Do not assume `get_param` results are strings. They can be structs, cells,
  numbers, handles, or objects.
- Sanitize identifiers and paths, but do not treat arbitrary values as MATLAB
  identifiers.
- Use async or timeouts for simulations, builds, tests, network calls, and any
  operation that can block MATLAB for a long time.
- For masked library blocks, read user-visible mask values from the outer masked
  subsystem unless you intentionally need implementation details.
- MATLAB Engine startup can expose lifecycle bugs that unit tests miss: a
  generated `MATLAB_<pid>` shared session may be a separate hidden MATLAB
  process, and `shareEngine('SimulinkMCP')` can fail even when the newly started
  engine is usable. Regression tests should mock named-engine connection
  failures, preferred-name sharing failures, idempotent reconnects, and safe
  disconnect behavior for externally managed engines.

## Coverage References

- Tool gaps: `docs/SIMULINK_FUNCTION_GAPS.md`
- Enterprise deployment modes: `docs/ENTERPRISE_DEPLOYMENT.md`
- Release process: `docs/RELEASE_PROCESS.md`

## Decision Records

For significant tool additions, removals, or mode changes, add a short decision
record under `.github/skills/mcp-server-command-management/decisions/` with:

- Context
- Decision
- Mode classification
- MATLAB APIs affected
- Files changed
- Verification
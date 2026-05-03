# MATLAB Agentic Toolkit Skill Import

## Context

The MathWorks MATLAB Agentic Toolkit provides plaintext skills for MATLAB
testing, debugging, review, modernization, app building, Live Script authoring,
product installation/listing, and Database Toolbox workflows. This server
already exposes MATLAB MCP tools that cover the toolkit's core execution and
inspection needs under local names.

## Decision

Import the non-setup MATLAB workflow skills into `.agents/skills/` and adapt
their manifests to this server's local tool names. Do not import the upstream
setup skill, plugin marketplace files, agent-specific setup templates, or eval
fixtures.

## Mode Classification

No MCP tools were added or reclassified. Existing mode behavior remains:

- `matlab_check_code` and `matlab_detect_toolboxes` are readonly.
- `matlab_run_script`, `matlab_run_tests`, and `matlab_execute_code` remain full.

## MATLAB APIs Affected

No server APIs were changed. The imported skills reference existing APIs and
tool patterns such as `checkcode`, `codeIssues`, `runtests`, `ver`, `uifigure`,
`matlab.unittest`, and Database Toolbox functions.

## Files Changed

- `.agents/skills/`
- `.agents/skills/TOOL_COMPATIBILITY.md`
- `docs/MATHWORKS_MATLAB_AGENTIC_TOOLKIT_REVIEW.md`
- `docs/SIMULINK_FUNCTION_GAPS.md`
- `FUNCTION_ADDITIONS.md`
- `README.md`
- `FILE_STRUCTURE.md`
- `SECURITY.md`
- `THIRD_PARTY_NOTICES.md`
- `tests/test_agent_skills.py`

## Verification

- Unit tests verify expected skills, excluded setup/reporting skills, absence of
  `.p` files and upstream eval fixtures, and local-only manifest tool names.
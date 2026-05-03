# MathWorks Agentic Toolkit Skill Import

## Context

MathWorks published the Simulink Agentic Toolkit with plaintext skills and six
broad MCP tool concepts. The desired outcome was to reuse the useful
Model-Based Design skills while keeping this MCP server source-visible and
reviewable.

## Decision

Import and adapt six plaintext domain skills into `.agents/skills/`. Do not
import the upstream bug-report skill, setup skill, `tools/tools.json`, or any
`.p` files.

## Mode Classification

No new MCP tools were added. The imported skills use existing tools and inherit
the existing `SIMULINK_MCP_MODE` policy:

- read-only skills can run under `readonly` when they only inspect models;
- build, simulation, test, requirement, and MATLAB execution workflows require
  `full` for mutation or arbitrary MATLAB execution.

## MATLAB APIs Affected

No server-side MATLAB APIs were added. The skills may guide agents toward
existing local tools such as `simulink_get_param`, `simulink_find_blocks`,
`simulink_add_block`, `simulink_connect_blocks`, `matlab_execute_code`, and
`matlab_run_tests`.

## Files Changed

- `.agents/skills/`
- `docs/MATHWORKS_AGENTIC_TOOLKIT_REVIEW.md`
- `docs/SIMULINK_FUNCTION_GAPS.md`
- `FUNCTION_ADDITIONS.md`
- `THIRD_PARTY_NOTICES.md`
- `SECURITY.md`
- `tests/test_agent_skills.py`

## Verification

Run `pytest tests/test_agent_skills.py tests/test_mcp_modes.py`.

---
name: simulink-tool-self-evaluation
description: "Use when: evaluating Simulink MCP tool coverage against available Simulink programmatic APIs, selecting the next tool candidates, or updating the local function-gap markdown without redistributing MathWorks HTML assets."
argument-hint: "Describe the tool coverage or Simulink API area to evaluate"
---

# Simulink Tool Self Evaluation

## Purpose

Use this skill to improve tool coverage without committing local MathWorks HTML
exports. The canonical public reference for missing candidates is
`docs/SIMULINK_FUNCTION_GAPS.md`.

## Workflow

1. Count currently registered MCP tools in `src/simulink_mcp_server/mcp_server.py`.
2. Review `docs/SIMULINK_FUNCTION_GAPS.md` for unimplemented candidates.
3. Pick a candidate only if it is frequent, safe to parameterize, discoverability
   improves for agents, and output can be made useful.
4. Classify the candidate as `readonly`, `open`, or `full`.
5. Add or update tests that do not require MATLAB unless the test is marked
   `integration`.
6. Update the gap markdown and add a decision record for meaningful tool changes.

## Public Documentation Rule

Do not commit saved MathWorks documentation pages, generated asset folders, CSS,
JavaScript, screenshots, or copied prose. For public references, use function
names, project-authored notes, and links to official MathWorks documentation.
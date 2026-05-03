---
name: building-simulink-models
description: Builds and edits Simulink, System Composer, Stateflow, and Simscape models. Use when modifying model structure, parameters, ports, connections, or Stateflow chart internals.
license: MathWorks BSD-3-Clause
metadata:
  version: "1.1"
---

# Building Models

This copy is adapted for `simulink-mcp-server`. Use the local source-visible tools listed in `../TOOL_COMPATIBILITY.md`; do not call external MathWorks Agentic Toolkit composite tools (`model_edit`, `model_read`, etc.) unless the user has explicitly configured them separately.

Use dedicated local tools for common Simulink edits: `simulink_add_block`, `simulink_connect_blocks`, `simulink_set_param`, `simulink_delete_block`, `simulink_create_subsystem`, and `simulink_arrange_system`. Use `matlab_execute_code` for Stateflow, System Composer, Simscape, or other APIs not yet exposed as dedicated tools.

## When to Use

- Adding, connecting, deleting, or replacing blocks in a model
- Configuring block parameters, signal properties, or model settings
- Creating or editing Stateflow chart internals (states, transitions, junctions)
- Building System Composer architecture models
- Wiring Simscape physical connections

## When NOT to Use

- Querying parameter values -> use `simulink_get_param`
- Resolving variable references to numeric values -> use `matlab_eval_expression` for simple expressions or `matlab_execute_code` for workspace/model-workspace/data-dictionary logic

## Workflow

1. **Read first:** Use `simulink_get_current_model`, `simulink_list_blocks`, `simulink_find_blocks`, and targeted `simulink_get_param` calls to understand the existing topology.
2. **Plan the data flow:** For complex edits, sketch inputs → operations → outputs, then map to blocks.
3. **Edit:** Use local structural tools one subsystem level at a time.
4. **Verify:** Re-read the affected scope with `simulink_list_blocks`, `simulink_find_blocks`, and parameter checks before saving.

**CRITICAL:** After a failed or partial edit, inspect the affected subsystem immediately before attempting corrective action.

## Operation Chaining with `ref`

Use `ref` to name a block and `#ref` to reference it in later operations within the same call:

```json
[{"op": "add_block", "type": "Gain", "name": "MyGain", "ref": "g1"},
 {"op": "connect", "target": "blk_5.y1 -> #g1.u1"}]
```

The response `created` map shows `ref → blk_id`. In subsequent calls, use the `blk_id` (e.g., `blk_42`) — `#ref` only works within a single call.

## Guardrails

- **Avoid manually reconstructing block paths** from displayed names. Block names can contain invisible newlines and trailing whitespace that cause `hilite_system`, `open_system`, and `get_param` to fail. Prefer tool-returned full paths, handles, or `Simulink.ID` resolution when available:
  ```matlab
  % blk_42 → use the number after "blk_" as the SID
  blockPath = Simulink.ID.getFullName('<ModelName>:42');
  hilite_system(blockPath)
  open_system(blockPath)
  get_param(blockPath, 'BlockType')
  ```
- Use `simulink_arrange_system` after structural edits when layout should be cleaned up.
- Use meaningfully named variables (e.g., `Kp_SpeedController`) instead of hardcoded numeric values. Define variables in model workspace or a `.m` init script.
- Prefer dedicated local tools for simple edits. Use `matlab_execute_code` only when no dedicated local tool exists, and keep code scoped, sanitized, and reviewable.
- Use `open_system` rather than `load_system` to open models that are not already open, or when creating new models, unless the user explicitly asks otherwise or the model is a library. This ensures the user can see live edits as they happen.

## Naming Conventions

Prefer code-generation-safe names for blocks, signals, and variables:

- Use only: `a-z`, `A-Z`, `0-9`, underscore (`_`)
- Don't start with a number
- Don't use leading/trailing or consecutive underscores
- Prefer names under 32 characters (required for some code generation targets)

## Block Types

Use the block's **display name** in the `type` field. Do not construct or guess library paths.

- **Built-in Simulink blocks:** Use the BlockType directly: `Gain`, `Sum`, `Constant`, `Integrator`, `SubSystem`, `Scope`
- **Library blocks (Simscape, Aerospace, DSP, Communications, etc.):** Use the display name as it appears in the Simulink Library Browser: `Voltage Source`, `Resistor`, `DC Motor`, `Solver Configuration`, `6DOF (Euler Angles)`
- If `simulink_add_block` fails with an invalid type, fall back to the full library path from MATLAB documentation (e.g., `ee_lib/Sources/Voltage Source`)

```json
[{"op": "add_block", "type": "Voltage Source", "name": "V1", "ref": "v1"},
 {"op": "add_block", "type": "Resistor", "name": "R1", "ref": "r1"},
 {"op": "add_block", "type": "Electrical Reference", "name": "Gnd", "ref": "gnd"},
 {"op": "add_block", "type": "Solver Configuration", "name": "Solver", "ref": "sc"}]
```

## Domain-Specific Rules

When working with these domains, read the corresponding reference file before editing:

- **Stateflow charts** -> `reference/stateflow.md` — local tools can add Chart blocks, but chart internals require `matlab_execute_code` with the Stateflow API. The reference covers API gotchas, subcharts, lint checks, and layout.
- **System Composer architecture models** -> `reference/system-composer.md` — create models with `systemcomposer.createModel`, then use local edit tools or `matlab_execute_code` as needed. Components use `type: "SubSystem"`, ports use Bus Element blocks. The reference covers component creation, port wiring, and behavior model generation.
- **Simscape physical models** -> `reference/simscape.md` — Physical connections use bidirectional `<->` syntax. The reference covers connection semantics, port patterns, and initial target variables.

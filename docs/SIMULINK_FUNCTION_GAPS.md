# Simulink Function Gaps

This file replaces local saved MathWorks documentation exports for public work.
It intentionally lists only project-authored notes and unimplemented function
names. Do not commit saved MathWorks HTML pages or asset folders.

Current implemented MCP tools: 43, as registered in
`src/simulink_mcp_server/mcp_server.py`.

## MathWorks Simulink Agentic Toolkit Comparison Gaps

The MathWorks Simulink Agentic Toolkit describes several composite model tools.
The adapted `.agents/skills` catalog maps their concepts onto current local
tools where possible, and tracks source-visible replacements here.

| Upstream Tool | Candidate Value | Suggested Mode |
|---|---|---|
| `model_overview` | High-level hierarchy/interface summary that composes current model context, block listing, and connection metadata into one agent-friendly response. | readonly |
| `model_read` | Structured graph read with stable block IDs, topology, expressions, connections, and parameter summaries. | readonly |
| `model_query_params` | Batch query for block, signal, and model configuration parameters, including optional compiled values. | readonly |
| `model_resolve_params` | Resolve model/workspace/data-dictionary variable references used by block parameters. | readonly |
| `model_edit` | Transactional multi-operation edit tool with add/connect/configure/delete/replace operations, partial-failure reporting, and layout handling. | full |
| `model_test` | Source-visible model test runner for persistent pass/fail Simulink tests, preferably layered over MATLAB Unit Test and Simulink Test APIs. | full |

## MathWorks MATLAB Agentic Toolkit Comparison Gaps

The MathWorks MATLAB Agentic Toolkit maps closely to existing local MATLAB tools,
but a few source-visible improvements would make the imported skills more
efficient and structured.

| Upstream Capability | Candidate Value | Suggested Mode |
|---|---|---|
| `matlab_coding_guidelines` resource | Local MCP resource or readonly tool that returns project coding guidance plus MATLAB review conventions. | readonly |
| `plain_text_live_code_guidelines` resource | Local MCP resource or readonly tool for plain-text Live Script authoring rules. | readonly |
| Structured `check_matlab_code` output | Return parsed `checkcode -struct` diagnostics with file, line, column, severity, and message fields instead of only command-window text. | readonly |
| Structured `run_matlab_test_file` output | Return parsed `matlab.unittest` pass/fail/error counts and diagnostics from `runtests`. | full |
| Structured `detect_matlab_toolboxes` output | Return MATLAB release and toolbox list as structured JSON rather than raw `ver` output. | readonly |
| Installed product/support-package listing | Dedicated readonly tool for MATLAB installation product inventory, including support-package roots. | readonly |

## Unimplemented Programmatic Modeling Candidates

| Function or API | Candidate Value | Suggested Mode |
|---|---|---|
| `gcbp` | Return a block path object for the selected block when string paths are ambiguous. | readonly |
| `getCallbackAnnotation` | Inspect callback annotation context. | readonly |
| `getCurrentAnnotation` | Inspect selected annotation context. | readonly |
| `getfullname` | Resolve handles to full paths. | readonly |
| `getSimulinkBlockHandle` | Resolve a block path to a numeric handle. | readonly |
| `Simulink.findBlocks` | Object-based block search for newer MATLAB releases. | readonly |
| `Simulink.findBlocksOfType` | Stronger type-specific block search. | readonly |
| `Simulink.FindOptions` | Expose reusable search options for advanced find workflows. | readonly |
| `Simulink.allBlockDiagrams` | List loaded models and libraries. | readonly |
| `modelfinder` | Search installed examples or model projects. | readonly |
| `Simulink.MDLInfo` | Inspect model metadata without loading the model. | readonly |
| `Simulink.MDLInfo.getDescription` | Read a model description without loading the model. | readonly |
| `Simulink.MDLInfo.getMetadata` | Read model metadata without loading the model. | readonly |
| `open_system` | Open a model, subsystem, dialog, or block in the editor. | open |
| `close_system` | Close model windows or dialogs. | full |
| `bdclose` | Close block diagrams. | full |
| `addterms` | Add terminators to unconnected ports during cleanup. | full |
| `Simulink.BlockDiagram.deleteContents` | Clear contents of a model or subsystem. | full |
| `Simulink.SubSystem.deleteContents` | Clear subsystem contents. | full |
| `add_line` | Low-level line creation when `simulink_connect_blocks` is too constrained. | full |
| `add_param` | Add custom model parameters. | full |
| `delete_param` | Remove custom model parameters. | full |
| `docblock` | Read or update model documentation blocks. | open/full |
| `Simulink.BlockDiagram.resizeBlocksToFitContent` | Improve visual layout after automated edits. | full |
| `bdIsSubsystem` | Check whether a path is a subsystem. | readonly |
| `Simulink.SubSystem.copyContentsToBlockDiagram` | Promote subsystem contents into a model. | full |
| `bdIsLibrary` | Identify whether a loaded diagram is a library. | readonly |
| `isSimulinkStarted` | Check Simulink runtime availability. | readonly |
| `slIsFileChangedOnDisk` | Detect model file changes since load. | readonly |
| `edittime.getDisplayIssues` | Inspect design-time issues for model review. | readonly |

## Simulation And Build Candidates

| Function or API | Candidate Value | Suggested Mode |
|---|---|---|
| `slbuild` | Dedicated long-running build tool with async result handling. | full |
| `rtwbuild` | Legacy or explicit code generation build entrypoint. | full |
| `Simulink.SimulationInput` | Parameterized simulations without mutating base model settings. | full |
| `Simulink.SimulationOutput` | Structured simulation result extraction. | readonly/full |
| `parsim` | Batch or parallel simulation orchestration. | full |
| `batchsim` | Batch simulation orchestration. | full |

## Target And Deployment Candidates

| Function or API | Candidate Value | Suggested Mode |
|---|---|---|
| `codertarget.data.getParameterValue` | Read target configuration in a structured way. | readonly |
| `codertarget.data.setParameterValue` | Update target configuration with validation. | full |
| `ros2device` | Query or connect to a configured ROS 2 target. | open/full |

## Maintenance Notes

- Keep this list to function names and original project notes.
- Remove candidates when they become implemented tools.
- Add a decision record for meaningful tool additions or mode changes.
# Local Tool Compatibility

These skills were adapted from MathWorks Agentic Toolkit plaintext skills. Use
this server's source-visible MCP tools when an upstream skill or reference uses
a different MCP tool name.

## Simulink Agentic Toolkit

The Simulink toolkit describes several broad model tools. This server exposes
smaller explicit Simulink and MATLAB tools instead:

| Upstream name | Local replacement pattern |
|---|---|
| `evaluate_matlab_code` | `matlab_execute_code` |
| `model_overview` | `simulink_get_current_model`, `simulink_list_blocks`, `simulink_find_blocks`, and targeted `simulink_get_param` calls |
| `model_read` | `simulink_list_blocks`, `simulink_find_blocks`, `simulink_get_param`, and `matlab_execute_code` for structured Simulink API queries |
| `model_query_params` | `simulink_get_param`; use `matlab_execute_code` when querying multiple parameters or compiled values |
| `model_resolve_params` | `matlab_eval_expression` for simple expressions; `matlab_execute_code` for workspace, model workspace, or data-dictionary resolution |
| `model_edit` | `simulink_add_block`, `simulink_connect_blocks`, `simulink_set_param`, `simulink_delete_block`, `simulink_create_subsystem`, `simulink_arrange_system`, and `matlab_execute_code` for APIs not exposed as dedicated tools |
| `model_test` | `matlab_run_tests` for MATLAB test files, or `matlab_execute_code` with Simulink Test APIs when Simulink Test is installed |

## MATLAB Agentic Toolkit

The MATLAB toolkit is written for the MathWorks MATLAB MCP Core Server. This
server provides equivalent capabilities under local names:

| Upstream name | Local replacement pattern |
|---|---|
| `evaluate_matlab_code` | `matlab_execute_code` |
| `run_matlab_file` | `matlab_run_script` |
| `run_matlab_test_file` | `matlab_run_tests` |
| `check_matlab_code` | `matlab_check_code` |
| `detect_matlab_toolboxes` | `matlab_detect_toolboxes` |
| `matlab_coding_guidelines` resource | Use applicable repo instructions, nearby source conventions, `matlab_check_code`, and MATLAB `checkcode` or `codeIssues` output |
| `plain_text_live_code_guidelines` resource | Use `matlab-create-live-script` guidance in this catalog |

When a reference template still uses an upstream name as a concept, translate it
through these tables before calling tools.

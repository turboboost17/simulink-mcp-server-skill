import asyncio

from simulink_mcp_server.mcp_server import handle_call_tool, handle_list_tools


def _listed_tool_names() -> set[str]:
    return {tool.name for tool in asyncio.run(handle_list_tools())}


def test_default_mode_exposes_all_tools(monkeypatch) -> None:
    monkeypatch.delenv("SIMULINK_MCP_MODE", raising=False)

    names = _listed_tool_names()

    assert len(names) == 43
    assert "matlab_execute_code" in names
    assert "simulink_set_param" in names


def test_readonly_mode_filters_mutating_tools(monkeypatch) -> None:
    monkeypatch.setenv("SIMULINK_MCP_MODE", "readonly")

    names = _listed_tool_names()

    assert "simulink_get_current_model" in names
    assert "simulink_get_param" in names
    assert "matlab_detect_toolboxes" in names
    assert "simulink_set_param" not in names
    assert "simulink_save_model" not in names
    assert "matlab_execute_code" not in names


def test_open_mode_allows_load_and_highlight(monkeypatch) -> None:
    monkeypatch.setenv("SIMULINK_MCP_MODE", "open")

    names = _listed_tool_names()
    assert "simulink_load_model" in names
    assert "simulink_highlight_block" in names
    assert "simulink_save_model" not in names
    assert "matlab_run_script" not in names


def test_disallowed_tool_call_is_blocked_before_execution(monkeypatch) -> None:
    monkeypatch.setenv("SIMULINK_MCP_MODE", "readonly")

    result = asyncio.run(
        handle_call_tool("matlab_execute_code", {"code": "disp('hello')"})
    )

    assert len(result) == 1
    assert "not available" in result[0].text
    assert "readonly" in result[0].text


def test_invalid_mode_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("SIMULINK_MCP_MODE", "unexpected")

    names = _listed_tool_names()

    assert "simulink_get_param" in names
    assert "matlab_execute_code" not in names

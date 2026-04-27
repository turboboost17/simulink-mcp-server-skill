"""Basic pytest tests for Simulink MCP Server functionality.

These tests intentionally avoid requiring MATLAB to be running; they only
validate that the Python surface area imports cleanly.
"""


def test_imports() -> None:
    from simulink_mcp_server.server import (
        MATLABEngineManager,
        connect_simulink_engine,
        simulink_add_block,
        simulink_new_model,
    )

    assert MATLABEngineManager is not None
    assert callable(connect_simulink_engine)
    assert callable(simulink_new_model)
    assert callable(simulink_add_block)


def test_engine_manager_initializes() -> None:
    from simulink_mcp_server.server import MATLABEngineManager

    manager = MATLABEngineManager()
    assert manager is not None

    available = manager.ensure_matlab_engine_installed()
    assert isinstance(available, bool)


def test_function_availability() -> None:
    from simulink_mcp_server.server import (
        connect_simulink_engine,
        simulink_add_block,
        simulink_add_bus_element,
        simulink_connect_blocks,
        simulink_create_bus_selector,
        simulink_create_subsystem,
        simulink_get_param,
        simulink_list_blocks,
        simulink_load_model,
        simulink_new_model,
        simulink_run_simulation,
        simulink_save_model,
        simulink_set_param,
    )

    assert callable(connect_simulink_engine)
    assert callable(simulink_new_model)
    assert callable(simulink_add_block)
    assert callable(simulink_connect_blocks)
    assert callable(simulink_get_param)
    assert callable(simulink_set_param)
    assert callable(simulink_create_subsystem)
    assert callable(simulink_save_model)
    assert callable(simulink_load_model)
    assert callable(simulink_run_simulation)
    assert callable(simulink_add_bus_element)
    assert callable(simulink_create_bus_selector)
    assert callable(simulink_list_blocks)

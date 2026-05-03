"""Basic pytest tests for Simulink MCP Server functionality.

These tests intentionally avoid requiring MATLAB to be running; they only
validate that the Python surface area imports cleanly.
"""

import sys
import types


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


def test_engine_connect_is_idempotent(monkeypatch) -> None:
    from simulink_mcp_server.server import MATLABEngineManager

    manager = MATLABEngineManager()
    manager.engine = object()
    manager.is_connected = True

    def fail_if_called() -> bool:
        raise AssertionError("already-connected manager should not reconnect")

    monkeypatch.setattr(manager, "ensure_matlab_engine_installed", fail_if_called)

    assert manager.connect() is True


def test_engine_connect_keeps_started_engine_when_share_name_fails(monkeypatch) -> None:
    from simulink_mcp_server.server import MATLABEngineManager

    class FakeEngineError(Exception):
        pass

    class FakeShareNamespace:
        def shareEngine(self, engine_name: str, nargout: int = 0) -> None:
            raise RuntimeError("current MATLAB session is shared already")

    class FakeMatlabNamespace:
        def __init__(self) -> None:
            self.engine = FakeShareNamespace()

    class FakeEngine:
        def __init__(self) -> None:
            self.matlab = FakeMatlabNamespace()

        def evalc(self, code: str) -> str:
            return ""

    fake_engine = FakeEngine()
    fake_matlab_module = types.ModuleType("matlab")
    fake_engine_module = types.ModuleType("matlab.engine")
    fake_engine_module.EngineError = FakeEngineError
    fake_engine_module.TimeoutError = TimeoutError

    def connect_matlab(engine_name: str) -> FakeEngine:
        raise FakeEngineError(f"{engine_name} not found")

    def start_matlab() -> FakeEngine:
        return fake_engine

    fake_engine_module.connect_matlab = connect_matlab
    fake_engine_module.start_matlab = start_matlab
    fake_matlab_module.engine = fake_engine_module

    monkeypatch.setitem(sys.modules, "matlab", fake_matlab_module)
    monkeypatch.setitem(sys.modules, "matlab.engine", fake_engine_module)

    manager = MATLABEngineManager()
    monkeypatch.setattr(manager, "ensure_matlab_engine_installed", lambda: True)

    assert manager.connect() is True
    assert manager.engine is fake_engine
    assert manager.is_connected is True
    assert manager._started_engine is True


def test_disconnect_does_not_quit_external_shared_engine() -> None:
    from simulink_mcp_server.server import MATLABEngineManager

    class FakeSharedEngine:
        def __init__(self) -> None:
            self.quit_called = False

        def quit(self) -> None:
            self.quit_called = True

    fake_engine = FakeSharedEngine()
    manager = MATLABEngineManager()
    manager.engine = fake_engine
    manager.is_connected = True
    manager._started_engine = False

    manager.disconnect()

    assert fake_engine.quit_called is False
    assert manager.engine is None
    assert manager.is_connected is False


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

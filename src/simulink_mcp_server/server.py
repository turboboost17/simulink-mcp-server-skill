"""
Simulink MCP Server

A Model Context Protocol server that provides VS Code agents with MATLAB Simulink 
functionality through a shared MATLAB engine connection using matlab.engine.shareEngine.
"""

import asyncio
import os
import sys
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, List, Union
import tempfile
import json
import logging

# Configure logging (MCP uses stdout for protocol; keep logs on stderr)
# VS Code surfaces server stderr as warnings, so default to WARNING.
_log_level_name = os.getenv("SIMULINK_MCP_LOG_LEVEL", "WARNING").upper()
_log_level = getattr(logging, _log_level_name, logging.WARNING)
logging.basicConfig(level=_log_level, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Get MATLAB path from environment variable
MATLAB_PATH = os.getenv('MATLAB_PATH', 'C:/Program Files/MATLAB/R2025a')

import re

# Try to import matlab.engine.TimeoutError for FutureResult timeout handling.
# Falls back to Python's built-in TimeoutError if matlab.engine isn't installed.
try:
    import matlab.engine
    _MatlabTimeoutError = matlab.engine.TimeoutError
except (ImportError, AttributeError):
    _MatlabTimeoutError = TimeoutError

def _sanitize_matlab_identifier(name: str) -> str:
    """Sanitize a string to be a valid MATLAB identifier/path component.
    
    Prevents code injection via model names, block names, parameters, etc.
    Allows: alphanumeric, underscore, forward slash (for paths), space, dot, hyphen.
    """
    if not name or not isinstance(name, str):
        raise ValueError(f"Invalid identifier: {name!r}")
    # Allow MATLAB-safe characters: word chars, /, space, dot, hyphen
    if not re.match(r'^[\w\s./\-]+$', name):
        raise ValueError(
            f"Identifier contains disallowed characters: {name!r}. "
            "Only alphanumeric, underscore, space, dot, hyphen, and / are allowed."
        )
    # Block single quotes which could escape MATLAB strings
    if "'" in name:
        raise ValueError(f"Identifier must not contain single quotes: {name!r}")
    return name

# Default timeout for MATLAB engine calls (seconds). 0 = no timeout.
DEFAULT_MATLAB_TIMEOUT = int(os.getenv("MATLAB_TIMEOUT", "30"))

class MATLABEngineManager:
    """Manages shared MATLAB engine connection with error handling and reconnection."""
    
    def __init__(self):
        self.engine = None
        self.shared_engine_name = "SimulinkMCP"  # Use the specific engine name you defined
        self.is_connected = False
        self.matlab_available = False
        # Async task tracking
        self._active_future = None  # (task_id, future, code_snippet, start_time)
        self._future_lock = threading.Lock()
        self._completed_tasks: Dict[str, Dict] = {}  # task_id -> result
        # Performance monitoring
        self._perf_log: List[Dict] = []  # recent execution timings
        
    def ensure_matlab_engine_installed(self):
        """Ensure MATLAB Engine for Python is installed."""
        try:
            import matlab.engine
            # Test if we can access the engine module (don't connect yet)
            self.matlab_available = True
            return True
        except ImportError:
            logger.info("MATLAB Engine not found, will use command-line execution")
            self.matlab_available = False
            return False
    
    def connect(self) -> bool:
        """Connect to shared MATLAB engine or create new one.
        
        This is intentionally synchronous — matlab.engine calls are blocking
        and this must be callable from both sync and async contexts.
        """
        if not self.ensure_matlab_engine_installed():
            logger.warning("MATLAB Engine not available, will use command-line fallback")
            return False
            
        try:
            import matlab.engine
            
            # Try to connect to existing shared engine with your specific name
            try:
                logger.info(f"Attempting to connect to shared engine: {self.shared_engine_name}")
                self.engine = matlab.engine.connect_matlab(self.shared_engine_name)
                logger.info(f"Connected to existing shared MATLAB engine: {self.shared_engine_name}")
            except matlab.engine.EngineError as e:
                logger.info(f"Shared engine '{self.shared_engine_name}' not found: {e}")
                # Create new shared engine with your specific name
                logger.info(f"Creating new shared MATLAB engine: {self.shared_engine_name}")
                self.engine = matlab.engine.start_matlab()
                # Share the engine with your specific name
                self.engine.matlab.engine.shareEngine(self.shared_engine_name, nargout=0)
                logger.info(f"Created and shared MATLAB engine: {self.shared_engine_name}")
            
            # Verify Simulink is available
            try:
                # Use evalc to avoid printing to stdout (stdout is reserved for MCP JSON-RPC)
                _ = self.engine.evalc("ver('Simulink')")
                logger.info("Simulink toolbox verified")
            except Exception as e:
                logger.warning(f"Simulink verification failed: {e}")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MATLAB engine: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from MATLAB engine."""
        if self.engine and self.is_connected:
            try:
                self.engine.quit()
                logger.info("Disconnected from MATLAB engine")
            except Exception as e:
                logger.error(f"Error disconnecting from MATLAB engine: {e}")
            finally:
                self.engine = None
                self.is_connected = False
    
    def execute_matlab_code(self, code: str, capture_output: bool = True,
                            timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute MATLAB code and return results.
        
        Args:
            code: MATLAB code to execute
            capture_output: Whether to capture and return output
            timeout: Seconds to wait before cancelling. None = DEFAULT_MATLAB_TIMEOUT, 0 = no timeout.
        """
        if timeout is None:
            timeout = DEFAULT_MATLAB_TIMEOUT
        
        result = {
            "success": False,
            "output": "",
            "error": "",
            "figures": [],
            "workspace_vars": {},
            "elapsed_ms": 0
        }
        
        start_time = time.monotonic()
        code_preview = code.strip()[:80].replace('\n', ' ')
        
        if self.matlab_available and self.is_connected and self.engine:
            # Use MATLAB Engine with timeout via background=True + FutureResult
            try:
                # IMPORTANT: MCP uses stdout for protocol messages.
                # Use evalc to capture any command-window output as a string.
                if timeout > 0:
                    # Use background=True so we can enforce a timeout
                    future = self.engine.evalc(code, nargout=1, background=True)
                    try:
                        output = future.result(timeout=float(timeout))
                    except (TimeoutError, _MatlabTimeoutError):
                        future.cancel()
                        elapsed = (time.monotonic() - start_time) * 1000
                        result["error"] = (
                            f"MATLAB execution timed out after {timeout}s. "
                            f"Code: {code_preview}..."
                        )
                        result["elapsed_ms"] = round(elapsed)
                        self._log_perf(code_preview, elapsed, timed_out=True)
                        logger.warning(f"Timeout ({timeout}s): {code_preview}")
                        return result
                else:
                    # No timeout — blocking call
                    output = self.engine.evalc(code)
                
                if capture_output:
                    result["output"] = (output or "").strip()
                result["success"] = True
            except Exception as e:
                result["error"] = str(e)
        else:
            # Fallback to command-line execution
            try:
                # Create temporary MATLAB script
                with tempfile.NamedTemporaryFile(mode='w', suffix='.m', delete=False) as f:
                    f.write(code)
                    script_path = f.name
                
                # Execute MATLAB command
                matlab_exe = os.path.join(MATLAB_PATH, 'bin', 'matlab.exe')
                cmd = [matlab_exe, '-batch', f"run('{script_path.replace(os.sep, '/')}'); exit;"]
                
                cli_timeout = timeout if timeout > 0 else 60
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=cli_timeout
                )
                
                result["output"] = process.stdout
                if process.stderr:
                    result["error"] = process.stderr
                result["success"] = process.returncode == 0
                
                # Clean up
                os.unlink(script_path)
                
            except subprocess.TimeoutExpired:
                result["error"] = f"MATLAB execution timed out after {cli_timeout}s"
            except Exception as e:
                result["error"] = str(e)
        
        elapsed = (time.monotonic() - start_time) * 1000
        result["elapsed_ms"] = round(elapsed)
        self._log_perf(code_preview, elapsed, timed_out=False)
        
        if elapsed > 5000:
            logger.warning(f"Slow MATLAB call ({elapsed:.0f}ms): {code_preview}")
        
        return result
    
    def execute_matlab_code_async(self, code: str) -> str:
        """Start async MATLAB execution, return a task_id for polling.
        
        The MATLAB engine is single-threaded, so only one async task
        can run at a time. Returns immediately with a task_id.
        """
        if not self.engine or not self.is_connected:
            raise RuntimeError("MATLAB engine not connected")
        
        with self._future_lock:
            if self._active_future is not None:
                _, existing_future, _, _ = self._active_future
                if not existing_future.done():
                    raise RuntimeError(
                        "Another async task is already running. "
                        "Cancel it first or wait for completion."
                    )
        
        task_id = str(uuid.uuid4())
        future = self.engine.evalc(code, nargout=1, background=True)
        code_preview = code.strip()[:80].replace('\n', ' ')
        
        with self._future_lock:
            self._active_future = (task_id, future, code_preview, time.monotonic())
        
        logger.info(f"Async task started: {task_id} — {code_preview}")
        return task_id
    
    def check_task(self, task_id: str) -> Dict[str, Any]:
        """Poll async task status. Returns dict with status/output/error."""
        # Check completed tasks cache first
        if task_id in self._completed_tasks:
            return self._completed_tasks[task_id]
        
        with self._future_lock:
            if self._active_future and self._active_future[0] == task_id:
                _, future, code_preview, start_time = self._active_future
                elapsed = (time.monotonic() - start_time) * 1000
                
                if future.done():
                    try:
                        output = future.result()
                        result = {
                            "status": "completed",
                            "output": (output or "").strip(),
                            "elapsed_ms": round(elapsed)
                        }
                    except Exception as e:
                        result = {
                            "status": "failed",
                            "error": str(e),
                            "elapsed_ms": round(elapsed)
                        }
                    self._completed_tasks[task_id] = result
                    self._active_future = None
                    self._log_perf(code_preview, elapsed, timed_out=False)
                    return result
                else:
                    return {
                        "status": "working",
                        "elapsed_ms": round(elapsed),
                        "code_preview": code_preview
                    }
        
        return {"status": "not_found", "error": f"Task {task_id} not found"}
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running async task."""
        with self._future_lock:
            if self._active_future and self._active_future[0] == task_id:
                _, future, code_preview, start_time = self._active_future
                cancelled = future.cancel()
                if cancelled:
                    elapsed = (time.monotonic() - start_time) * 1000
                    self._completed_tasks[task_id] = {
                        "status": "cancelled",
                        "elapsed_ms": round(elapsed)
                    }
                    self._active_future = None
                    logger.info(f"Cancelled task {task_id}: {code_preview}")
                return cancelled
        return False
    
    def _log_perf(self, code_preview: str, elapsed_ms: float, timed_out: bool):
        """Log performance data for a MATLAB execution."""
        entry = {
            "timestamp": time.time(),
            "code": code_preview,
            "elapsed_ms": round(elapsed_ms),
            "timed_out": timed_out
        }
        self._perf_log.append(entry)
        # Keep last 100 entries
        if len(self._perf_log) > 100:
            self._perf_log = self._perf_log[-100:]
        logger.debug(f"MATLAB perf: {elapsed_ms:.0f}ms {'TIMEOUT' if timed_out else 'OK'} — {code_preview}")
    
    def get_perf_summary(self) -> Dict[str, Any]:
        """Return performance summary of recent MATLAB executions."""
        if not self._perf_log:
            return {"total_calls": 0}
        
        times = [e["elapsed_ms"] for e in self._perf_log]
        timeouts = sum(1 for e in self._perf_log if e["timed_out"])
        slow = [e for e in self._perf_log if e["elapsed_ms"] > 5000]
        
        return {
            "total_calls": len(self._perf_log),
            "avg_ms": round(sum(times) / len(times)),
            "max_ms": max(times),
            "min_ms": min(times),
            "timeouts": timeouts,
            "slow_calls_gt5s": len(slow),
            "slow_details": [{"code": e["code"], "ms": e["elapsed_ms"]} for e in slow[-5:]]
        }

# Global engine manager
engine_manager = MATLABEngineManager()

# Simulink tool functions
def connect_simulink_engine() -> str:
    """Connect to shared MATLAB engine for Simulink operations."""
    try:
        logger.info("Starting connection attempt to Simulink engine...")
        success = engine_manager.connect()
        
        if success:
            logger.info(f"Successfully connected to shared MATLAB engine: {engine_manager.shared_engine_name}")
            return f"Successfully connected to shared MATLAB engine '{engine_manager.shared_engine_name}' with Simulink support"
        else:
            logger.warning("Failed to connect to MATLAB engine, using command-line fallback")
            return "Using command-line MATLAB execution (MATLAB Engine not available)"
    except Exception as e:
        logger.error(f"Error during engine connection: {str(e)}")
        return f"Error connecting to MATLAB engine: {str(e)}"

def simulink_new_model(model_name: str) -> str:
    """Create a new Simulink model."""
    try:
        model_name = _sanitize_matlab_identifier(model_name)
        code = f"""
        new_system('{model_name}');
        open_system('{model_name}');
        disp('Model created successfully');
        """
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully created new Simulink model: {model_name}"
        else:
            return f"Failed to create model: {result['error']}"
    except Exception as e:
        return f"Error creating Simulink model: {str(e)}"

def simulink_add_block(model_name: str, block_type: str, block_name: str, position: Optional[List[int]] = None) -> str:
    """Add a block to a Simulink model."""
    try:
        model_name = _sanitize_matlab_identifier(model_name)
        block_name = _sanitize_matlab_identifier(block_name)
        # block_type uses library paths like 'simulink/Sources/Constant'
        block_type = _sanitize_matlab_identifier(block_type)
        if position:
            pos_str = f"'Position', [{position[0]}, {position[1]}, {position[2]}, {position[3]}]"
        else:
            pos_str = ""
        
        code = f"""
        add_block('{block_type}', '{model_name}/{block_name}'{', ' + pos_str if pos_str else ''});
        disp('Block added successfully');
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully added block '{block_name}' of type '{block_type}' to model '{model_name}'"
        else:
            return f"Failed to add block: {result['error']}"
    except Exception as e:
        return f"Error adding block: {str(e)}"

def simulink_connect_blocks(model_name: str, source_block: str, source_port: int, dest_block: str, dest_port: int) -> str:
    """Connect two blocks in a Simulink model."""
    try:
        model_name = _sanitize_matlab_identifier(model_name)
        source_block = _sanitize_matlab_identifier(source_block)
        dest_block = _sanitize_matlab_identifier(dest_block)
        code = f"""
        add_line('{model_name}', '{source_block}/{source_port}', '{dest_block}/{dest_port}');
        disp('Blocks connected successfully');
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully connected {source_block}:{source_port} to {dest_block}:{dest_port}"
        else:
            return f"Failed to connect blocks: {result['error']}"
    except Exception as e:
        return f"Error connecting blocks: {str(e)}"

def simulink_get_param(model_name: str, block_name: str, parameter: str) -> str:
    """Get a parameter value from a Simulink block or model.
    
    If block_name is empty, gets a model-level parameter.
    """
    try:
        model_name = _sanitize_matlab_identifier(model_name)
        parameter = _sanitize_matlab_identifier(parameter)
        if block_name:
            block_name = _sanitize_matlab_identifier(block_name)
            target = f"{model_name}/{block_name}"
        else:
            target = model_name
        code = f"""
        param_value = get_param('{target}', '{parameter}');
        if isstruct(param_value)
            disp(evalc('disp(param_value)'));
        else
            disp(['Parameter value: ', char(string(param_value))]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Parameter '{parameter}' value: {result['output']}"
        else:
            return f"Failed to get parameter: {result['error']}"
    except Exception as e:
        return f"Error getting parameter: {str(e)}"

def simulink_set_param(model_name: str, block_name: str, parameter: str, value: str) -> str:
    """Set a parameter value for a Simulink block or model.
    
    If block_name is empty, sets a model-level parameter.
    """
    try:
        model_name = _sanitize_matlab_identifier(model_name)
        parameter = _sanitize_matlab_identifier(parameter)
        if block_name:
            block_name = _sanitize_matlab_identifier(block_name)
            target = f"{model_name}/{block_name}"
        else:
            target = model_name
        # Value is deliberately NOT sanitized as an identifier - it can be numeric, etc.
        # But escape single quotes to prevent MATLAB string breakout
        value = value.replace("'", "''")
        code = f"""
        set_param('{target}', '{parameter}', '{value}');
        disp('Parameter set successfully');
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully set parameter '{parameter}' to '{value}' for '{target}'"
        else:
            return f"Failed to set parameter: {result['error']}"
    except Exception as e:
        return f"Error setting parameter: {str(e)}"

def simulink_create_subsystem(model_name: str, blocks: List[str], subsystem_name: str) -> str:
    """Create a subsystem from selected blocks."""
    try:
        # Format block list for MATLAB
        block_list = "', '".join([f"{model_name}/{block}" for block in blocks])
        
        code = f"""
        selected_blocks = {{'{block_list}'}};
        Simulink.BlockDiagram.createSubsystem(selected_blocks, 'Name', '{subsystem_name}');
        disp('Subsystem created successfully');
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully created subsystem '{subsystem_name}' from blocks: {', '.join(blocks)}"
        else:
            return f"Failed to create subsystem: {result['error']}"
    except Exception as e:
        return f"Error creating subsystem: {str(e)}"

def simulink_save_model(model_name: str, file_path: Optional[str] = None) -> str:
    """Save a Simulink model to file."""
    try:
        if file_path:
            code = f"save_system('{model_name}', '{file_path}'); disp('Model saved successfully');"
        else:
            code = f"save_system('{model_name}'); disp('Model saved successfully');"
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            save_location = file_path or f"{model_name}.slx"
            return f"Successfully saved model '{model_name}' to '{save_location}'"
        else:
            return f"Failed to save model: {result['error']}"
    except Exception as e:
        return f"Error saving model: {str(e)}"

def simulink_load_model(file_path: str) -> str:
    """Load a Simulink model from file."""
    try:
        code = f"""
        model_name = load_system('{file_path}');
        open_system(model_name);
        disp(['Loaded model: ', char(model_name)]);
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully loaded model from '{file_path}': {result['output']}"
        else:
            return f"Failed to load model: {result['error']}"
    except Exception as e:
        return f"Error loading model: {str(e)}"

def simulink_run_simulation(model_name: str, stop_time: Optional[float] = None) -> str:
    """Run simulation for a Simulink model."""
    try:
        if stop_time:
            code = f"""
            set_param('{model_name}', 'StopTime', '{stop_time}');
            sim('{model_name}');
            disp('Simulation completed successfully');
            """
        else:
            code = f"""
            sim('{model_name}');
            disp('Simulation completed successfully');
            """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully ran simulation for model '{model_name}': {result['output']}"
        else:
            return f"Failed to run simulation: {result['error']}"
    except Exception as e:
        return f"Error running simulation: {str(e)}"

def simulink_add_bus_element(model_name: str, bus_object_name: str, element_name: str, data_type: str = "double", dimensions: str = "1") -> str:
    """Add an element to a Simulink Bus object."""
    try:
        code = f"""
        % Create or get bus object
        if ~exist('{bus_object_name}', 'var')
            {bus_object_name} = Simulink.Bus;
        end
        
        % Create new element
        element = Simulink.BusElement;
        element.Name = '{element_name}';
        element.DataType = '{data_type}';
        element.Dimensions = {dimensions};
        
        % Add element to bus
        {bus_object_name}.Elements(end+1) = element;
        
        % Save to base workspace
        assignin('base', '{bus_object_name}', {bus_object_name});
        disp('Bus element added successfully');
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully added element '{element_name}' to bus '{bus_object_name}'"
        else:
            return f"Failed to add bus element: {result['error']}"
    except Exception as e:
        return f"Error adding bus element: {str(e)}"

def simulink_create_bus_selector(model_name: str, bus_signal_block: str, selected_signals: List[str], selector_name: str) -> str:
    """Create a Bus Selector block and configure it."""
    try:
        # Format signal list for MATLAB
        signal_list = "', '".join(selected_signals)
        
        code = f"""
        % Add Bus Selector block
        add_block('simulink/Signal Routing/Bus Selector', '{model_name}/{selector_name}');
        
        % Configure selected signals
        set_param('{model_name}/{selector_name}', 'OutputSignals', '{signal_list}');
        
        % Connect to bus signal source
        add_line('{model_name}', '{bus_signal_block}/1', '{selector_name}/1');
        
        disp('Bus Selector created and configured successfully');
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully created Bus Selector '{selector_name}' with signals: {', '.join(selected_signals)}"
        else:
            return f"Failed to create Bus Selector: {result['error']}"
    except Exception as e:
        return f"Error creating Bus Selector: {str(e)}"

def simulink_list_blocks(model_name: str, block_type: Optional[str] = None) -> str:
    """List all blocks in a Simulink model, optionally filtered by type."""
    try:
        if block_type:
            code = f"""
            blocks = find_system('{model_name}', 'BlockType', '{block_type}');
            for i = 1:length(blocks)
                disp(blocks{{i}});
            end
            """
        else:
            code = f"""
            blocks = find_system('{model_name}', 'Type', 'block');
            for i = 1:length(blocks)
                disp(blocks{{i}});
            end
            """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Blocks in model '{model_name}':\n{result['output']}"
        else:
            return f"Failed to list blocks: {result['error']}"
    except Exception as e:
        return f"Error listing blocks: {str(e)}"

# ============================================================================
# INTERACTIVE CONTEXT FUNCTIONS - Get current user context in Simulink Editor
# ============================================================================

def simulink_get_current_model() -> str:
    """Get the top-level model name of the currently active Simulink system.
    Uses bdroot to get the root model."""
    try:
        code = """
        current_model = bdroot;
        if isempty(current_model)
            disp('No model currently open or active');
        else
            disp(['Current model: ', current_model]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return result['output'].strip()
        else:
            return f"Failed to get current model: {result['error']}"
    except Exception as e:
        return f"Error getting current model: {str(e)}"

def simulink_get_current_block() -> str:
    """Get the path of the currently selected block in Simulink.
    Uses gcb (get current block)."""
    try:
        code = """
        current_block = gcb;
        if isempty(current_block)
            disp('No block currently selected');
        else
            disp(['Current block: ', current_block]);
            % Also get block type for context
            try
                block_type = get_param(current_block, 'BlockType');
                disp(['Block type: ', block_type]);
            catch
                disp('Block type: Unknown');
            end
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return result['output'].strip()
        else:
            return f"Failed to get current block: {result['error']}"
    except Exception as e:
        return f"Error getting current block: {str(e)}"

def simulink_get_current_block_handle() -> str:
    """Get the handle of the currently selected block.
    Uses gcbh (get current block handle)."""
    try:
        code = """
        block_handle = gcbh;
        if block_handle == 0 || block_handle == -1
            disp('No block currently selected');
        else
            disp(['Block handle: ', num2str(block_handle)]);
            % Get block path for context
            try
                block_path = getfullname(block_handle);
                disp(['Block path: ', block_path]);
            catch
                disp('Block path: Unknown');
            end
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return result['output'].strip()
        else:
            return f"Failed to get current block handle: {result['error']}"
    except Exception as e:
        return f"Error getting current block handle: {str(e)}"

def simulink_get_current_system() -> str:
    """Get the path of the currently active Simulink system/subsystem.
    Uses gcs (get current system)."""
    try:
        code = """
        current_system = gcs;
        if isempty(current_system)
            disp('No system currently active');
        else
            disp(['Current system: ', current_system]);
            % Check if it's a subsystem
            try
                if bdIsSubsystem(current_system)
                    disp('Type: Subsystem');
                else
                    disp('Type: Top-level model');
                end
            catch
                disp('Type: Unknown');
            end
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return result['output'].strip()
        else:
            return f"Failed to get current system: {result['error']}"
    except Exception as e:
        return f"Error getting current system: {str(e)}"

def simulink_get_selected_blocks() -> str:
    """Get all currently selected blocks in the active Simulink window.
    Uses find_system with 'Selected' parameter."""
    try:
        code = """
        current_system = gcs;
        if isempty(current_system)
            disp('No system currently active');
        else
            selected = find_system(current_system, 'SearchDepth', 1, 'Selected', 'on');
            if isempty(selected)
                disp('No blocks currently selected');
            else
                disp(['Number of selected blocks: ', num2str(length(selected))]);
                for i = 1:length(selected)
                    try
                        block_type = get_param(selected{i}, 'BlockType');
                        disp(['  ', selected{i}, ' (', block_type, ')']);
                    catch
                        disp(['  ', selected{i}]);
                    end
                end
            end
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return result['output'].strip()
        else:
            return f"Failed to get selected blocks: {result['error']}"
    except Exception as e:
        return f"Error getting selected blocks: {str(e)}"

def simulink_find_blocks(model_name: str, criteria: Dict[str, str]) -> str:
    """Find blocks in a model matching specific criteria.
    Uses Simulink.findBlocks with flexible search criteria.
    
    Args:
        model_name: Name of the model to search
        criteria: Dictionary of search criteria (e.g., {'BlockType': 'Gain', 'Name': 'MyBlock'})
    """
    try:
        # Build MATLAB struct for criteria
        criteria_str = ", ".join([f"'{k}', '{v}'" for k, v in criteria.items()])
        
        code = f"""
        try
            blocks = Simulink.findBlocks('{model_name}', {criteria_str});
            if isempty(blocks)
                disp('No blocks found matching criteria');
            else
                disp(['Found ', num2str(length(blocks)), ' block(s):']);
                for i = 1:length(blocks)
                    block_path = getfullname(blocks(i));
                    disp(['  ', block_path]);
                end
            end
        catch ME
            disp(['Error: ', ME.message]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return result['output'].strip()
        else:
            return f"Failed to find blocks: {result['error']}"
    except Exception as e:
        return f"Error finding blocks: {str(e)}"

# ============================================================================
# ENHANCED EDITING FUNCTIONS - More powerful model manipulation
# ============================================================================

def simulink_delete_block(block_path: str) -> str:
    """Delete a block from a Simulink model.
    Uses delete_block."""
    try:
        block_path = _sanitize_matlab_identifier(block_path)
        code = f"""
        try
            delete_block('{block_path}');
            disp('Block deleted successfully');
        catch ME
            disp(['Error: ', ME.message]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully deleted block: {block_path}"
        else:
            return f"Failed to delete block: {result['error']}"
    except Exception as e:
        return f"Error deleting block: {str(e)}"

def simulink_delete_line(model_name: str, source_block: str, source_port: int, dest_block: str, dest_port: int) -> str:
    """Delete a line connection between two blocks.
    Uses delete_line."""
    try:
        code = f"""
        try
            delete_line('{model_name}', '{source_block}/{source_port}', '{dest_block}/{dest_port}');
            disp('Line deleted successfully');
        catch ME
            disp(['Error: ', ME.message]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully deleted line from {source_block}:{source_port} to {dest_block}:{dest_port}"
        else:
            return f"Failed to delete line: {result['error']}"
    except Exception as e:
        return f"Error deleting line: {str(e)}"

def simulink_replace_block(model_name: str, old_block_type: str, new_block_type: str, replace_name: bool = False) -> str:
    """Replace all blocks of one type with another type in a model.
    Uses replace_block."""
    try:
        name_param = "'noprompt'" if replace_name else ""
        code = f"""
        try
            num_replaced = replace_block('{model_name}', 'BlockType', '{old_block_type}', '{new_block_type}', {name_param});
            disp(['Replaced ', num2str(num_replaced), ' block(s)']);
        catch ME
            disp(['Error: ', ME.message]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Block replacement result: {result['output']}"
        else:
            return f"Failed to replace blocks: {result['error']}"
    except Exception as e:
        return f"Error replacing blocks: {str(e)}"

def simulink_highlight_block(block_path: str, color: str = "red") -> str:
    """Highlight a block in the Simulink editor for visual feedback.
    Uses hilite_system."""
    try:
        block_path = _sanitize_matlab_identifier(block_path)
        if color not in ('red', 'green', 'yellow', 'cyan', 'magenta', 'none'):
            color = 'red'
        code = f"""
        try
            hilite_system('{block_path}', '{color}');
            disp('Block highlighted successfully');
        catch ME
            disp(['Error: ', ME.message]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully highlighted block: {block_path} with color: {color}"
        else:
            return f"Failed to highlight block: {result['error']}"
    except Exception as e:
        return f"Error highlighting block: {str(e)}"

def simulink_arrange_system(system_path: str) -> str:
    """Automatically arrange and layout blocks in a system for better readability.
    Uses Simulink.BlockDiagram.arrangeSystem."""
    try:
        code = f"""
        try
            Simulink.BlockDiagram.arrangeSystem('{system_path}');
            disp('System arranged successfully');
        catch ME
            disp(['Error: ', ME.message]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully arranged system: {system_path}"
        else:
            return f"Failed to arrange system: {result['error']}"
    except Exception as e:
        return f"Error arranging system: {str(e)}"

def simulink_route_line(line_handle: int) -> str:
    """Automatically route a line for cleaner appearance.
    Uses Simulink.BlockDiagram.routeLine."""
    try:
        code = f"""
        try
            Simulink.BlockDiagram.routeLine({line_handle});
            disp('Line routed successfully');
        catch ME
            disp(['Error: ', ME.message]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully routed line with handle: {line_handle}"
        else:
            return f"Failed to route line: {result['error']}"
    except Exception as e:
        return f"Error routing line: {str(e)}"

def simulink_expand_subsystem(subsystem_path: str) -> str:
    """Replace a subsystem with its contents (flatten hierarchy).
    Uses Simulink.BlockDiagram.expandSubsystem."""
    try:
        code = f"""
        try
            Simulink.BlockDiagram.expandSubsystem('{subsystem_path}');
            disp('Subsystem expanded successfully');
        catch ME
            disp(['Error: ', ME.message]);
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return f"Successfully expanded subsystem: {subsystem_path}"
        else:
            return f"Failed to expand subsystem: {result['error']}"
    except Exception as e:
        return f"Error expanding subsystem: {str(e)}"

def simulink_model_is_loaded(model_name: str) -> str:
    """Check if a model is currently loaded in memory.
    Uses bdIsLoaded."""
    try:
        code = f"""
        if bdIsLoaded('{model_name}')
            disp('Model is loaded');
        else
            disp('Model is not loaded');
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return result['output'].strip()
        else:
            return f"Failed to check if model is loaded: {result['error']}"
    except Exception as e:
        return f"Error checking model status: {str(e)}"

def simulink_model_is_dirty(model_name: str) -> str:
    """Check if a model has unsaved changes.
    Uses bdIsDirty."""
    try:
        code = f"""
        if bdIsDirty('{model_name}')
            disp('Model has unsaved changes');
        else
            disp('Model has no unsaved changes');
        end
        """
        
        result = engine_manager.execute_matlab_code(code)
        
        if result["success"]:
            return result['output'].strip()
        else:
            return f"Failed to check model dirty status: {result['error']}"
    except Exception as e:
        return f"Error checking model dirty status: {str(e)}"

# ========================================
# General MATLAB Code Execution Functions
# ========================================

def matlab_execute_code(code: str, capture_output: bool = True,
                        timeout: Optional[int] = None) -> Dict[str, Any]:
    """Execute arbitrary MATLAB code and return results.
    
    Args:
        code: MATLAB code string to execute
        capture_output: Whether to capture and return output
        timeout: Seconds to wait. None=default (30s), 0=no timeout.
        
    Returns:
        Dictionary with status, output, error, and elapsed_ms fields
    """
    if timeout is None:
        timeout = DEFAULT_MATLAB_TIMEOUT
    
    try:
        if not engine_manager.engine or not engine_manager.is_connected:
            return {
                "status": "error",
                "error": "MATLAB engine not connected"
            }
        
        code_preview = code.strip()[:80].replace('\n', ' ')
        start_time = time.monotonic()
        
        if capture_output:
            try:
                if timeout > 0:
                    future = engine_manager.engine.evalc(code, nargout=1, background=True)
                    try:
                        output = future.result(timeout=float(timeout))
                    except (TimeoutError, _MatlabTimeoutError):
                        future.cancel()
                        elapsed = (time.monotonic() - start_time) * 1000
                        engine_manager._log_perf(code_preview, elapsed, timed_out=True)
                        return {
                            "status": "error",
                            "error": f"MATLAB execution timed out after {timeout}s. Code: {code_preview}...",
                            "elapsed_ms": round(elapsed)
                        }
                else:
                    output = engine_manager.engine.evalc(code, nargout=1)
                
                elapsed = (time.monotonic() - start_time) * 1000
                engine_manager._log_perf(code_preview, elapsed, timed_out=False)
                return {
                    "status": "success",
                    "output": str(output),
                    "elapsed_ms": round(elapsed)
                }
            except Exception as e:
                elapsed = (time.monotonic() - start_time) * 1000
                engine_manager._log_perf(code_preview, elapsed, timed_out=False)
                return {
                    "status": "error",
                    "error": str(e),
                    "elapsed_ms": round(elapsed)
                }
        else:
            try:
                if timeout > 0:
                    future = engine_manager.engine.eval(code, nargout=0, background=True)
                    try:
                        future.result(timeout=float(timeout))
                    except (TimeoutError, _MatlabTimeoutError):
                        future.cancel()
                        elapsed = (time.monotonic() - start_time) * 1000
                        engine_manager._log_perf(code_preview, elapsed, timed_out=True)
                        return {
                            "status": "error",
                            "error": f"MATLAB execution timed out after {timeout}s",
                            "elapsed_ms": round(elapsed)
                        }
                else:
                    engine_manager.engine.eval(code, nargout=0)
                
                elapsed = (time.monotonic() - start_time) * 1000
                engine_manager._log_perf(code_preview, elapsed, timed_out=False)
                return {
                    "status": "success",
                    "output": "Code executed successfully",
                    "elapsed_ms": round(elapsed)
                }
            except Exception as e:
                elapsed = (time.monotonic() - start_time) * 1000
                engine_manager._log_perf(code_preview, elapsed, timed_out=False)
                return {
                    "status": "error",
                    "error": str(e),
                    "elapsed_ms": round(elapsed)
                }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }

def matlab_eval_expression(expression: str) -> Dict[str, Any]:
    """Evaluate a MATLAB expression and return the result.
    
    Args:
        expression: MATLAB expression to evaluate
        
    Returns:
        Dictionary with status and value
    """
    try:
        if not engine_manager.engine or not engine_manager.is_connected:
            return {
                "status": "error",
                "error": "MATLAB engine not connected"
            }
        
        # Evaluate and get result
        result = engine_manager.engine.eval(expression, nargout=1)
        
        # Convert MATLAB result to Python types
        if hasattr(result, '__iter__') and not isinstance(result, str):
            # Handle arrays/matrices
            try:
                import numpy as np
                result_list = np.array(result).tolist()
                return {
                    "status": "success",
                    "value": result_list,
                    "type": "array"
                }
            except:
                return {
                    "status": "success",
                    "value": str(result),
                    "type": "complex"
                }
        else:
            # Handle scalars and strings
            return {
                "status": "success",
                "value": result,
                "type": type(result).__name__
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def matlab_get_workspace_variable(variable_name: str) -> Dict[str, Any]:
    """Get the value of a variable from MATLAB workspace.
    
    Args:
        variable_name: Name of the variable to retrieve
        
    Returns:
        Dictionary with status, value, and type information
    """
    try:
        if not engine_manager.engine or not engine_manager.is_connected:
            return {
                "status": "error",
                "error": "MATLAB engine not connected"
            }
        
        # Check if variable exists
        exists = engine_manager.engine.eval(f"exist('{variable_name}', 'var')", nargout=1)
        if exists == 0:
            return {
                "status": "error",
                "error": f"Variable '{variable_name}' not found in workspace"
            }
        
        # Get the variable value
        value = engine_manager.engine.workspace[variable_name]
        
        # Convert to Python types
        try:
            import numpy as np
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value_list = np.array(value).tolist()
                return {
                    "status": "success",
                    "variable": variable_name,
                    "value": value_list,
                    "type": "array"
                }
            else:
                return {
                    "status": "success",
                    "variable": variable_name,
                    "value": value,
                    "type": type(value).__name__
                }
        except:
            return {
                "status": "success",
                "variable": variable_name,
                "value": str(value),
                "type": "complex"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def matlab_set_workspace_variable(variable_name: str, value: Any) -> Dict[str, Any]:
    """Set a variable in the MATLAB workspace.
    
    Args:
        variable_name: Name of the variable to set
        value: Value to assign (will be converted to MATLAB type)
        
    Returns:
        Dictionary with status
    """
    try:
        if not engine_manager.engine or not engine_manager.is_connected:
            return {
                "status": "error",
                "error": "MATLAB engine not connected"
            }
        
        # Set the variable
        engine_manager.engine.workspace[variable_name] = value
        
        return {
            "status": "success",
            "message": f"Variable '{variable_name}' set successfully"
        }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def matlab_list_workspace_variables() -> Dict[str, Any]:
    """List all variables in the MATLAB workspace.
    
    Returns:
        Dictionary with list of variable names and their info
    """
    try:
        if not engine_manager.engine or not engine_manager.is_connected:
            return {
                "status": "error",
                "error": "MATLAB engine not connected"
            }
        
        # Get list of variables using 'who'
        vars_output = engine_manager.engine.evalc("who", nargout=1)
        var_names = [v.strip() for v in vars_output.strip().split('\n') if v.strip()]
        
        # Get detailed info using 'whos'
        whos_output = engine_manager.engine.evalc("whos", nargout=1)
        
        return {
            "status": "success",
            "variables": var_names,
            "details": whos_output
        }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def matlab_clear_workspace(variables: Optional[List[str]] = None) -> Dict[str, Any]:
    """Clear variables from MATLAB workspace.
    
    Args:
        variables: List of variable names to clear. If None, clears all.
        
    Returns:
        Dictionary with status
    """
    try:
        if not engine_manager.engine or not engine_manager.is_connected:
            return {
                "status": "error",
                "error": "MATLAB engine not connected"
            }
        
        if variables:
            # Clear specific variables
            var_list = " ".join(variables)
            engine_manager.engine.eval(f"clear {var_list}", nargout=0)
            return {
                "status": "success",
                "message": f"Cleared variables: {var_list}"
            }
        else:
            # Clear all variables
            engine_manager.engine.eval("clear", nargout=0)
            return {
                "status": "success",
                "message": "Cleared all workspace variables"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def matlab_run_script(script_path: str) -> Dict[str, Any]:
    """Run a MATLAB script file (.m file).
    
    Args:
        script_path: Path to the .m script file
        
    Returns:
        Dictionary with status and output
    """
    try:
        if not engine_manager.engine or not engine_manager.is_connected:
            return {
                "status": "error",
                "error": "MATLAB engine not connected"
            }
        
        # Check if file exists
        if not Path(script_path).exists():
            return {
                "status": "error",
                "error": f"Script file not found: {script_path}"
            }
        
        # Get directory and script name
        script_dir = str(Path(script_path).parent.absolute())
        script_name = Path(script_path).stem  # Name without extension
        
        # Add directory to path and run
        engine_manager.engine.addpath(script_dir, nargout=0)
        output = engine_manager.engine.evalc(script_name, nargout=1)
        
        return {
            "status": "success",
            "output": str(output),
            "script": script_path
        }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def matlab_call_function(function_name: str, *args, **kwargs) -> Dict[str, Any]:
    """Call a MATLAB function with arguments.
    
    Args:
        function_name: Name of the MATLAB function
        *args: Positional arguments
        **kwargs: Keyword argument 'nargout' for number of output arguments
        
    Returns:
        Dictionary with status and result
    """
    try:
        if not engine_manager.engine or not engine_manager.is_connected:
            return {
                "status": "error",
                "error": "MATLAB engine not connected"
            }
        
        # Get number of output arguments (default 1)
        nargout = kwargs.get('nargout', 1)
        
        # Get the function
        if not hasattr(engine_manager.engine, function_name):
            return {
                "status": "error",
                "error": f"Function '{function_name}' not found"
            }
        
        func = getattr(engine_manager.engine, function_name)
        
        # Call function
        if nargout == 0:
            func(*args, nargout=0)
            return {
                "status": "success",
                "message": f"Function '{function_name}' executed"
            }
        else:
            result = func(*args, nargout=nargout)
            
            # Convert result to JSON-serializable format
            try:
                import numpy as np
                if hasattr(result, '__iter__') and not isinstance(result, str):
                    result_list = np.array(result).tolist()
                    return {
                        "status": "success",
                        "result": result_list
                    }
                else:
                    return {
                        "status": "success",
                        "result": result
                    }
            except:
                return {
                    "status": "success",
                    "result": str(result)
                }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

async def main():
    """Entrypoint used by `python -m simulink_mcp_server.server`.

    VS Code expects an MCP server speaking JSON-RPC over stdio.
    Delegate to the actual MCP implementation in `mcp_server.py`.
    """

    # Import lazily to avoid circular imports (mcp_server imports from this module).
    from .mcp_server import main as mcp_main

    await mcp_main()

if __name__ == "__main__":
    asyncio.run(main())
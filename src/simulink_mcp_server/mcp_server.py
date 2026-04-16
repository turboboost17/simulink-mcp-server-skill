#!/usr/bin/env python3
"""
Simulink MCP Server using standard MCP SDK

This MCP server provides tools to interact with MATLAB Simulink through
a shared MATLAB engine connection using matlab.engine.shareEngine.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Sequence, Dict, Optional, List, cast

from .server import (
    engine_manager, connect_simulink_engine, simulink_new_model, simulink_add_block,
    simulink_connect_blocks, simulink_get_param, simulink_set_param,
    # Interactive context functions
    simulink_get_current_model, simulink_get_current_block,
    simulink_get_current_block_handle, simulink_get_current_system,
    simulink_get_selected_blocks, simulink_find_blocks,
    # Enhanced editing functions
    simulink_delete_block, simulink_delete_line, simulink_replace_block,
    simulink_highlight_block, simulink_arrange_system, simulink_route_line,
    simulink_expand_subsystem,
    # Model management functions
    simulink_model_is_loaded, simulink_model_is_dirty,
    simulink_save_model, simulink_load_model, simulink_run_simulation,
    simulink_list_blocks, simulink_create_subsystem,
    # Bus operations
    simulink_add_bus_element, simulink_create_bus_selector,
    # MATLAB execution functions
    matlab_execute_code, matlab_eval_expression, matlab_get_workspace_variable,
    matlab_set_workspace_variable, matlab_list_workspace_variables, matlab_clear_workspace,
    matlab_run_script, matlab_call_function,
)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
    )
except ImportError:
    # Fallback for different MCP package structure
    logging.error("MCP package not found. Please install with: uv add mcp")
    sys.exit(1)

# Configure logging (MCP uses stdout for protocol; keep logs on stderr)
# VS Code surfaces server stderr as warnings, so default to WARNING.
_log_level_name = os.getenv("SIMULINK_MCP_LOG_LEVEL", "WARNING").upper()
_log_level = getattr(logging, _log_level_name, logging.WARNING)
logging.basicConfig(level=_log_level, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Initialize the server
server = Server("simulink-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available Simulink and MATLAB tools."""
    tools = [
        # ============================================================
        # Engine management
        # ============================================================
        Tool(
            name="connect_simulink_engine",
            description="Connect to shared MATLAB engine for Simulink operations",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        # ============================================================
        # Interactive context functions
        # ============================================================
        Tool(
            name="simulink_get_current_model",
            description="Get the name of the currently active Simulink model (bdroot). Use this first to discover which model the user is working on.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="simulink_get_current_block",
            description="Get the path and type of the currently selected block in Simulink (gcb). Returns block path and BlockType.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="simulink_get_current_block_handle",
            description="Get the handle of the currently selected block (gcbh). Useful for operations that require block handles.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="simulink_get_current_system",
            description="Get the path of the currently active Simulink system or subsystem (gcs). Identifies if the user is inside a subsystem.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="simulink_get_selected_blocks",
            description="Get all currently selected blocks in the active Simulink window. Returns block paths and types.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="simulink_find_blocks",
            description="Find blocks in a model matching specific criteria. Uses Simulink.findBlocks with flexible search.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model to search"
                    },
                    "criteria": {
                        "type": "object",
                        "description": "Search criteria as key-value pairs, e.g. {'BlockType': 'Gain', 'Name': 'MyBlock'}",
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": ["model_name", "criteria"]
            }
        ),
        # ============================================================
        # Model management
        # ============================================================
        Tool(
            name="simulink_new_model",
            description="Create a new Simulink model and open it in the editor",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name for the new Simulink model"
                    }
                },
                "required": ["model_name"]
            }
        ),
        Tool(
            name="simulink_load_model",
            description="Load a Simulink model from a .slx file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the .slx model file"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="simulink_save_model",
            description="Save a Simulink model. Optionally specify a file path for Save-As.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Optional file path for Save-As"
                    }
                },
                "required": ["model_name"]
            }
        ),
        Tool(
            name="simulink_model_is_loaded",
            description="Check if a Simulink model is currently loaded in memory (bdIsLoaded)",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the model to check"
                    }
                },
                "required": ["model_name"]
            }
        ),
        Tool(
            name="simulink_model_is_dirty",
            description="Check if a Simulink model has unsaved changes (bdIsDirty)",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the model to check"
                    }
                },
                "required": ["model_name"]
            }
        ),
        Tool(
            name="simulink_run_simulation",
            description="Run a Simulink model simulation with optional stop time",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "stop_time": {
                        "type": "number",
                        "description": "Optional simulation stop time in seconds"
                    }
                },
                "required": ["model_name"]
            }
        ),
        # ============================================================
        # Block operations
        # ============================================================
        Tool(
            name="simulink_add_block",
            description="Add a block to a Simulink model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "block_type": {
                        "type": "string",
                        "description": "Type of block (e.g., 'simulink/Sources/Constant')"
                    },
                    "block_name": {
                        "type": "string",
                        "description": "Name for the block instance"
                    },
                    "position": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional position [left, top, right, bottom]",
                        "minItems": 4,
                        "maxItems": 4
                    }
                },
                "required": ["model_name", "block_type", "block_name"]
            }
        ),
        Tool(
            name="simulink_delete_block",
            description="Delete a block from a Simulink model",
            inputSchema={
                "type": "object",
                "properties": {
                    "block_path": {
                        "type": "string",
                        "description": "Full path to the block (e.g., 'ModelName/BlockName')"
                    }
                },
                "required": ["block_path"]
            }
        ),
        Tool(
            name="simulink_replace_block",
            description="Replace all blocks of one type with another type in a model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "old_block_type": {
                        "type": "string",
                        "description": "BlockType to replace (e.g., 'Gain')"
                    },
                    "new_block_type": {
                        "type": "string",
                        "description": "New block type path (e.g., 'simulink/Math Operations/Product')"
                    }
                },
                "required": ["model_name", "old_block_type", "new_block_type"]
            }
        ),
        Tool(
            name="simulink_list_blocks",
            description="List all blocks in a Simulink model, optionally filtered by BlockType",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "block_type": {
                        "type": "string",
                        "description": "Optional BlockType filter (e.g., 'Gain', 'Sum', 'Scope')"
                    }
                },
                "required": ["model_name"]
            }
        ),
        Tool(
            name="simulink_highlight_block",
            description="Highlight a block in the Simulink editor for visual feedback. Colors: red, green, yellow, cyan, magenta, none",
            inputSchema={
                "type": "object",
                "properties": {
                    "block_path": {
                        "type": "string",
                        "description": "Full path to the block (e.g., 'ModelName/BlockName')"
                    },
                    "color": {
                        "type": "string",
                        "description": "Highlight color (red, green, yellow, cyan, magenta, none)",
                        "enum": ["red", "green", "yellow", "cyan", "magenta", "none"]
                    }
                },
                "required": ["block_path"]
            }
        ),
        # ============================================================
        # Connection / line operations
        # ============================================================
        Tool(
            name="simulink_connect_blocks",
            description="Connect two blocks in a Simulink model with a signal line",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "source_block": {
                        "type": "string",
                        "description": "Name of the source block"
                    },
                    "source_port": {
                        "type": "integer",
                        "description": "Output port number (1-based)"
                    },
                    "dest_block": {
                        "type": "string",
                        "description": "Name of the destination block"
                    },
                    "dest_port": {
                        "type": "integer",
                        "description": "Input port number (1-based)"
                    }
                },
                "required": ["model_name", "source_block", "source_port", "dest_block", "dest_port"]
            }
        ),
        Tool(
            name="simulink_delete_line",
            description="Delete a signal line connecting two blocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "source_block": {
                        "type": "string",
                        "description": "Name of the source block"
                    },
                    "source_port": {
                        "type": "integer",
                        "description": "Output port number (1-based)"
                    },
                    "dest_block": {
                        "type": "string",
                        "description": "Name of the destination block"
                    },
                    "dest_port": {
                        "type": "integer",
                        "description": "Input port number (1-based)"
                    }
                },
                "required": ["model_name", "source_block", "source_port", "dest_block", "dest_port"]
            }
        ),
        # ============================================================
        # Parameter management
        # ============================================================
        Tool(
            name="simulink_get_param",
            description="Get a parameter value from a Simulink block or model. Leave block_name empty to get model-level parameters (e.g. HardwareBoard, Toolchain, CoderTargetData).",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "block_name": {
                        "type": "string",
                        "description": "Name of the block (leave empty for model-level parameters)",
                        "default": ""
                    },
                    "parameter": {
                        "type": "string",
                        "description": "Parameter name to retrieve"
                    }
                },
                "required": ["model_name", "parameter"]
            }
        ),
        Tool(
            name="simulink_set_param",
            description="Set a parameter value for a Simulink block or model. Leave block_name empty to set model-level parameters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "block_name": {
                        "type": "string",
                        "description": "Name of the block (leave empty for model-level parameters)",
                        "default": ""
                    },
                    "parameter": {
                        "type": "string",
                        "description": "Parameter name to set"
                    },
                    "value": {
                        "type": "string",
                        "description": "New parameter value"
                    }
                },
                "required": ["model_name", "parameter", "value"]
            }
        ),
        # ============================================================
        # Hierarchy & layout
        # ============================================================
        Tool(
            name="simulink_create_subsystem",
            description="Create a subsystem from a list of blocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "blocks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of block names to group into subsystem"
                    },
                    "subsystem_name": {
                        "type": "string",
                        "description": "Name for the new subsystem"
                    }
                },
                "required": ["model_name", "blocks", "subsystem_name"]
            }
        ),
        Tool(
            name="simulink_expand_subsystem",
            description="Replace a subsystem with its contents (flatten hierarchy)",
            inputSchema={
                "type": "object",
                "properties": {
                    "subsystem_path": {
                        "type": "string",
                        "description": "Full path to the subsystem (e.g., 'ModelName/SubsystemName')"
                    }
                },
                "required": ["subsystem_path"]
            }
        ),
        Tool(
            name="simulink_arrange_system",
            description="Automatically arrange and layout blocks in a system for better readability",
            inputSchema={
                "type": "object",
                "properties": {
                    "system_path": {
                        "type": "string",
                        "description": "Path to the system to arrange (model or subsystem)"
                    }
                },
                "required": ["system_path"]
            }
        ),
        Tool(
            name="simulink_route_line",
            description="Automatically route a signal line for cleaner appearance",
            inputSchema={
                "type": "object",
                "properties": {
                    "line_handle": {
                        "type": "integer",
                        "description": "Handle of the line to route"
                    }
                },
                "required": ["line_handle"]
            }
        ),
        # ============================================================
        # Bus operations
        # ============================================================
        Tool(
            name="simulink_add_bus_element",
            description="Add an element to a Simulink Bus object",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "bus_object_name": {
                        "type": "string",
                        "description": "Name of the bus object"
                    },
                    "element_name": {
                        "type": "string",
                        "description": "Name of the element to add"
                    },
                    "data_type": {
                        "type": "string",
                        "description": "Data type (default: 'double')"
                    },
                    "dimensions": {
                        "type": "string",
                        "description": "Dimensions (default: '1')"
                    }
                },
                "required": ["model_name", "bus_object_name", "element_name"]
            }
        ),
        Tool(
            name="simulink_create_bus_selector",
            description="Create a Bus Selector block and configure it",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the Simulink model"
                    },
                    "bus_signal_block": {
                        "type": "string",
                        "description": "Name of the bus signal source block"
                    },
                    "selected_signals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of signal names to select"
                    },
                    "selector_name": {
                        "type": "string",
                        "description": "Name for the new Bus Selector block"
                    }
                },
                "required": ["model_name", "bus_signal_block", "selected_signals", "selector_name"]
            }
        ),
        # ============================================================
        # MATLAB code execution tools
        # ============================================================
        Tool(
            name="matlab_execute_code",
            description="Execute arbitrary MATLAB code and return output. Supports multi-line code blocks. Use for analysis, plotting, data processing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "MATLAB code to execute"
                    },
                    "capture_output": {
                        "type": "boolean",
                        "description": "Whether to capture and return output (default: true)"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="matlab_eval_expression",
            description="Evaluate a MATLAB expression and return the numeric/string result. Use for quick calculations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "MATLAB expression to evaluate (e.g., 'sqrt(144)', '2^10')"
                    }
                },
                "required": ["expression"]
            }
        ),
        Tool(
            name="matlab_get_workspace_variable",
            description="Get the value of a variable from the MATLAB workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "variable_name": {
                        "type": "string",
                        "description": "Name of the variable to retrieve"
                    }
                },
                "required": ["variable_name"]
            }
        ),
        Tool(
            name="matlab_set_workspace_variable",
            description="Set a variable in the MATLAB workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "variable_name": {
                        "type": "string",
                        "description": "Name of the variable to set"
                    },
                    "value": {
                        "description": "Value to assign (will be converted to appropriate MATLAB type)"
                    }
                },
                "required": ["variable_name", "value"]
            }
        ),
        Tool(
            name="matlab_list_workspace_variables",
            description="List all variables in the MATLAB workspace with type and size details (whos)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="matlab_clear_workspace",
            description="Clear variables from MATLAB workspace. Clears all if no list provided.",
            inputSchema={
                "type": "object",
                "properties": {
                    "variables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of variable names to clear. If not provided, clears all."
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="matlab_run_script",
            description="Run a MATLAB .m script file and return output",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Absolute path to the .m script file"
                    }
                },
                "required": ["script_path"]
            }
        ),
        Tool(
            name="matlab_call_function",
            description="Call a MATLAB function with arguments",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name of the MATLAB function"
                    },
                    "args": {
                        "type": "array",
                        "items": {},
                        "description": "Positional arguments for the function"
                    },
                    "nargout": {
                        "type": "integer",
                        "description": "Number of output arguments (default: 1)"
                    }
                },
                "required": ["function_name"]
            }
        ),
        # ============================================================
        # MATLAB code quality (matching MathWorks core server features)
        # ============================================================
        Tool(
            name="matlab_check_code",
            description="Perform static code analysis on a MATLAB script. Returns warnings about coding style, potential errors, deprecated functions, performance issues. Non-destructive, read-only.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Absolute path to the MATLAB .m file to analyze"
                    }
                },
                "required": ["script_path"]
            }
        ),
        Tool(
            name="matlab_run_tests",
            description="Run a MATLAB test file and return comprehensive test results. Designed for MATLAB unit test files that follow the testing framework.",
            inputSchema={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "Absolute path to the MATLAB test .m file"
                    }
                },
                "required": ["script_path"]
            }
        ),
        Tool(
            name="matlab_detect_toolboxes",
            description="Returns information about installed MATLAB and toolboxes, including version numbers",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]

    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls.

    MCP SDK >=1.17 expects the handler to return an iterable of content blocks
    (list[TextContent | ImageContent | ...]), NOT a CallToolResult object.
    """
    try:
        if arguments is None:
            arguments = {}

        result_text: str = ""

        # ============================================================
        # Engine management
        # ============================================================
        if name == "connect_simulink_engine":
            result_text = connect_simulink_engine()

        # ============================================================
        # Interactive context functions
        # ============================================================
        elif name == "simulink_get_current_model":
            result_text = simulink_get_current_model()

        elif name == "simulink_get_current_block":
            result_text = simulink_get_current_block()

        elif name == "simulink_get_current_block_handle":
            result_text = simulink_get_current_block_handle()

        elif name == "simulink_get_current_system":
            result_text = simulink_get_current_system()

        elif name == "simulink_get_selected_blocks":
            result_text = simulink_get_selected_blocks()

        elif name == "simulink_find_blocks":
            model_name = arguments.get("model_name", "")
            criteria = arguments.get("criteria", {})
            if not model_name:
                return [TextContent(type="text", text="Error: model_name is required")]
            result_text = simulink_find_blocks(model_name, criteria)

        # ============================================================
        # Model management
        # ============================================================
        elif name == "simulink_new_model":
            model_name = arguments.get("model_name", "")
            if not model_name:
                return [TextContent(type="text", text="Error: model_name is required")]
            result_text = simulink_new_model(model_name)

        elif name == "simulink_load_model":
            file_path = arguments.get("file_path", "")
            if not file_path:
                return [TextContent(type="text", text="Error: file_path is required")]
            result_text = simulink_load_model(file_path)

        elif name == "simulink_save_model":
            model_name = arguments.get("model_name", "")
            file_path = arguments.get("file_path")
            if not model_name:
                return [TextContent(type="text", text="Error: model_name is required")]
            result_text = simulink_save_model(model_name, file_path)

        elif name == "simulink_model_is_loaded":
            model_name = arguments.get("model_name", "")
            if not model_name:
                return [TextContent(type="text", text="Error: model_name is required")]
            result_text = simulink_model_is_loaded(model_name)

        elif name == "simulink_model_is_dirty":
            model_name = arguments.get("model_name", "")
            if not model_name:
                return [TextContent(type="text", text="Error: model_name is required")]
            result_text = simulink_model_is_dirty(model_name)

        elif name == "simulink_run_simulation":
            model_name = arguments.get("model_name", "")
            stop_time = arguments.get("stop_time")
            if not model_name:
                return [TextContent(type="text", text="Error: model_name is required")]
            result_text = simulink_run_simulation(model_name, stop_time)

        # ============================================================
        # Block operations
        # ============================================================
        elif name == "simulink_add_block":
            model_name = arguments.get("model_name", "")
            block_type = arguments.get("block_type", "")
            block_name = arguments.get("block_name", "")
            position = arguments.get("position")
            if not all([model_name, block_type, block_name]):
                return [TextContent(type="text", text="Error: model_name, block_type, and block_name are required")]
            result_text = simulink_add_block(model_name, block_type, block_name, position)

        elif name == "simulink_delete_block":
            block_path = arguments.get("block_path", "")
            if not block_path:
                return [TextContent(type="text", text="Error: block_path is required")]
            result_text = simulink_delete_block(block_path)

        elif name == "simulink_replace_block":
            model_name = arguments.get("model_name", "")
            old_block_type = arguments.get("old_block_type", "")
            new_block_type = arguments.get("new_block_type", "")
            if not all([model_name, old_block_type, new_block_type]):
                return [TextContent(type="text", text="Error: model_name, old_block_type, new_block_type required")]
            result_text = simulink_replace_block(model_name, old_block_type, new_block_type)

        elif name == "simulink_list_blocks":
            model_name = arguments.get("model_name", "")
            block_type = arguments.get("block_type")
            if not model_name:
                return [TextContent(type="text", text="Error: model_name is required")]
            result_text = simulink_list_blocks(model_name, block_type)

        elif name == "simulink_highlight_block":
            block_path = arguments.get("block_path", "")
            color = arguments.get("color", "red")
            if not block_path:
                return [TextContent(type="text", text="Error: block_path is required")]
            result_text = simulink_highlight_block(block_path, color)

        # ============================================================
        # Connection / line operations
        # ============================================================
        elif name == "simulink_connect_blocks":
            model_name = arguments.get("model_name", "")
            source_block = arguments.get("source_block", "")
            source_port = arguments.get("source_port")
            dest_block = arguments.get("dest_block", "")
            dest_port = arguments.get("dest_port")
            if not all([model_name, source_block, source_port, dest_block, dest_port]):
                return [TextContent(type="text", text="Error: all connection parameters are required")]
            result_text = simulink_connect_blocks(model_name, source_block, int(source_port), dest_block, int(dest_port))

        elif name == "simulink_delete_line":
            model_name = arguments.get("model_name", "")
            source_block = arguments.get("source_block", "")
            source_port = arguments.get("source_port")
            dest_block = arguments.get("dest_block", "")
            dest_port = arguments.get("dest_port")
            if not all([model_name, source_block, source_port, dest_block, dest_port]):
                return [TextContent(type="text", text="Error: all connection parameters are required")]
            result_text = simulink_delete_line(model_name, source_block, int(source_port), dest_block, int(dest_port))

        # ============================================================
        # Parameter management
        # ============================================================
        elif name == "simulink_get_param":
            model_name = arguments.get("model_name", "")
            block_name = arguments.get("block_name", "")
            parameter = arguments.get("parameter", "")
            if not all([model_name, parameter]):
                return [TextContent(type="text", text="Error: model_name and parameter are required")]
            result_text = simulink_get_param(model_name, block_name, parameter)

        elif name == "simulink_set_param":
            model_name = arguments.get("model_name", "")
            block_name = arguments.get("block_name", "")
            parameter = arguments.get("parameter", "")
            value = arguments.get("value", "")
            if not all([model_name, parameter, value]):
                return [TextContent(type="text", text="Error: model_name, parameter, and value are required")]
            result_text = simulink_set_param(model_name, block_name, parameter, value)

        # ============================================================
        # Hierarchy & layout
        # ============================================================
        elif name == "simulink_create_subsystem":
            model_name = arguments.get("model_name", "")
            blocks = arguments.get("blocks", [])
            subsystem_name = arguments.get("subsystem_name", "")
            if not all([model_name, blocks, subsystem_name]):
                return [TextContent(type="text", text="Error: model_name, blocks, and subsystem_name are required")]
            result_text = simulink_create_subsystem(model_name, blocks, subsystem_name)

        elif name == "simulink_expand_subsystem":
            subsystem_path = arguments.get("subsystem_path", "")
            if not subsystem_path:
                return [TextContent(type="text", text="Error: subsystem_path is required")]
            result_text = simulink_expand_subsystem(subsystem_path)

        elif name == "simulink_arrange_system":
            system_path = arguments.get("system_path", "")
            if not system_path:
                return [TextContent(type="text", text="Error: system_path is required")]
            result_text = simulink_arrange_system(system_path)

        elif name == "simulink_route_line":
            line_handle = arguments.get("line_handle")
            if line_handle is None:
                return [TextContent(type="text", text="Error: line_handle is required")]
            result_text = simulink_route_line(int(line_handle))

        # ============================================================
        # Bus operations
        # ============================================================
        elif name == "simulink_add_bus_element":
            model_name = arguments.get("model_name", "")
            bus_object_name = arguments.get("bus_object_name", "")
            element_name = arguments.get("element_name", "")
            data_type = arguments.get("data_type", "double")
            dimensions = arguments.get("dimensions", "1")
            if not all([model_name, bus_object_name, element_name]):
                return [TextContent(type="text", text="Error: model_name, bus_object_name, element_name required")]
            result_text = simulink_add_bus_element(model_name, bus_object_name, element_name, data_type, dimensions)

        elif name == "simulink_create_bus_selector":
            model_name = arguments.get("model_name", "")
            bus_signal_block = arguments.get("bus_signal_block", "")
            selected_signals = arguments.get("selected_signals", [])
            selector_name = arguments.get("selector_name", "")
            if not all([model_name, bus_signal_block, selected_signals, selector_name]):
                return [TextContent(type="text", text="Error: all bus selector parameters are required")]
            result_text = simulink_create_bus_selector(model_name, bus_signal_block, selected_signals, selector_name)

        # ============================================================
        # MATLAB execution tools
        # ============================================================
        elif name == "matlab_execute_code":
            code = arguments.get("code", "")
            capture_output = arguments.get("capture_output", True)
            if not code:
                return [TextContent(type="text", text="Error: code is required")]
            result = matlab_execute_code(code, capture_output)
            result_text = json.dumps(result, indent=2, default=str)

        elif name == "matlab_eval_expression":
            expression = arguments.get("expression", "")
            if not expression:
                return [TextContent(type="text", text="Error: expression is required")]
            result = matlab_eval_expression(expression)
            result_text = json.dumps(result, indent=2, default=str)

        elif name == "matlab_get_workspace_variable":
            variable_name = arguments.get("variable_name", "")
            if not variable_name:
                return [TextContent(type="text", text="Error: variable_name is required")]
            result = matlab_get_workspace_variable(variable_name)
            result_text = json.dumps(result, indent=2, default=str)

        elif name == "matlab_set_workspace_variable":
            variable_name = arguments.get("variable_name", "")
            value = arguments.get("value")
            if not variable_name:
                return [TextContent(type="text", text="Error: variable_name is required")]
            result = matlab_set_workspace_variable(variable_name, value)
            result_text = json.dumps(result, indent=2, default=str)

        elif name == "matlab_list_workspace_variables":
            result = matlab_list_workspace_variables()
            result_text = json.dumps(result, indent=2, default=str)

        elif name == "matlab_clear_workspace":
            variables = arguments.get("variables")
            result = matlab_clear_workspace(variables)
            result_text = json.dumps(result, indent=2, default=str)

        elif name == "matlab_run_script":
            script_path = arguments.get("script_path", "")
            if not script_path:
                return [TextContent(type="text", text="Error: script_path is required")]
            result = matlab_run_script(script_path)
            result_text = json.dumps(result, indent=2, default=str)

        elif name == "matlab_call_function":
            function_name = arguments.get("function_name", "")
            args = arguments.get("args", [])
            nargout = arguments.get("nargout", 1)
            if not function_name:
                return [TextContent(type="text", text="Error: function_name is required")]
            result = matlab_call_function(function_name, *args, nargout=nargout)
            result_text = json.dumps(result, indent=2, default=str)

        # ============================================================
        # MATLAB code quality tools (matching MathWorks core server)
        # ============================================================
        elif name == "matlab_check_code":
            script_path = arguments.get("script_path", "")
            if not script_path:
                return [TextContent(type="text", text="Error: script_path is required")]
            result = matlab_execute_code(
                f"disp(evalc(\"checkcode('{script_path.replace(chr(39), chr(39)+chr(39))}');\"))"
            )
            result_text = json.dumps(result, indent=2, default=str)

        elif name == "matlab_run_tests":
            script_path = arguments.get("script_path", "")
            if not script_path:
                return [TextContent(type="text", text="Error: script_path is required")]
            result = matlab_execute_code(
                f"results = runtests('{script_path.replace(chr(39), chr(39)+chr(39))}'); disp(results);"
            )
            result_text = json.dumps(result, indent=2, default=str)

        elif name == "matlab_detect_toolboxes":
            result = matlab_execute_code("ver")
            result_text = json.dumps(result, indent=2, default=str)

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Error handling tool call {name}: {e}")
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    """Main function to run the MCP server."""
    # Initialize MATLAB engine connection (sync call — matlab.engine is blocking)
    logger.info("Initializing Simulink MCP Server...")
    engine_manager.connect()

    # Run the MCP server
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
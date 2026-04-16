"""
Example usage of the Simulink MCP Server functions.
This script demonstrates how to use the various Simulink operations programmatically.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import server
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from simulink_mcp_server.server import (
    engine_manager, 
    connect_simulink_engine,
    simulink_new_model,
    simulink_add_block,
    simulink_connect_blocks,
    simulink_set_param,
    simulink_get_param,
    simulink_save_model,
    simulink_run_simulation,
    simulink_list_blocks
)

async def demo_basic_model():
    """Demonstrate creating a basic Simulink model."""
    print("=== Creating Basic Simulink Model ===")
    
    # Connect to engine
    result = connect_simulink_engine()
    print(f"Engine connection: {result}")
    
    # Create new model
    model_name = "DemoModel"
    print(f"Creating model: {simulink_new_model(model_name)}")
    
    # Add blocks
    print(f"Adding Constant block: {simulink_add_block(model_name, 'simulink/Sources/Constant', 'Constant1', [30, 30, 60, 60])}")
    print(f"Adding Gain block: {simulink_add_block(model_name, 'simulink/Math Operations/Gain', 'Gain1', [120, 30, 150, 60])}")
    print(f"Adding Scope block: {simulink_add_block(model_name, 'simulink/Sinks/Scope', 'Scope1', [210, 30, 240, 60])}")
    
    # Connect blocks
    print(f"Connecting Constant to Gain: {simulink_connect_blocks(model_name, 'Constant1', 1, 'Gain1', 1)}")
    print(f"Connecting Gain to Scope: {simulink_connect_blocks(model_name, 'Gain1', 1, 'Scope1', 1)}")
    
    # Set parameters
    print(f"Setting Constant value: {simulink_set_param(model_name, 'Constant1', 'Value', '3.14')}")
    print(f"Setting Gain value: {simulink_set_param(model_name, 'Gain1', 'Gain', '2')}")
    
    # Get parameters to verify
    print(f"Constant value: {simulink_get_param(model_name, 'Constant1', 'Value')}")
    print(f"Gain value: {simulink_get_param(model_name, 'Gain1', 'Gain')}")
    
    # List blocks
    print(f"Blocks in model: {simulink_list_blocks(model_name)}")
    
    # Save model
    print(f"Saving model: {simulink_save_model(model_name)}")
    
    # Run simulation
    print(f"Running simulation: {simulink_run_simulation(model_name, 10.0)}")

async def demo_advanced_features():
    """Demonstrate advanced Simulink features."""
    print("\n=== Advanced Simulink Features ===")
    
    model_name = "AdvancedDemo"
    print(f"Creating advanced model: {simulink_new_model(model_name)}")
    
    # Add multiple blocks for subsystem demo
    blocks = []
    for i in range(3):
        block_name = f"Gain{i+1}"
        simulink_add_block(model_name, 'simulink/Math Operations/Gain', block_name, [30 + i*60, 30, 60 + i*60, 60])
        blocks.append(block_name)
    
    # Create subsystem (would need blocks to be selected first)
    print("Note: Subsystem creation requires interactive selection in real implementation")
    
    # List specific block types
    print(f"Gain blocks: {simulink_list_blocks(model_name, 'Gain')}")

async def main():
    """Main demo function."""
    print("Simulink MCP Server Demo")
    print("========================")
    
    # Initialize engine manager
    await engine_manager.connect()
    
    try:
        await demo_basic_model()
        await demo_advanced_features()
    except Exception as e:
        print(f"Demo error: {e}")
    finally:
        await engine_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
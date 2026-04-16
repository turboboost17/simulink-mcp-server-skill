"""
Test script for new interactive Simulink MCP functions.
Tests the context-aware functions that interact with the currently open model.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simulink_mcp_server.server import (
    engine_manager,
    simulink_get_current_model,
    simulink_get_current_block,
    simulink_get_current_block_handle,
    simulink_get_current_system,
    simulink_get_selected_blocks,
    simulink_find_blocks,
    simulink_delete_block,
    simulink_highlight_block,
    simulink_arrange_system,
    simulink_model_is_loaded,
    simulink_model_is_dirty,
)
import asyncio

async def test_interactive_functions():
    """Test the interactive context functions."""
    print("=== Testing Interactive Simulink Functions ===\n")
    
    # Connect to shared engine
    print("1. Connecting to MATLAB engine...")
    connected = await engine_manager.connect()
    if not connected:
        print("Failed to connect to MATLAB engine")
        return
    print("✓ Connected successfully\n")
    
    # Test getting current context
    print("2. Testing Context Functions (with open model):")
    print("-" * 60)
    
    print("\n📍 Current Model (bdroot):")
    result = simulink_get_current_model()
    print(f"   {result}")
    
    print("\n📍 Current System (gcs):")
    result = simulink_get_current_system()
    print(f"   {result}")
    
    print("\n📍 Current Block (gcb):")
    result = simulink_get_current_block()
    print(f"   {result}")
    
    print("\n📍 Current Block Handle (gcbh):")
    result = simulink_get_current_block_handle()
    print(f"   {result}")
    
    print("\n📍 Selected Blocks:")
    result = simulink_get_selected_blocks()
    print(f"   {result}")
    
    # Extract model name from context for further tests
    model_result = simulink_get_current_model()
    if "Current model:" in model_result:
        model_name = model_result.split("Current model:")[1].strip()
        if model_name and model_name != "No model currently open or active":
            print(f"\n3. Testing with detected model: '{model_name}'")
            print("-" * 60)
            
            print("\n🔍 Finding Gain blocks:")
            result = simulink_find_blocks(model_name, {"BlockType": "Gain"})
            print(f"   {result}")
            
            print("\n📊 Model Status Checks:")
            result = simulink_model_is_loaded(model_name)
            print(f"   Loaded: {result}")
            
            result = simulink_model_is_dirty(model_name)
            print(f"   Dirty: {result}")
            
            print("\n✨ Testing Layout Functions:")
            print("   Arranging system layout...")
            result = simulink_arrange_system(model_name)
            print(f"   {result}")
            
            # Test highlighting if we have a current block
            block_result = simulink_get_current_block()
            if "Current block:" in block_result:
                block_path = block_result.split("Current block:")[1].split("\n")[0].strip()
                if block_path and block_path != "No block currently selected":
                    print(f"\n🎨 Highlighting current block: {block_path}")
                    result = simulink_highlight_block(block_path, "green")
                    print(f"   {result}")
        else:
            print("\n⚠️  No model detected. Please open a Simulink model and try again.")
    else:
        print("\n⚠️  Could not detect open model. Please open a Simulink model and try again.")
    
    print("\n" + "=" * 60)
    print("✓ Interactive function tests complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_interactive_functions())

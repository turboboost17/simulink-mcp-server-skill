"""
Test script for MATLAB code execution functions

This script tests the newly added MATLAB code execution capabilities:
- matlab_execute_code
- matlab_eval_expression
- matlab_get_workspace_variable
- matlab_set_workspace_variable
- matlab_list_workspace_variables
- matlab_clear_workspace
- matlab_run_script
- matlab_call_function
"""

import sys
from pathlib import Path

# Add source directory to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from simulink_mcp_server.server import (
    engine_manager,
    matlab_execute_code,
    matlab_eval_expression,
    matlab_get_workspace_variable,
    matlab_set_workspace_variable,
    matlab_list_workspace_variables,
    matlab_clear_workspace,
    matlab_call_function
)
import asyncio


async def test_matlab_functions():
    """Test all MATLAB code execution functions."""
    
    print("=" * 60)
    print("Testing MATLAB Code Execution Functions")
    print("=" * 60)
    
    # Connect to MATLAB engine
    print("\n1. Connecting to MATLAB engine...")
    connected = await engine_manager.connect()
    if not connected:
        print("❌ Failed to connect to MATLAB engine")
        return
    print("✅ Connected successfully")
    
    # Test 1: Execute simple code
    print("\n2. Testing matlab_execute_code()...")
    result = matlab_execute_code("disp('Hello from MATLAB!')")
    print(f"   Result: {result}")
    if result.get('status') == 'success':
        print("✅ Code execution successful")
    else:
        print(f"❌ Code execution failed: {result.get('error')}")
    
    # Test 2: Set a variable
    print("\n3. Testing matlab_set_workspace_variable()...")
    result = matlab_set_workspace_variable("test_var", 42)
    print(f"   Result: {result}")
    if result.get('status') == 'success':
        print("✅ Variable set successfully")
    else:
        print(f"❌ Variable set failed: {result.get('error')}")
    
    # Test 3: Get the variable
    print("\n4. Testing matlab_get_workspace_variable()...")
    result = matlab_get_workspace_variable("test_var")
    print(f"   Result: {result}")
    if result.get('status') == 'success' and result.get('value') == 42:
        print("✅ Variable retrieved successfully")
    else:
        print(f"❌ Variable retrieval failed")
    
    # Test 4: Evaluate expression
    print("\n5. Testing matlab_eval_expression()...")
    result = matlab_eval_expression("2 + 2")
    print(f"   Result: {result}")
    if result.get('status') == 'success' and result.get('value') == 4.0:
        print("✅ Expression evaluated successfully")
    else:
        print(f"❌ Expression evaluation failed")
    
    # Test 5: Create a matrix
    print("\n6. Testing matrix creation...")
    result = matlab_set_workspace_variable("my_matrix", [[1, 2], [3, 4]])
    print(f"   Set Result: {result}")
    
    result = matlab_get_workspace_variable("my_matrix")
    print(f"   Get Result: {result}")
    if result.get('status') == 'success':
        print("✅ Matrix creation and retrieval successful")
    else:
        print(f"❌ Matrix operations failed")
    
    # Test 6: List workspace variables
    print("\n7. Testing matlab_list_workspace_variables()...")
    result = matlab_list_workspace_variables()
    print(f"   Result: {result}")
    if result.get('status') == 'success':
        print(f"✅ Workspace variables listed: {result.get('variables')}")
    else:
        print(f"❌ Listing variables failed")
    
    # Test 7: Call MATLAB function
    print("\n8. Testing matlab_call_function()...")
    result = matlab_call_function("magic", 3, nargout=1)
    print(f"   Result: {result}")
    if result.get('status') == 'success':
        print("✅ Function call successful")
        print(f"   Magic square: {result.get('result')}")
    else:
        print(f"❌ Function call failed: {result.get('error')}")
    
    # Test 8: Execute multi-line code
    print("\n9. Testing multi-line code execution...")
    code = """
    x = 1:10;
    y = x.^2;
    mean_y = mean(y);
    disp(['Mean of y: ', num2str(mean_y)]);
    """
    result = matlab_execute_code(code)
    print(f"   Result: {result}")
    if result.get('status') == 'success':
        print("✅ Multi-line code executed successfully")
    else:
        print(f"❌ Multi-line execution failed: {result.get('error')}")
    
    # Test 9: Clear specific variable
    print("\n10. Testing matlab_clear_workspace() with specific variable...")
    result = matlab_clear_workspace(["test_var"])
    print(f"   Result: {result}")
    if result.get('status') == 'success':
        print("✅ Specific variable cleared")
    else:
        print(f"❌ Clear failed: {result.get('error')}")
    
    # Verify variable was cleared
    result = matlab_get_workspace_variable("test_var")
    if result.get('status') == 'error':
        print("✅ Verified: Variable no longer exists")
    else:
        print("❌ Variable still exists")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_matlab_functions())

"""
Test script to verify MATLAB Engine connection and shared engine setup.
Run this to debug connection issues.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simulink_mcp_server.server import MATLABEngineManager, connect_simulink_engine

async def test_engine_connection():
    """Test the MATLAB engine connection step by step."""
    print("=== MATLAB Engine Connection Test ===")
    
    # Test 1: Check if MATLAB Engine is available
    print("\n1. Testing MATLAB Engine availability...")
    manager = MATLABEngineManager()
    available = manager.ensure_matlab_engine_installed()
    
    if available:
        print("✓ MATLAB Engine Python package is available")
    else:
        print("✗ MATLAB Engine Python package is NOT available")
        print("  - Need to install MATLAB Engine for Python")
        return False
    
    # Test 2: Try to connect to shared engine
    print(f"\n2. Testing connection to shared engine '{manager.shared_engine_name}'...")
    
    try:
        import matlab.engine
        
        # Check if the shared engine exists
        engines = matlab.engine.find_matlab()
        print(f"Found existing MATLAB engines: {engines}")
        
        if manager.shared_engine_name in engines:
            print(f"✓ Shared engine '{manager.shared_engine_name}' found")
        else:
            print(f"! Shared engine '{manager.shared_engine_name}' not found - will create new one")
        
        # Test actual connection
        success = await manager.connect()
        
        if success:
            print("✓ Successfully connected to MATLAB engine")
            
            # Test basic MATLAB command
            result = manager.execute_matlab_code("disp('Hello from MATLAB!')")
            if result["success"]:
                print(f"✓ MATLAB execution test passed: {result['output']}")
            else:
                print(f"✗ MATLAB execution test failed: {result['error']}")
            
            # Test Simulink
            result = manager.execute_matlab_code("ver('Simulink')")
            if result["success"]:
                print("✓ Simulink is available")
            else:
                print(f"✗ Simulink test failed: {result['error']}")
                
        else:
            print("✗ Failed to connect to MATLAB engine")
            return False
            
    except Exception as e:
        print(f"✗ Connection test failed with error: {e}")
        return False
    
    # Test 3: Test the high-level function
    print("\n3. Testing high-level connection function...")
    result = connect_simulink_engine()
    print(f"Result: {result}")
    
    print("\n=== Test Complete ===")
    return True

def test_matlab_installation():
    """Test basic MATLAB installation."""
    print("=== MATLAB Installation Test ===")
    
    import os
    matlab_path = os.getenv('MATLAB_PATH', 'C:/Program Files/MATLAB/R2025a')
    print(f"MATLAB_PATH: {matlab_path}")
    
    if os.path.exists(matlab_path):
        print("✓ MATLAB installation directory found")
        
        matlab_exe = os.path.join(matlab_path, 'bin', 'matlab.exe')
        if os.path.exists(matlab_exe):
            print("✓ MATLAB executable found")
        else:
            print("✗ MATLAB executable not found")
            
        engine_path = os.path.join(matlab_path, 'extern', 'engines', 'python')
        if os.path.exists(engine_path):
            print("✓ MATLAB Engine for Python source found")
        else:
            print("✗ MATLAB Engine for Python source not found")
    else:
        print("✗ MATLAB installation directory not found")
        print("  - Check MATLAB_PATH environment variable")

if __name__ == "__main__":
    print("Simulink MCP Server - Connection Test")
    print("====================================")
    
    test_matlab_installation()
    print()
    
    # Run async test
    try:
        asyncio.run(test_engine_connection())
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)
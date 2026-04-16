# Simulink MCP Server - Configuration File
# Copy this file to 'config.local.ps1' and customize for your system
# The install script will use config.local.ps1 if it exists

# MATLAB Installation Path
# Leave empty for auto-detection, or specify exact path
$MATLAB_PATH = ""
# Example: $MATLAB_PATH = "C:\Program Files\MATLAB\R2025a"

# Shared Engine Name
# This is the name used for matlab.engine.shareEngine()
$SHARED_ENGINE_NAME = "SimulinkMCP"

# Python Version (for UV)
# Leave empty to use UV's default Python version
$PYTHON_VERSION = ""
# Example: $PYTHON_VERSION = "3.12"

# MCP Server Name in VS Code
# This is how the server appears in Copilot Chat
$MCP_SERVER_NAME = "simulink-mcp-server"

# Additional Environment Variables (optional)
# Add any custom environment variables needed for your setup
$CUSTOM_ENV_VARS = @{}
# Example:
# $CUSTOM_ENV_VARS = @{
#     "MATLAB_LICENSE_FILE" = "C:\Licenses\matlab.lic"
#     "MY_CUSTOM_VAR" = "some_value"
# }

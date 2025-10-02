#!/usr/bin/env python3
"""
Manual test of the MCP server to debug the response format issue
"""

import asyncio
import json
import subprocess
import sys
from mcp_server import api_client

async def test_api_directly():
    """Test the API client directly"""
    print("=== Testing API Client Directly ===")
    try:
        result = await api_client.list_customers()
        print("✅ API call successful")
        print("Result:", json.dumps(result, indent=2))
        return True
    except Exception as e:
        print("❌ API call failed:", e)
        return False

def test_mcp_server_startup():
    """Test if the MCP server can start up"""
    print("\n=== Testing MCP Server Startup ===")
    try:
        # Try to start the MCP server and see if it initializes
        result = subprocess.run([
            "uv", "run", "python3", "-c", 
            "from mcp_server import server; print('MCP server imported successfully')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ MCP server imports successfully")
            print("Output:", result.stdout)
            return True
        else:
            print("❌ MCP server import failed")
            print("Error:", result.stderr)
            return False
    except Exception as e:
        print("❌ MCP server test failed:", e)
        return False

async def main():
    print("Customer JIRA Tracker MCP Server Debug Test")
    print("=" * 50)
    
    # Test 1: API client
    api_ok = await test_api_directly()
    
    # Test 2: MCP server startup
    server_ok = test_mcp_server_startup()
    
    print("\n=== Summary ===")
    print(f"API Client: {'✅ OK' if api_ok else '❌ FAILED'}")
    print(f"MCP Server: {'✅ OK' if server_ok else '❌ FAILED'}")
    
    if api_ok and server_ok:
        print("\n🎉 All tests passed! The MCP server should work.")
        print("\nIf you're still getting validation errors in Cursor, try:")
        print("1. Restart Cursor completely")
        print("2. Check Cursor's MCP logs for more details")
        print("3. Verify the MCP server is running: ps aux | grep mcp_server")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    asyncio.run(main())





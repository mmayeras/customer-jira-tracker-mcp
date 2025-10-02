#!/usr/bin/env python3
"""
Test script for Customer JIRA Tracker MCP server
"""

import os
import asyncio
import sys
from mcp_server import api_client

async def test_mcp_server():
    """Test the MCP server functionality"""
    
    print(f"🧪 Testing MCP server...")
    print(f"   API URL: {api_client.api_url}")
    print(f"   API Key: {api_client.api_key[:10]}..." if len(api_client.api_key) > 10 else f"   API Key: {api_client.api_key}")
    print()
    
    try:
        # Test 1: Health check
        print("1️⃣ Testing API health...")
        result = await api_client._make_request("GET", "/health")
        if result.get("status") == "healthy":
            print("   ✅ API is healthy")
        else:
            print(f"   ❌ API health check failed: {result}")
            return False
    except Exception as e:
        print(f"   ❌ API health check failed: {e}")
        print("   💡 Make sure the API server is running: ./run_local.sh")
        return False
    
    try:
        # Test 2: List customers
        print("2️⃣ Testing list customers...")
        result = await api_client.list_customers()
        print(f"   ✅ Found {len(result.get('customers', []))} customers")
        
        # Test 3: Add test customer
        print("3️⃣ Testing add customer tickets...")
        result = await api_client.add_customer_tickets(
            "Test Customer", 
            ["TEST-123", "TEST-456"], 
            "Test customer for MCP validation"
        )
        print(f"   ✅ Added tickets to Test Customer: {result['total_tickets']} tickets")
        
        # Test 4: Get customer tickets
        print("4️⃣ Testing get customer tickets...")
        result = await api_client.get_customer_tickets("Test Customer")
        print(f"   ✅ Retrieved {result['total_tickets']} tickets for Test Customer")
        
        # Test 5: Add comment
        print("5️⃣ Testing add ticket comment...")
        result = await api_client.add_ticket_comment(
            "Test Customer", 
            "TEST-123", 
            "Test comment from MCP server"
        )
        print(f"   ✅ Added comment to TEST-123")
        
        print()
        print("🎉 All tests passed! MCP server is working correctly.")
        print("   You can now use it in Cursor with the MCP configuration.")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("Customer JIRA Tracker MCP Server Test")
    print("=" * 40)
    
    success = await test_mcp_server()
    
    if success:
        print("\n✅ MCP server is ready for use in Cursor!")
        sys.exit(0)
    else:
        print("\n❌ MCP server test failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

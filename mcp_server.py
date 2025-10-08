#!/usr/bin/env python3
"""
MCP Server that bridges to the Customer JIRA Tracker HTTP API
This server runs in the container and exposes MCP tools
"""

import os
import json
import asyncio
import httpx
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# Configuration
API_URL = os.getenv("CUSTOMER_JIRA_API_URL", "http://localhost:8080")
API_KEY = os.getenv("CUSTOMER_JIRA_API_KEY", "local-dev-key")
SSL_VERIFY = os.getenv("CUSTOMER_JIRA_SSL_VERIFY", "true").lower() == "true"

class CustomerJiraTrackerAPI:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to the API"""
        url = f"{self.api_url}{endpoint}"
        
        async with httpx.AsyncClient(verify=SSL_VERIFY) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=self.headers, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=self.headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
                raise Exception(error_msg)
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")
    
    async def get_customer_tickets(self, customer_name: str) -> Dict:
        """Get all tickets for a customer"""
        endpoint = f"/api/customers/{customer_name}/tickets"
        return await self._make_request("GET", endpoint)
    
    async def add_customer_tickets(self, customer_name: str, ticket_keys: List[str], notes: Optional[str] = None) -> Dict:
        """Add tickets to a customer"""
        endpoint = f"/api/customers/{customer_name}/tickets"
        data = {"ticket_keys": ticket_keys}
        if notes:
            data["notes"] = notes
        return await self._make_request("POST", endpoint, data)
    
    async def add_ticket_comment(self, customer_name: str, ticket_key: str, comment: str) -> Dict:
        """Add a comment to a specific ticket"""
        endpoint = f"/api/customers/{customer_name}/tickets/{ticket_key}/comments"
        data = {"comment": comment}
        return await self._make_request("POST", endpoint, data)
    
    async def update_customer_notes(self, customer_name: str, notes: str) -> Dict:
        """Update customer notes"""
        endpoint = f"/api/customers/{customer_name}/notes"
        data = {"notes": notes}
        return await self._make_request("PUT", endpoint, data)
    
    async def remove_customer_tickets(self, customer_name: str, ticket_keys: List[str]) -> Dict:
        """Remove tickets from a customer"""
        endpoint = f"/api/customers/{customer_name}/tickets"
        return await self._make_request("DELETE", endpoint, ticket_keys)
    
    async def list_customers(self) -> Dict:
        """List all customers"""
        return await self._make_request("GET", "/api/customers")
    
    async def export_customer_data(self, customer_name: str, format: str = "markdown", include_jira: bool = False, save_file: bool = True) -> Dict:
        """Export customer data in specified format"""
        endpoint = f"/api/customers/{customer_name}/export"
        # Add query parameters to the URL
        query_params = f"?format={format}&include_jira={str(include_jira).lower()}&save_file={str(save_file).lower()}"
        endpoint += query_params
        return await self._make_request("GET", endpoint)
    

# Initialize the API client
api_client = CustomerJiraTrackerAPI(API_URL, API_KEY)

# Initialize MCP server
server = Server("customer-jira-tracker")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="get_customer_tickets",
                description="Get all tickets for a specific customer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer"
                        }
                    },
                    "required": ["customer_name"]
                }
            ),
            Tool(
                name="add_customer_tickets",
                description="Add tickets to a customer's tracking list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer"
                        },
                        "ticket_keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of JIRA ticket keys to add"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Optional notes about the customer"
                        }
                    },
                    "required": ["customer_name", "ticket_keys"]
                }
            ),
            Tool(
                name="add_ticket_comment",
                description="Add a comment to a specific ticket",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer"
                        },
                        "ticket_key": {
                            "type": "string",
                            "description": "JIRA ticket key"
                        },
                        "comment": {
                            "type": "string",
                            "description": "Comment text to add"
                        }
                    },
                    "required": ["customer_name", "ticket_key", "comment"]
                }
            ),
            Tool(
                name="update_customer_notes",
                description="Update notes for a customer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes to store for this customer"
                        }
                    },
                    "required": ["customer_name", "notes"]
                }
            ),
            Tool(
                name="remove_customer_tickets",
                description="Remove tickets from a customer's tracking list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer"
                        },
                        "ticket_keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of JIRA ticket keys to remove"
                        }
                    },
                    "required": ["customer_name", "ticket_keys"]
                }
            ),
            Tool(
                name="list_customers",
                description="List all customers with their ticket counts",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="export_customer_data",
                description="Export customer ticket data in Markdown format",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "Name of the customer to export"
                        },
                        "format": {
                            "type": "string",
                            "description": "Export format (default: markdown)",
                            "default": "markdown"
                        },
                        "include_jira": {
                            "type": "boolean",
                            "description": "Include JIRA information (requires JIRA integration)",
                            "default": False
                        },
                        "save_file": {
                            "type": "boolean",
                            "description": "Save export to file in customer data directory",
                            "default": true
                        }
                    },
                    "required": ["customer_name"]
                }
            )
        ]
    )

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_customer_tickets",
            description="Get all tickets for a specific customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer"
                    }
                },
                "required": ["customer_name"]
            }
        ),
        Tool(
            name="add_customer_tickets",
            description="Add tickets to a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer"
                    },
                    "ticket_keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of JIRA ticket keys to add"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes for the customer"
                    }
                },
                "required": ["customer_name", "ticket_keys"]
            }
        ),
        Tool(
            name="add_ticket_comment",
            description="Add a comment to a specific ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer"
                    },
                    "ticket_key": {
                        "type": "string",
                        "description": "JIRA ticket key"
                    },
                    "comment": {
                        "type": "string",
                        "description": "Comment text to add"
                    }
                },
                "required": ["customer_name", "ticket_key", "comment"]
            }
        ),
        Tool(
            name="update_customer_notes",
            description="Update customer notes",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer"
                    },
                    "notes": {
                        "type": "string",
                        "description": "New notes for the customer"
                    }
                },
                "required": ["customer_name", "notes"]
            }
        ),
        Tool(
            name="remove_customer_tickets",
            description="Remove tickets from a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer"
                    },
                    "ticket_keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of JIRA ticket keys to remove"
                    }
                },
                "required": ["customer_name", "ticket_keys"]
            }
        ),
        Tool(
            name="list_customers",
            description="List all customers with their ticket counts",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="export_customer_data",
            description="Export customer ticket data in Markdown format",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Name of the customer to export"
                    },
                    "format": {
                        "type": "string",
                        "description": "Export format (default: markdown)",
                        "default": "markdown"
                    },
                    "include_jira": {
                        "type": "boolean",
                        "description": "Include JIRA information (requires JIRA integration)",
                        "default": False
                    },
                    "save_file": {
                        "type": "boolean",
                        "description": "Save export to file in customer data directory",
                        "default": true
                    }
                },
                "required": ["customer_name"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]):
    """Handle tool calls"""
    try:
        if name == "get_customer_tickets":
            customer_name = arguments["customer_name"]
            result = await api_client.get_customer_tickets(customer_name)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "add_customer_tickets":
            customer_name = arguments["customer_name"]
            ticket_keys = arguments["ticket_keys"]
            notes = arguments.get("notes")
            result = await api_client.add_customer_tickets(customer_name, ticket_keys, notes)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "add_ticket_comment":
            customer_name = arguments["customer_name"]
            ticket_key = arguments["ticket_key"]
            comment = arguments["comment"]
            result = await api_client.add_ticket_comment(customer_name, ticket_key, comment)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "update_customer_notes":
            customer_name = arguments["customer_name"]
            notes = arguments["notes"]
            result = await api_client.update_customer_notes(customer_name, notes)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "remove_customer_tickets":
            customer_name = arguments["customer_name"]
            ticket_keys = arguments["ticket_keys"]
            result = await api_client.remove_customer_tickets(customer_name, ticket_keys)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_customers":
            result = await api_client.list_customers()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "export_customer_data":
            customer_name = arguments["customer_name"]
            format_type = arguments.get("format", "markdown")
            include_jira = arguments.get("include_jira", False)
            save_file = arguments.get("save_file", True)
            result = await api_client.export_customer_data(customer_name, format_type, include_jira, save_file)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point"""
    print(f"Starting Customer JIRA Tracker MCP Server")
    print(f"API URL: {API_URL}")
    print(f"API Key: {API_KEY[:10]}..." if len(API_KEY) > 10 else f"API Key: {API_KEY}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="customer-jira-tracker",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(tools_changed=False),
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())




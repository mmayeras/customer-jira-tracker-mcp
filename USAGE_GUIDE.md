# Customer JIRA Tracker - Usage Guide

This comprehensive guide covers everything you need to know about using the Customer JIRA Tracker with Cursor IDE integration.

## 📋 Table of Contents

1. [Overview](#overview)
2. [MCP Server Architecture](#mcp-server-architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Authentication & Security](#authentication--security)
6. [Using MCP Tools in Cursor](#using-mcp-tools-in-cursor)
7. [Export Functionality](#export-functionality)
8. [API Reference](#api-reference)
9. [Deployment Scenarios](#deployment-scenarios)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Usage](#advanced-usage)

## 🎯 Overview

The Customer JIRA Tracker is a sophisticated system that bridges JIRA ticket management with Cursor IDE through the Model Context Protocol (MCP). It provides seamless integration for tracking customer-specific JIRA tickets directly within your development environment.

### Key Components

- **HTTP API Server**: RESTful API for customer and ticket management
- **MCP Server**: Protocol bridge between Cursor and the HTTP API
- **Cursor Integration**: Direct tool access within Cursor IDE
- **Data Storage**: JSON-based persistent storage

## 🏗️ MCP Server Architecture

The MCP server (`mcp_server.py`) acts as a bridge between Cursor IDE and the HTTP API:

```
Cursor IDE → MCP Server → HTTP API → JSON Storage
```

### MCP Protocol Implementation

The server implements the MCP protocol correctly by:
- Returning unstructured content directly (not wrapped in `CallToolResult`)
- Handling SSL verification for different environments
- Providing proper error handling and validation
- Supporting both local and OpenShift deployments

### Tool Registration

All tools are registered using the `@server.call_tool()` decorator and return content in the format expected by the MCP protocol.

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.10+**: Required for MCP library compatibility
- **uv**: Modern Python package manager
- **Cursor IDE**: Latest version with MCP support
- **Podman** (optional): For containerized deployment

### Step 1: Clone and Install Dependencies

```bash
git clone <repository-url>
cd jiraTracker
uv sync
```

### Step 2: Configure MCP Integration

#### Option A: Interactive Setup (Recommended)

Run the interactive setup script:

```bash
./setup_mcp.sh
```

This script will:
- Check for required dependencies
- Prompt for configuration values (JIRA token, GitHub token, OpenShift URL/key)
- Prompt for SSL verification settings for both local and OpenShift environments
- Generate `~/.cursor/mcp.json` automatically
- Set up both local and OpenShift configurations

#### Option B: Manual Configuration

1. Copy the template:
   ```bash
   cp cursor-mcp-config.template.json ~/.cursor/mcp.json
   ```

2. Edit `~/.cursor/mcp.json` with your specific values:
   ```json
   {
     "mcpServers": {
       "customer-jira-tracker-local": {
         "command": "uv",
         "args": ["run", "--directory", "/path/to/jiraTracker", "mcp_server.py"],
         "env": {
           "CUSTOMER_JIRA_API_URL": "http://localhost:8080",
           "CUSTOMER_JIRA_API_KEY": "local-dev-key",
           "CUSTOMER_JIRA_SSL_VERIFY": "true"
         }
       }
     }
   }
   ```

### Step 3: Start the HTTP API Server

#### Local Development
```bash
uv run local_http_server.py
```

#### Containerized (Podman)
```bash
./run_local.sh
```

### Step 4: Restart Cursor IDE

After configuration, restart Cursor to load the MCP servers.

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `CUSTOMER_JIRA_API_URL` | HTTP API server URL | `http://localhost:8080` | Yes | `https://api.example.com` |
| `CUSTOMER_JIRA_API_KEY` | API authentication key | `local-dev-key` | Yes | `abc123def456` |
| `CUSTOMER_JIRA_SSL_VERIFY` | Enable/disable SSL verification | `true` | No | `false` |

### MCP Server Configuration

#### Local Development Configuration

```json
{
  "customer-jira-tracker-local": {
    "command": "uv",
    "args": ["run", "--directory", "${PROJECT_ROOT}", "mcp_server.py"],
    "env": {
      "CUSTOMER_JIRA_API_URL": "http://localhost:8080",
      "CUSTOMER_JIRA_API_KEY": "local-dev-key",
      "CUSTOMER_JIRA_SSL_VERIFY": "true"
    }
  }
}
```

#### OpenShift Production Configuration

```json
{
  "customer-jira-tracker-openshift": {
    "command": "uv",
    "args": ["run", "--directory", "${PROJECT_ROOT}", "mcp_server.py"],
    "env": {
      "CUSTOMER_JIRA_API_URL": "https://customer-jira-tracker-mcp.apps.example.com",
      "CUSTOMER_JIRA_API_KEY": "production-api-key-here",
      "CUSTOMER_JIRA_SSL_VERIFY": "false"
    }
  }
}
```

### SSL Verification Control

The `CUSTOMER_JIRA_SSL_VERIFY` environment variable controls SSL certificate verification:

#### When to Use `"true"` (Default)
- Production environments with valid SSL certificates
- Public APIs with proper certificate chains
- When security is a priority

#### When to Use `"false"`
- Development environments with self-signed certificates
- OpenShift deployments with internal certificates
- Testing scenarios where certificate validation isn't critical

**Security Note**: Only disable SSL verification in trusted environments.

## 🔐 Authentication & Security

### Local Development

#### No Authentication (Default)
```bash
# Start server without authentication
uv run local_http_server.py
```

#### With API Key Authentication
```bash
# Set environment variable
export CUSTOMER_JIRA_API_KEY="your-secret-key"

# Start server
uv run local_http_server.py
```

### OpenShift Production

#### Required Authentication
```bash
# Set production API key
export CUSTOMER_JIRA_API_KEY="production-secret-key"

# Deploy to OpenShift
cd openshift
oc apply -f deployment.yaml
```

#### Secret Management
```yaml
# OpenShift Secret
apiVersion: v1
kind: Secret
metadata:
  name: customer-jira-api-key
type: Opaque
stringData:
  api-key: "your-production-api-key"
```

### Security Best Practices

1. **Use Strong API Keys**: Generate cryptographically secure keys
2. **Rotate Keys Regularly**: Change API keys periodically
3. **Environment Separation**: Use different keys for dev/staging/prod
4. **SSL in Production**: Always use HTTPS in production environments
5. **Monitor Access**: Log and monitor API key usage

## 🛠️ Using MCP Tools in Cursor

Once configured, the following MCP tools are available in Cursor:

### Customer Management Tools

#### List All Customers
```python
# In Cursor, use the MCP tool directly
mcp_customer-jira-tracker-local_list_customers
```

**Response:**
```json
{
  "customers": [
    {
      "customer": "ACME Corp",
      "total_tickets": 3,
      "last_updated": "2025-10-02T08:53:34.047888"
    }
  ]
}
```

#### Get Customer Tickets
```python
mcp_customer-jira-tracker-local_get_customer_tickets
  customer_name: "ACME Corp"
```

**Response:**
```json
{
  "customer": "ACME Corp",
  "tickets": [
    {
      "key": "AAA-1234",
      "added_date": "2025-10-02T07:16:20.392854",
      "comments": []
    }
  ],
  "total_tickets": 1,
  "total_comments": 0
}
```

### Ticket Management Tools

#### Add Tickets to Customer
```python
mcp_customer-jira-tracker-local_add_customer_tickets
  customer_name: "ACME Corp"
  ticket_keys: ["JIRA-123", "JIRA-456"]
  notes: "Initial ticket batch"
```

#### Add Comment to Ticket
```python
mcp_customer-jira-tracker-local_add_ticket_comment
  customer_name: "ACME Corp"
  ticket_key: "JIRA-123"
  comment: "Working on this issue"
```

#### Remove Tickets from Customer
```python
mcp_customer-jira-tracker-local_remove_customer_tickets
  customer_name: "ACME Corp"
  ticket_keys: ["JIRA-456"]
```

#### Update Customer Notes
```python
mcp_customer-jira-tracker-local_update_customer_notes
  customer_name: "ACME Corp"
  notes: "Updated customer information"
```

## 📊 Export Functionality

The Customer JIRA Tracker includes powerful export capabilities to generate comprehensive Markdown reports of customer ticket data.

### Export Features

- **Markdown Format**: Clean, readable Markdown tables with proper formatting
- **JIRA Integration**: Optional JIRA data (Status, Priority, Assignee, Last Updated)
- **Customer Summary**: Total tickets, comments, and last updated information
- **Comments Section**: Detailed ticket comments with timestamps
- **File Storage**: Automatic saving to customer data directory with timestamps

### MCP Export Tool

#### Export Customer Data
```python
mcp_customer-jira-tracker-local_export_customer_data
  customer_name: "ACME Corp"
  format: "markdown"
  include_jira: true
  save_file: true
```

**Parameters:**
- `customer_name` (required): Name of the customer to export
- `format` (optional): Export format, defaults to "markdown"
- `include_jira` (optional): Include JIRA information, defaults to false
- `save_file` (optional): Save to file, defaults to true

**Response:**
```json
{
  "customer": "ACME Corp",
  "format": "markdown",
  "content": "# Customer: ACME Corp\n\n**Last Updated:** 2025-10-02T11:40:36.101729\n...",
  "saved_to": "customer_jira_data/ACME_Corp_export_20251002_115337.md",
  "include_jira": true
}
```

### Export Output Format

The export generates a comprehensive Markdown document with:

1. **Header Section**: Customer name, last updated, ticket counts
2. **Notes Section**: Customer notes (if any)
3. **Tickets Table**: 
   - Basic: Ticket Key, Added Date, Comments count
   - With JIRA: Adds Status, Priority, Assignee, Last Updated columns
4. **Comments Section**: Detailed comments for each ticket with timestamps

**Example Output:**
```markdown
# Customer: ACME Corp

**Last Updated:** 2025-10-02T11:40:36.101729
**Total Tickets:** 2
**Total Comments:** 1

## Notes
Customer notes here

## Tickets

| Ticket Key | Added Date | Comments | Status | Priority | Assignee | Last Updated |
| --- | --- | --- | --- | --- | --- | --- |
| `AAA-1234` | 2025-10-02 | 1 | N/A (MCP Integration Pending) | N/A (MCP Integration Pending) | N/A (MCP Integration Pending) | N/A (MCP Integration Pending) |
| `BBB-5678` | 2025-10-02 | 0 | N/A (MCP Integration Pending) | N/A (MCP Integration Pending) | N/A (MCP Integration Pending) | N/A (MCP Integration Pending) |

## Comments

### AAA-1234
**2025-10-02T11:38:25**

This is a comment for the ticket
```

### File Storage

Export files are automatically saved to the customer data directory with the naming convention:
```
{customer_name}_export_{timestamp}.md
```

Example: `ACME_Corp_export_20251002_115337.md`

## 📚 API Reference

### HTTP API Endpoints

#### Customer Management

**GET /api/customers**
- List all customers
- **Response**: Array of customer objects

**GET /api/customers/{customer_name}/tickets**
- Get tickets for a specific customer
- **Parameters**: `customer_name` (path)
- **Response**: Customer object with tickets

**POST /api/customers/{customer_name}/tickets**
- Add tickets to a customer
- **Parameters**: `customer_name` (path)
- **Body**: `{"ticket_keys": ["JIRA-123"], "notes": "optional"}`
- **Response**: Updated customer object

**DELETE /api/customers/{customer_name}/tickets**
- Remove tickets from a customer
- **Parameters**: `customer_name` (path)
- **Body**: `{"ticket_keys": ["JIRA-123"]}`
- **Response**: Updated customer object

#### Ticket Operations

**POST /api/customers/{customer_name}/tickets/{ticket_key}/comments**
- Add comment to a ticket
- **Parameters**: `customer_name`, `ticket_key` (path)
- **Body**: `{"comment": "comment text"}`
- **Response**: Updated customer object

**PUT /api/customers/{customer_name}**
- Update customer notes
- **Parameters**: `customer_name` (path)
- **Body**: `{"notes": "updated notes"}`
- **Response**: Updated customer object

### MCP Tool Parameters

#### list_customers
- **Parameters**: None
- **Returns**: List of all customers with ticket counts

#### get_customer_tickets
- **Parameters**: `customer_name` (string)
- **Returns**: Customer object with all tickets

#### add_customer_tickets
- **Parameters**: 
  - `customer_name` (string)
  - `ticket_keys` (array of strings)
  - `notes` (string, optional)
- **Returns**: Updated customer object

#### add_ticket_comment
- **Parameters**:
  - `customer_name` (string)
  - `ticket_key` (string)
  - `comment` (string)
- **Returns**: Updated customer object

#### remove_customer_tickets
- **Parameters**:
  - `customer_name` (string)
  - `ticket_keys` (array of strings)
- **Returns**: Updated customer object

#### update_customer_notes
- **Parameters**:
  - `customer_name` (string)
  - `notes` (string)
- **Returns**: Updated customer object

## 🚀 Deployment Scenarios

### Local Development

1. **Start HTTP API Server**:
   ```bash
   uv run local_http_server.py
   ```

2. **Configure MCP**:
   ```bash
   ./setup_mcp.sh
   ```

3. **Restart Cursor IDE**

### OpenShift Production

1. **Deploy HTTP API**:
   ```bash
   cd openshift
   oc apply -f deployment.yaml
   oc apply -f service.yaml
   oc apply -f route.yaml
   ```

2. **Configure MCP for OpenShift**:
   ```json
   {
     "customer-jira-tracker-openshift": {
       "command": "uv",
       "args": ["run", "--directory", "${PROJECT_ROOT}", "mcp_server.py"],
       "env": {
         "CUSTOMER_JIRA_API_URL": "https://your-openshift-route.com",
         "CUSTOMER_JIRA_API_KEY": "your-production-key",
         "CUSTOMER_JIRA_SSL_VERIFY": "false"
       }
     }
   }
   ```

3. **Restart Cursor IDE**

### Docker/Podman Deployment

1. **Build Image**:
   ```bash
   podman build -t customer-jira-tracker .
   ```

2. **Run Container**:
   ```bash
   podman run -d -p 8080:8080 \
     -e CUSTOMER_JIRA_API_KEY="your-key" \
     customer-jira-tracker
   ```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. MCP Tools Not Available

**Symptoms**: Tools don't appear in Cursor
**Solutions**:
- Restart Cursor IDE after configuration
- Check `~/.cursor/mcp.json` syntax
- Verify MCP server is running: `ps aux | grep mcp_server`
- Check Cursor logs: `~/Library/Application Support/Cursor/logs/`

#### 2. SSL Certificate Errors

**Symptoms**: `[SSL: CERTIFICATE_VERIFY_FAILED]` errors
**Solutions**:
- Set `CUSTOMER_JIRA_SSL_VERIFY=false` for self-signed certificates
- Ensure HTTPS URL is used for OpenShift
- Check certificate validity

#### 3. API Connection Errors

**Symptoms**: `Request failed` or connection timeouts
**Solutions**:
- Verify `CUSTOMER_JIRA_API_URL` is correct
- Check if HTTP API server is running
- Validate API key authentication
- Test API directly: `curl -H "Authorization: Bearer key" http://localhost:8080/api/customers`

#### 4. Validation Errors

**Symptoms**: `20 validation errors for CallToolResult`
**Solutions**:
- Ensure MCP server returns content directly (not wrapped in CallToolResult)
- Check MCP protocol compatibility
- Verify MCP library version

#### 5. Authentication Failures

**Symptoms**: `401 Unauthorized` or `403 Forbidden`
**Solutions**:
- Verify API key is correct
- Check API key format (Bearer token)
- Ensure API key is set in environment variables

### Debug Mode

#### Enable MCP Server Debug Output
```bash
# Run MCP server with verbose output
uv run mcp_server.py
```

#### Test API Connectivity
```bash
# Test local API
curl -H "Authorization: Bearer local-dev-key" http://localhost:8080/api/customers

# Test OpenShift API
curl -H "Authorization: Bearer your-key" https://your-openshift-url.com/api/customers
```

#### Check MCP Server Logs
```bash
# Find Cursor MCP logs
find ~/Library/Application\ Support/Cursor/logs -name "*mcp*" -type f

# View latest MCP logs
tail -f ~/Library/Application\ Support/Cursor/logs/*/window1/exthost/anysphere.cursor-mcp/*.log
```

## 🔧 Advanced Usage

### Custom API Keys

#### Generate Secure API Key
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(f"API Key: {api_key}")
```

#### Rotate API Keys
1. Generate new key
2. Update configuration
3. Restart services
4. Update Cursor MCP configuration

### Data Management

#### Backup Customer Data
```bash
# Backup JSON data
cp customer_jira_data/*.json backup/
```

#### Restore Customer Data
```bash
# Restore from backup
cp backup/*.json customer_jira_data/
```

### Performance Optimization

#### Connection Pooling
The MCP server uses `httpx.AsyncClient` with connection pooling for optimal performance.

#### Caching
Consider implementing caching for frequently accessed customer data.

### Monitoring

#### Health Checks
```bash
# Check API health
curl http://localhost:8080/health

# Check MCP server
ps aux | grep mcp_server
```

#### Logging
- MCP server logs: Cursor application logs
- API server logs: Console output or container logs
- Error tracking: Monitor for validation and connection errors

## 📞 Support

### Getting Help

1. **Check Documentation**: Review this guide and README.md
2. **Troubleshooting**: Follow the troubleshooting section
3. **Debug Mode**: Enable debug output for detailed information
4. **Community**: Open an issue in the repository

### Reporting Issues

When reporting issues, include:
- Cursor version
- Python version
- MCP configuration
- Error messages
- Steps to reproduce

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

This guide covers all aspects of using the Customer JIRA Tracker with Cursor IDE. For additional information, refer to the README.md or open an issue in the repository.
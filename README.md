# Customer JIRA Tracker

A comprehensive JIRA ticket tracking system with MCP (Model Context Protocol) integration for Cursor IDE. This system allows you to track customer-specific JIRA tickets with full CRUD operations and seamless integration with Cursor's AI assistant.

## 🚀 Features

- **Customer Management**: Create and manage customer profiles
- **Ticket Tracking**: Add, remove, and track JIRA tickets per customer
- **Comment System**: Add comments to individual tickets
- **Export Functionality**: Export customer data to Markdown format with JIRA integration
- **MCP Integration**: Direct integration with Cursor IDE via MCP protocol
- **Dual Deployment**: Support for both local development and OpenShift production
- **Flexible Authentication**: API key-based authentication with SSL verification control

## 🏗️ Architecture

The system consists of three main components:

1. **HTTP API Server** (`local_http_server.py` / OpenShift deployment)
   - FastAPI-based REST API
   - Customer and ticket management endpoints
   - JSON file-based data storage
   - API key authentication

2. **MCP Server** (`mcp_server.py`)
   - Bridges Cursor IDE to the HTTP API
   - Exposes MCP tools for customer and ticket operations
   - Handles SSL verification for different environments
   - Supports both local and OpenShift deployments

3. **Cursor Integration** (`cursor-mcp-config.json`)
   - Configuration for Cursor IDE
   - Environment-specific settings
   - SSL verification control

## 🚀 Quick Start

### Prerequisites

- Podman (for containerized deployment)
- Cursor IDE

### 1. Clone and Setup

```bash
git clone <repository-url>
cd jiraTracker
```

### 2. Configure MCP Integration

#### Option A: Interactive Setup (Recommended)
```bash
./setup_mcp.sh
```

The interactive setup will prompt you for:
- JIRA Personal Token
- GitHub Personal Access Token  
- OpenShift API URL
- OpenShift API Key
- SSL verification settings for both local and OpenShift environments

#### Option B: Manual Configuration
```bash
cp cursor-mcp-config.template.json ~/.cursor/mcp.json
# Edit ~/.cursor/mcp.json with your specific values
```

### 3. Start the Services

#### Containerized Local Development (Recommended)
```bash
./run_local.sh
```

This will:
- Build the HTTP API server container
- Build the MCP server container
- Start the HTTP API server
- Configure MCP to use containerized services

### 4. Restart Cursor IDE

After configuration, restart Cursor to load the MCP servers.

## 📊 Export Functionality

The Customer JIRA Tracker includes powerful export capabilities to generate Markdown reports of customer ticket data.

### Export Features

- **Markdown Format**: Clean, readable Markdown tables
- **JIRA Integration**: Optional JIRA data (Status, Priority, Assignee, Last Updated)
- **Customer Summary**: Total tickets, comments, and last updated information
- **Comments Section**: Detailed ticket comments with timestamps
- **File Storage**: Automatic saving to customer data directory

### Export API Endpoint

```bash
GET /api/customers/{customer_name}/export
```

**Parameters:**
- `format` (default: "markdown") - Export format
- `include_jira` (default: false) - Include JIRA information
- `save_file` (default: true) - Save to file in customer data directory

**Example Usage:**

```bash
# Basic export
curl "http://localhost:8080/api/customers/AA/export"

# Export with JIRA data
curl "http://localhost:8080/api/customers/AA/export?include_jira=true"

# Export without saving to file
curl "http://localhost:8080/api/customers/AA/export?save_file=false"
```

### MCP Tool Usage

In Cursor IDE, use the `export_customer_data` tool:

```json
{
  "customer_name": "AA",
  "format": "markdown",
  "include_jira": true,
  "save_file": true
}
```

### Export Output Example

```markdown
# Customer: AA

**Last Updated:** 2025-10-02T11:40:36.101729
**Total Tickets:** 2
**Total Comments:** 1

## Notes
Initial ticket for AA customer

## Tickets

| Ticket Key | Added Date | Comments | Status | Priority | Assignee | Last Updated |
| --- | --- | --- | --- | --- | --- | --- |
| `RFE-1234` | 2025-10-02 | 1 | N/A (MCP Integration Pending) | N/A (MCP Integration Pending) | N/A (MCP Integration Pending) | N/A (MCP Integration Pending) |

## Comments

### RFE-1234
**2025-10-02T11:38:25**

This is a test comment for the export functionality
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CUSTOMER_JIRA_API_URL` | HTTP API server URL | `http://localhost:8080` | Yes |
| `CUSTOMER_JIRA_API_KEY` | API authentication key | `local-dev-key` | Yes |
| `CUSTOMER_JIRA_SSL_VERIFY` | Enable/disable SSL verification | `true` | No |

### MCP Server Configuration

The MCP server supports two deployment modes using containerized services:

#### Local Development (Containerized)
```json
{
  "customer-jira-tracker-local": {
    "command": "podman",
    "args": [
      "run", "-i", "--name=customer-jira-tracker-client",
      "--network=host",
      "-e", "CUSTOMER_JIRA_API_URL=http://localhost:8080",
      "-e", "CUSTOMER_JIRA_API_KEY=local-dev-key",
      "-e", "CUSTOMER_JIRA_SSL_VERIFY=false",
      "localhost/customer-jira-tracker-client:local"
    ],
    "env": {
      "CUSTOMER_JIRA_API_URL": "http://localhost:8080",
      "CUSTOMER_JIRA_API_KEY": "local-dev-key",
      "CUSTOMER_JIRA_SSL_VERIFY": "false"
    }
  }
}
```

#### OpenShift Production (Containerized)
```json
{
  "customer-jira-tracker-openshift": {
    "command": "podman",
    "args": [
      "run", "-i", "--name=customer-jira-tracker-client-openshift",
      "-e", "CUSTOMER_JIRA_API_URL=https://your-openshift-url.com",
      "-e", "CUSTOMER_JIRA_API_KEY=your-production-key",
      "-e", "CUSTOMER_JIRA_SSL_VERIFY=true",
      "quay.io/your-org/customer-jira-tracker:latest"
    ],
    "env": {
      "CUSTOMER_JIRA_API_URL": "https://your-openshift-url.com",
      "CUSTOMER_JIRA_API_KEY": "your-production-key",
      "CUSTOMER_JIRA_SSL_VERIFY": "true"
    }
  }
}
```

## 🔐 Authentication & Security

### Local Development
- **Default**: No authentication required
- **Optional**: Set `CUSTOMER_JIRA_API_KEY` for API key authentication
- **SSL**: Not required for local development

### OpenShift Production
- **Required**: API key authentication via `CUSTOMER_JIRA_API_KEY`
- **SSL**: HTTPS required, but verification can be disabled for self-signed certificates
- **Security**: Use strong, unique API keys

### SSL Verification Control

The `CUSTOMER_JIRA_SSL_VERIFY` environment variable controls SSL certificate verification:

- `"true"` (default): Verify SSL certificates (recommended for production)
- `"false"`: Skip SSL verification (useful for self-signed certificates in development)

## 📚 Available MCP Tools

Once configured, the following tools are available in Cursor:

### Customer Management
- `list_customers` - List all customers with ticket counts
- `get_customer_tickets` - Get all tickets for a specific customer

### Ticket Operations
- `add_customer_tickets` - Add tickets to a customer
- `remove_customer_tickets` - Remove tickets from a customer
- `add_ticket_comment` - Add a comment to a specific ticket

### Customer Updates
- `update_customer_notes` - Update customer notes

## 🛠️ Development

### Project Structure
```
jiraTracker/
├── Dockerfile                # Main container image (OpenShift HTTP server)
├── Dockerfile.mcp            # MCP server container image
├── mcp_server.py             # MCP server implementation
├── local_http_server.py      # HTTP API server (for local development)
├── cursor-mcp-config.json    # Cursor MCP configuration
├── cursor-mcp-config.template.json  # Template for manual setup
├── setup_mcp.sh             # Interactive setup script
├── run_local.sh             # Local development runner (containerized)
├── openshift/               # OpenShift deployment files
│   ├── http_server.py       # OpenShift HTTP server
│   ├── deployment.yaml      # Kubernetes deployment
│   └── ...
└── customer_jira_data/      # JSON data storage
```

### Container Images

The project uses two main container images:

1. **HTTP API Server** (`customer-jira-tracker-server:local`)
   - Based on `Dockerfile.server`
   - Runs the HTTP API server
   - Used for both local development and OpenShift production

2. **MCP Client** (`customer-jira-tracker-client:local`)
   - Based on `Dockerfile.client`
   - Runs the MCP server that bridges to the HTTP API
   - Used by Cursor IDE for MCP integration

### Building Container Images
```bash
# Build HTTP API server image
podman build -t customer-jira-tracker-server:local -f Dockerfile.server .

# Build MCP client image
podman build -t customer-jira-tracker-client:local -f Dockerfile.client .

# Build for OpenShift production
podman build -t quay.io/your-org/customer-jira-tracker:latest -f Dockerfile .
```

## 🚀 Deployment

### Local Development (Containerized)
1. Run `./run_local.sh` to start HTTP API server container
2. MCP server runs automatically when Cursor connects
3. Configure MCP with local settings (done automatically by setup script)
4. Restart Cursor IDE

### OpenShift Production
1. Deploy using the provided OpenShift manifests
2. Build and push container images to your registry
3. Configure MCP with production settings
4. Set `CUSTOMER_JIRA_SSL_VERIFY=false` for self-signed certificates (default is `true`)
5. Restart Cursor IDE

## 🔍 Troubleshooting

### Common Issues

1. **MCP Tools Not Available**
   - Ensure Cursor is restarted after configuration
   - Check `~/.cursor/mcp.json` syntax
   - Verify MCP server is running

2. **SSL Certificate Errors**
   - Set `CUSTOMER_JIRA_SSL_VERIFY=false` for self-signed certificates (default is `true`)
   - Ensure HTTPS URL is used for OpenShift

3. **API Connection Errors**
   - Verify `CUSTOMER_JIRA_API_URL` is correct
   - Check if HTTP API server is running
   - Validate API key authentication

4. **Validation Errors**
   - Ensure MCP server returns content directly (not wrapped in CallToolResult)
   - Check MCP protocol compatibility

### Debug Mode
```bash
# Check container status
podman ps -a

# View HTTP API server logs
podman logs customer-jira-tracker-local

# Test API connectivity
curl -H "Authorization: Bearer your-api-key" http://localhost:8080/api/customers

# Test MCP server manually
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}' | podman run --rm -i -e CUSTOMER_JIRA_API_URL=http://host.containers.internal:8080 -e CUSTOMER_JIRA_API_KEY=local-dev-key -e CUSTOMER_JIRA_SSL_VERIFY=false localhost/customer-jira-tracker-client:local
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the USAGE_GUIDE.md for detailed instructions
3. Open an issue in the repository
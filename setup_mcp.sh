#!/bin/bash

# Setup script for Customer JIRA Tracker MCP integration

echo "🚀 Setting up Customer JIRA Tracker MCP integration..."
echo ""
echo "This script will configure MCP integration for Cursor IDE with:"
echo "  • JIRA and GitHub MCP servers"
echo "  • Local and OpenShift Customer JIRA Tracker servers"
echo "  • SSL verification settings for both environments"
echo "  • Automatic generation of ~/.cursor/mcp.json"
echo ""

# Configuration
PROJECT_ROOT="$(pwd)"
MCP_CONFIG="$HOME/.cursor/mcp.json"
BACKUP_CONFIG="$HOME/.cursor/mcp.json.backup.$(date +%Y%m%d_%H%M%S)"

# Check if Cursor MCP config exists
if [ -f "$MCP_CONFIG" ]; then
    echo "📋 Found existing MCP config, creating backup..."
    cp "$MCP_CONFIG" "$BACKUP_CONFIG"
    echo "✅ Backup created: $BACKUP_CONFIG"
fi

# Prompt for configuration values
echo "🔧 MCP Configuration Setup"
echo "=========================="

# Get project root
echo "Project root: $PROJECT_ROOT"

# Get JIRA personal token
if [ -z "$JIRA_PERSONAL_TOKEN" ]; then
    echo -n "Enter your JIRA Personal Access Token (or press Enter to skip): "
    read -r JIRA_PERSONAL_TOKEN
fi

# Get GitHub personal access token
if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo -n "Enter your GitHub Personal Access Token (or press Enter to skip): "
    read -r GITHUB_PERSONAL_ACCESS_TOKEN
fi

# Get OpenShift configuration
if [ -z "$OPENSHIFT_API_URL" ]; then
    echo -n "Enter your OpenShift API URL (or press Enter to use default): "
    read -r OPENSHIFT_API_URL
    if [ -z "$OPENSHIFT_API_URL" ]; then
        OPENSHIFT_API_URL="https://customer-jira-tracker-mcp.apps.your-domain.com"
    fi
fi

if [ -z "$OPENSHIFT_API_KEY" ]; then
    echo -n "Enter your OpenShift API Key (or press Enter to use default): "
    read -r OPENSHIFT_API_KEY
    if [ -z "$OPENSHIFT_API_KEY" ]; then
        OPENSHIFT_API_KEY="your-openshift-api-key-here"
    fi
fi

# Prompt for SSL verification settings
echo ""
echo "🔒 SSL Verification Settings:"
echo "  - Local development: Usually 'true' (verify SSL certificates)"
echo "  - OpenShift with self-signed certificates: Usually 'false'"
echo ""

echo -n "Enable SSL verification for local development? (y/N): "
read -r SSL_VERIFY_LOCAL
if [[ "$SSL_VERIFY_LOCAL" =~ ^[Yy]$ ]]; then
    SSL_VERIFY_LOCAL="true"
else
    SSL_VERIFY_LOCAL="false"
fi

echo -n "Enable SSL verification for OpenShift? (y/N): "
read -r SSL_VERIFY_OPENSHIFT
if [[ "$SSL_VERIFY_OPENSHIFT" =~ ^[Yy]$ ]]; then
    SSL_VERIFY_OPENSHIFT="true"
else
    SSL_VERIFY_OPENSHIFT="false"
fi

# Generate MCP configuration from template
echo "📝 Generating MCP configuration..."

# Create temporary file with substitutions
cat > "$MCP_CONFIG" << EOF
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "/opt/podman/bin/podman",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "JIRA_URL",
        "-e", "JIRA_PERSONAL_TOKEN",
        "-e", "JIRA_SSL_VERIFY",
        "ghcr.io/sooperset/mcp-atlassian"
      ],
      "env": {
        "JIRA_URL": "https://issues.redhat.com",
        "JIRA_PERSONAL_TOKEN": "$JIRA_PERSONAL_TOKEN",
        "JIRA_SSL_VERIFY": "true"
      }
    },
    "customer-jira-tracker-local": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "$PROJECT_ROOT",
        "mcp_server.py"
      ],
      "env": {
        "CUSTOMER_JIRA_API_URL": "http://localhost:8080",
        "CUSTOMER_JIRA_API_KEY": "local-dev-key",
        "CUSTOMER_JIRA_SSL_VERIFY": "$SSL_VERIFY_LOCAL"
      }
    },
    "customer-jira-tracker-openshift": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "$PROJECT_ROOT",
        "mcp_server.py"
      ],
      "env": {
        "CUSTOMER_JIRA_API_URL": "$OPENSHIFT_API_URL",
        "CUSTOMER_JIRA_API_KEY": "$OPENSHIFT_API_KEY",
        "CUSTOMER_JIRA_SSL_VERIFY": "$SSL_VERIFY_OPENSHIFT"
      }
    },
    "github": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_PERSONAL_ACCESS_TOKEN"
      }
    }
  }
}
EOF

echo "✅ MCP configuration generated at $MCP_CONFIG"

# Check if API server is running
echo "🔍 Checking if API server is running..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ API server is running at http://localhost:8080"
else
    echo "⚠️  API server is not running. Please start it first:"
    echo "   ./run_local.sh"
    echo ""
    echo "   Or run manually:"
    echo "   python local_http_server.py"
fi

# Check if MCP server dependencies are installed
echo "🔍 Checking MCP server dependencies..."
if uv run --directory . python -c "import mcp, httpx, fastapi" 2>/dev/null; then
    echo "✅ MCP server dependencies are installed"
else
    echo "⚠️  Installing MCP server dependencies..."
    uv pip install -r requirements.txt
fi

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Start the API server: ./run_local.sh"
echo "2. Restart Cursor to load the MCP configuration"
echo "3. Test with: 'list customers' or 'add tickets PROJ-123 to Acme Corp'"
echo ""
echo "📚 For detailed usage, see USAGE_GUIDE.md"

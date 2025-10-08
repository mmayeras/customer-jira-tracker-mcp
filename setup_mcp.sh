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

echo -n "Enable SSL verification for local development? (Y/n): "
read -r SSL_VERIFY_LOCAL
if [[ "$SSL_VERIFY_LOCAL" =~ ^[Nn]$ ]]; then
    SSL_VERIFY_LOCAL="false"
else
    SSL_VERIFY_LOCAL="true"
fi

echo -n "Enable SSL verification for OpenShift? (Y/n): "
read -r SSL_VERIFY_OPENSHIFT
if [[ "$SSL_VERIFY_OPENSHIFT" =~ ^[Nn]$ ]]; then
    SSL_VERIFY_OPENSHIFT="false"
else
    SSL_VERIFY_OPENSHIFT="true"
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
      "command": "podman",
      "args": [
        "run",
        "-i",
        "--rm",
        "--restart=unless-stopped",
        "--name=customer-jira-tracker-local",
        "-p", "8080:8080",
        "-v", "$PROJECT_ROOT/customer_jira_data:/data",
        "-e", "CUSTOMER_JIRA_STORAGE=/data",
        "-e", "CUSTOMER_JIRA_API_URL=http://localhost:8080",
        "-e", "CUSTOMER_JIRA_API_KEY=local-dev-key",
        "-e", "CUSTOMER_JIRA_SSL_VERIFY=$SSL_VERIFY_LOCAL",
        "customer-jira-tracker:local"
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

# Check if port 8080 is available
echo "🔍 Checking if port 8080 is available..."
if lsof -i :8080 > /dev/null 2>&1; then
    echo "⚠️  Port 8080 is already in use. The container will use this port."
    echo "   If you have conflicts, stop other services on port 8080 first."
else
    echo "✅ Port 8080 is available for the container"
fi

# Check if container image exists
echo "🔍 Checking if container image exists..."
if podman image exists customer-jira-tracker:local 2>/dev/null; then
    echo "✅ Container image customer-jira-tracker:local exists"
else
    echo "⚠️  Building container image..."
    podman build -f Dockerfile.local -t customer-jira-tracker:local .
    echo "✅ Container image built successfully"
fi

# Check if container is already running
echo "🔍 Checking if container is already running..."
if podman ps --format "{{.Names}}" | grep -q "customer-jira-tracker-local"; then
    echo "✅ Container is already running"
    echo "   To restart: podman restart customer-jira-tracker-local"
    echo "   To stop: podman stop customer-jira-tracker-local"
else
    echo "ℹ️  Container will start automatically when Cursor connects to MCP"
    echo "   To start manually: podman run -d --name customer-jira-tracker-local --restart=unless-stopped -p 8080:8080 -v $PROJECT_ROOT/customer_jira_data:/data customer-jira-tracker:local"
fi

echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Restart Cursor to load the MCP configuration"
echo "2. The container will start automatically when Cursor connects"
echo "3. Test with: 'list customers' or 'add tickets PROJ-123 to Acme Corp'"
echo ""
echo "🔧 Container Management:"
echo "   View logs: podman logs customer-jira-tracker-local"
echo "   Restart: podman restart customer-jira-tracker-local"
echo "   Stop: podman stop customer-jira-tracker-local"
echo "   Remove: podman rm customer-jira-tracker-local"
echo ""
echo "📚 For detailed usage, see USAGE_GUIDE.md"

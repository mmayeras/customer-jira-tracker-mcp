#!/bin/bash

# Customer JIRA Tracker - Local Development Script
# This script runs the API server locally using Podman

set -e

echo "🚀 Starting Customer JIRA Tracker API locally..."

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed. Please install Podman first."
    exit 1
fi

# Check if image exists, build only if needed
if ! podman image exists customer-jira-tracker-server:local 2>/dev/null || [[ "$1" == "--rebuild" ]]; then
    echo "📦 Building local server container image..."
    podman build -t customer-jira-tracker-server:local -f Dockerfile.server .
else
    echo "✅ Server container image already exists, skipping build"
    echo "   Use --rebuild to force rebuild the image"
fi

# Create data directory if it doesn't exist
mkdir -p ./customer_jira_data

# Stop and remove existing container if it exists
if podman ps -a --format "{{.Names}}" | grep -q "customer-jira-tracker-server"; then
    echo "🛑 Stopping existing container..."
    podman stop customer-jira-tracker-server 2>/dev/null || true
    podman rm customer-jira-tracker-server 2>/dev/null || true
fi

# Run the container
echo "🏃 Running server container..."
podman run -d \
  --name customer-jira-tracker-server \
  --restart=unless-stopped \
  -p 8080:8080 \
  -v ./customer_jira_data:/data \
  -e CUSTOMER_JIRA_STORAGE=/data \
  -e PORT=8080 \
  -e REQUIRE_AUTH=false \
  -e CUSTOMER_JIRA_API_KEY=local-dev-key \
  customer-jira-tracker-server:local

# Wait for the container to start
echo "⏳ Waiting for API to start..."
sleep 3

# Check if the API is running
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ API is running at http://localhost:8080"
    echo "📊 Health check: http://localhost:8080/health"
    echo "📚 API docs: http://localhost:8080/docs"
    echo ""
    echo "🔧 To use with Cursor MCP:"
    echo "1. Copy the configuration from cursor-mcp-config.json to your Cursor MCP settings"
    echo "2. Update the API URL if needed"
    echo "3. Restart Cursor"
    echo ""
    echo "🔧 Container Management:"
    echo "   View logs: podman logs customer-jira-tracker-server"
    echo "   Restart: podman restart customer-jira-tracker-server"
    echo "   Stop: podman stop customer-jira-tracker-server"
    echo "   Remove: podman rm customer-jira-tracker-server"
    echo "   Rebuild: ./run_local.sh --rebuild"
else
    echo "❌ Failed to start API. Check logs with: podman logs customer-jira-tracker-server"
    exit 1
fi

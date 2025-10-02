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

# Build the local image
echo "📦 Building local container image..."
podman build -t customer-jira-tracker-local -f Dockerfile.local .

# Create data directory if it doesn't exist
mkdir -p ./customer_jira_data

# Run the container
echo "🏃 Running container..."
podman run -d \
  --name customer-jira-tracker-local \
  -p 8080:8080 \
  -v ./customer_jira_data:/data \
  -e CUSTOMER_JIRA_STORAGE=/data \
  -e PORT=8080 \
  -e REQUIRE_AUTH=false \
  -e CUSTOMER_JIRA_TRACKER_API_KEY=local-dev-key \
  customer-jira-tracker-local

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
    echo "🛑 To stop the API: podman stop customer-jira-tracker-local"
    echo "🗑️  To remove the container: podman rm customer-jira-tracker-local"
else
    echo "❌ Failed to start API. Check logs with: podman logs customer-jira-tracker-local"
    exit 1
fi

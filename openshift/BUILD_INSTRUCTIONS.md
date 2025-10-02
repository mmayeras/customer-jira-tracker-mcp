# Build and Push Instructions

This document provides instructions for building and pushing the Customer JIRA Tracker MCP Server image to Quay.io.

## Prerequisites

- Podman installed and running
- Quay.io account with access to your organization
- `podman` CLI authenticated with Quay.io

**Note**: When building on Mac (ARM64), use `--platform linux/amd64` to ensure compatibility with OpenShift clusters running on AMD64 architecture.

## Build and Push Steps

### 1. Login to Quay.io

```bash
# Login to Quay.io with your credentials
podman login quay.io
```

### 2. Build the Image

From the project root directory:

```bash
# Build the image with the correct tag (AMD64 architecture)
podman build --platform linux/amd64 -t quay.io/your-username/customer-jira-tracker:latest .

# Optional: Build with a specific version tag
podman build --platform linux/amd64 -t quay.io/your-username/customer-jira-tracker:v1.0.0 .
```

### 3. Push the Image

```bash
# Push the latest tag
podman push quay.io/your-username/customer-jira-tracker:latest

# Optional: Push version tag
podman push quay.io/your-username/customer-jira-tracker:v1.0.0
```

### 4. Verify the Image

```bash
# Test the image locally
podman run -p 8080:8080 quay.io/your-username/customer-jira-tracker:latest

# Check if the health endpoint works
curl http://localhost:8080/health
```

## Image Tags

The deployment scripts use these default tags:

- **Latest**: `quay.io/your-username/customer-jira-tracker:latest`
- **Version**: `quay.io/your-username/customer-jira-tracker:v1.0.0` (optional)

## Deployment

After building and pushing the image, you can deploy to OpenShift:

```bash
# Deploy using the pre-built image
cd openshift
EXTERNAL_IMAGE=quay.io/your-username/customer-jira-tracker:latest ./deploy.sh

# Or deploy with a specific image tag
EXTERNAL_IMAGE=quay.io/your-username/customer-jira-tracker:v1.0.0 ./deploy.sh
```

## Usage Modes

The image supports two different usage modes:

1. **OpenShift HTTP API Mode** (Default): Runs `http_server.py` to provide HTTP endpoints
2. **Local MCP Mode**: Run `python customer_jira_server.py` for direct MCP stdio usage

For Cursor integration with OpenShift, you need both:
- The OpenShift deployment (running `http_server.py`)
- A local MCP server (running `mcp-http-server.py`) that connects to the HTTP API

## Image Features

The built image includes:

- **Dual Mode**: Supports both MCP stdio and HTTP server modes
- **HTTP Server**: FastAPI-based HTTP API with authentication
- **MCP Server**: Original stdio-based MCP server
- **MCP HTTP Integration**: Files for local Cursor integration (included in image for easy access)
- **Dependencies**: All required Python packages including requests
- **Health Checks**: Built-in health and readiness endpoints
- **Security**: API key authentication for HTTP endpoints

## Troubleshooting

### Authentication Issues

```bash
# Re-authenticate with Quay.io
podman logout quay.io
podman login quay.io
```

### Build Issues

```bash
# Clean build (no cache) with AMD64 architecture
podman build --platform linux/amd64 --no-cache -t quay.io/your-username/customer-jira-tracker:latest .

# Check build logs
podman build --platform linux/amd64 -t quay.io/your-username/customer-jira-tracker:latest . 2>&1 | tee build.log
```

### Push Issues

```bash
# Check if image exists locally
podman images | grep customer-jira-tracker

# Test image locally before pushing
podman run --rm quay.io/your-username/customer-jira-tracker:latest python -c "print('Image works!')"
```

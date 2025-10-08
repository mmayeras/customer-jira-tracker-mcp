# OpenShift Deployment

This directory contains the deployment configuration for the Customer JIRA Tracker API on OpenShift.

## Deployment

### Deploy Script

Use the `deploy.sh` script to deploy the Customer JIRA Tracker API to OpenShift.

```bash
# Deploy using the default pre-built image
cd openshift
./deploy.sh

# Or deploy with a specific image tag
EXTERNAL_IMAGE=quay.io/your-username/customer-jira-tracker-server:v1.0.0 ./deploy.sh
```

## Prerequisites

- OpenShift cluster access
- `oc` CLI tool installed and authenticated
- Podman installed (for building and pushing images)
- Quay.io account with access to your organization

## Build and Push Instructions

Before deploying, you need to build and push the image to Quay.io. See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed steps.

## Configuration

Set these environment variables before running:

```bash
export NAMESPACE="customer-jira-tracker"  # Default namespace
export ROUTE_HOST="customer-jira-tracker-server.apps.your-cluster.com"  # Your route hostname
export EXTERNAL_IMAGE="quay.io/your-username/customer-jira-tracker-server:latest"  # Default image
```

## Quick Start

1. **Build and push your image** (see BUILD_INSTRUCTIONS.md)
2. **Set environment variables** (optional)
3. **Deploy the application**: `./deploy.sh`
4. **Update the API key** in the secret
5. **Access your application** via the route URL

## Storage Configuration

The PVC uses the default storage class. If you need a specific storage class:

1. Edit `pvc.yaml`
2. Uncomment and set the `storageClassName` field
3. Redeploy the application

## Cleanup

To remove all resources:

```bash
# Clean up all resources
./cleanup.sh

# Or clean up with custom namespace
NAMESPACE=my-namespace ./cleanup.sh
```


## Files

- `deploy.sh` - Main deployment script
- `cleanup.sh` - Cleanup script to remove all resources
- `deployment.yaml` - Main deployment manifest
- `service.yaml` - Service definition
- `route.yaml` - Route definition
- `pvc.yaml` - Persistent volume claim (uses default storage class)
- `secret.yaml` - Secret template for API key
- `BUILD_INSTRUCTIONS.md` - Build and push instructions
- `http_server.py` - FastAPI HTTP server implementation
- `main.py` - Application entry point

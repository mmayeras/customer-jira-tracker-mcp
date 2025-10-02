#!/bin/bash

# OpenShift Deployment Script for Customer JIRA Tracker MCP Server
# This script deploys using a pre-built image from Quay.io

set -e

# Configuration
NAMESPACE=${NAMESPACE:-customer-jira-tracker}
APP_NAME="customer-jira-tracker-mcp"
# You can change this to any public registry image
EXTERNAL_IMAGE=${EXTERNAL_IMAGE:-quay.io/rh_ee_mmayeras/customer-jira-tracker:latest}
ROUTE_HOST=${ROUTE_HOST:-customer-jira-tracker-mcp.apps.your-domain.com}

echo "🚀 Deploying Customer JIRA Tracker MCP Server to OpenShift"
echo "Namespace: $NAMESPACE"
echo "App Name: $APP_NAME"
echo "External Image: $EXTERNAL_IMAGE"
echo "Route Host: $ROUTE_HOST"

# Create namespace if it doesn't exist
echo "📁 Creating namespace..."
oc new-project $NAMESPACE 2>/dev/null || oc project $NAMESPACE

# Deploy PVC
echo "💾 Creating PersistentVolumeClaim..."
oc apply -f pvc.yaml

# Create secret for API key
echo "🔐 Creating API key secret..."
if ! oc get secret customer-jira-tracker-secret >/dev/null 2>&1; then
    echo "⚠️  Secret not found. Creating with default API key."
    echo "   Please update the secret with your actual API key:"
    echo "   oc patch secret customer-jira-tracker-secret -p '{\"data\":{\"api-key\":\"'$(echo -n 'your-secure-api-key' | base64)'\"}}'"
    oc apply -f secret.yaml
else
    echo "✅ Secret already exists, skipping creation."
fi

# Create deployment with pre-built image
echo "🚀 Creating deployment with pre-built image..."
cat > deployment-prebuilt.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-jira-tracker-mcp
  labels:
    app: customer-jira-tracker-mcp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: customer-jira-tracker-mcp
  template:
    metadata:
      labels:
        app: customer-jira-tracker-mcp
    spec:
      containers:
      - name: customer-jira-tracker-mcp
        image: $EXTERNAL_IMAGE
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: CUSTOMER_JIRA_STORAGE
          value: "/data"
        - name: PORT
          value: "8080"
        - name: REQUIRE_AUTH
          value: "true"
        - name: CUSTOMER_JIRA_TRACKER_API_KEY
          valueFrom:
            secretKeyRef:
              name: customer-jira-tracker-secret
              key: api-key
        volumeMounts:
        - name: data-storage
          mountPath: /data
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: data-storage
        persistentVolumeClaim:
          claimName: customer-jira-tracker-data
EOF

oc apply -f deployment-prebuilt.yaml

# Create service
echo "🌐 Creating service..."
oc apply -f service.yaml

# Create route
echo "🛣️  Creating route..."
# Update route with actual host
sed "s/customer-jira-tracker-mcp.apps.your-domain.com/$ROUTE_HOST/g" route.yaml | oc apply -f -

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
oc rollout status deployment/$APP_NAME --timeout=300s

# Get the route URL
ROUTE_URL=$(oc get route $APP_NAME-route -o jsonpath='{.spec.host}')
echo "✅ Deployment complete!"
echo "🌐 Application URL: https://$ROUTE_URL"
echo "🔍 Health Check: https://$ROUTE_URL/health"
echo "📊 API Documentation: https://$ROUTE_URL/docs"

# Show deployment status
echo ""
echo "📋 Deployment Status:"
oc get pods -l app=$APP_NAME
oc get services -l app=$APP_NAME
oc get routes -l app=$APP_NAME

echo ""
echo "🎉 Customer JIRA Tracker MCP Server is now running on OpenShift!"
echo "You can now configure Cursor to use the HTTP endpoints instead of local MCP."

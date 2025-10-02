FROM python:3.13-slim

WORKDIR /app

# Copy the OpenShift application files
COPY openshift/ .

# Copy the shared jira_mcp_client.py from root
COPY jira_mcp_client.py .

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx mcp

# Set default storage to /data
ENV CUSTOMER_JIRA_STORAGE=/data
ENV PORT=8080

# Create data directory
RUN mkdir -p /data

# Expose port for HTTP server
EXPOSE 8080

# Run the HTTP server
CMD ["python", "main.py"]

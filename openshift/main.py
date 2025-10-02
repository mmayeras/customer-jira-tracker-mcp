#!/usr/bin/env python3
"""
Main entry point for Customer JIRA Tracker on OpenShift
"""

import os
import uvicorn
from http_server import app

def main():
    """Start the HTTP server"""
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

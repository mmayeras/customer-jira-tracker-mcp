#!/usr/bin/env python3
"""
Local HTTP Server for Customer JIRA Tracker
For local development and testing with Podman
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import unquote

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data models
class TicketComment(BaseModel):
    comment: str
    timestamp: str

class CustomerTicket(BaseModel):
    key: str
    added_date: str
    comments: List[TicketComment] = []

class CustomerData(BaseModel):
    customer: str
    tickets: List[CustomerTicket] = []
    ticket_keys: List[str] = []
    notes: str = ""
    last_updated: str = ""
    total_tickets: int = 0
    total_comments: int = 0

class AddTicketsRequest(BaseModel):
    ticket_keys: List[str]
    notes: Optional[str] = None

class AddCommentRequest(BaseModel):
    comment: str

class UpdateNotesRequest(BaseModel):
    notes: str

# Initialize FastAPI app
app = FastAPI(
    title="Customer JIRA Tracker API (Local)",
    description="REST API for tracking JIRA tickets by customer - Local Development",
    version="1.0.0"
)

# Configuration
STORAGE_DIR = os.getenv("CUSTOMER_JIRA_STORAGE", "./customer_jira_data")
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
API_KEY = os.getenv("CUSTOMER_JIRA_API_KEY", "local-dev-key")

# Ensure storage directory exists
Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)

def get_api_key(authorization: Optional[str] = Header(None)) -> str:
    """Extract and validate API key from Authorization header"""
    if not REQUIRE_AUTH:
        return ""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

def get_customer_file_path(customer_name: str) -> Path:
    """Get the file path for a customer's data"""
    safe_name = customer_name.replace(" ", "_").replace("/", "_")
    return Path(STORAGE_DIR) / f"{safe_name}.json"

def load_customer_data(customer_name: str) -> CustomerData:
    """Load customer data from JSON file"""
    file_path = get_customer_file_path(customer_name)
    
    if not file_path.exists():
        return CustomerData(
            customer=customer_name,
            last_updated=datetime.now().isoformat()
        )
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return CustomerData(**data)
    except Exception as e:
        logger.error(f"Error loading customer data for {customer_name}: {e}")
        return CustomerData(
            customer=customer_name,
            last_updated=datetime.now().isoformat()
        )

def save_customer_data(customer_data: CustomerData) -> None:
    """Save customer data to JSON file"""
    file_path = get_customer_file_path(customer_data.customer)
    
    try:
        with open(file_path, 'w') as f:
            json.dump(customer_data.dict(), f, indent=2)
        logger.info(f"Saved customer data for {customer_data.customer}")
    except Exception as e:
        logger.error(f"Error saving customer data for {customer_data.customer}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save customer data")

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {"status": "ready", "timestamp": datetime.now().isoformat()}

# API endpoints
@app.get("/api/customers/{customer_name}/tickets")
async def get_customer_tickets(
    customer_name: str,
    api_key: str = Depends(get_api_key)
):
    """Get all tickets for a customer"""
    customer_data = load_customer_data(customer_name)
    return customer_data.dict()

@app.post("/api/customers/{customer_name}/tickets")
async def add_customer_tickets(
    customer_name: str,
    request: AddTicketsRequest,
    api_key: str = Depends(get_api_key)
):
    """Add tickets to a customer"""
    customer_data = load_customer_data(customer_name)
    
    # Add new tickets
    for ticket_key in request.ticket_keys:
        if ticket_key not in customer_data.ticket_keys:
            customer_data.ticket_keys.append(ticket_key)
            customer_data.tickets.append(CustomerTicket(
                key=ticket_key,
                added_date=datetime.now().isoformat()
            ))
    
    # Update notes if provided
    if request.notes:
        customer_data.notes = request.notes
    
    # Update metadata
    customer_data.total_tickets = len(customer_data.tickets)
    customer_data.total_comments = sum(len(ticket.comments) for ticket in customer_data.tickets)
    customer_data.last_updated = datetime.now().isoformat()
    
    save_customer_data(customer_data)
    return customer_data.dict()

@app.post("/api/customers/{customer_name}/tickets/{ticket_key}/comments")
async def add_ticket_comment(
    customer_name: str,
    ticket_key: str,
    request: AddCommentRequest,
    api_key: str = Depends(get_api_key)
):
    """Add a comment to a specific ticket"""
    customer_data = load_customer_data(customer_name)
    
    # Find the ticket
    ticket = None
    for t in customer_data.tickets:
        if t.key == ticket_key:
            ticket = t
            break
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Add comment
    comment = TicketComment(
        comment=request.comment,
        timestamp=datetime.now().isoformat()
    )
    ticket.comments.append(comment)
    
    # Update metadata
    customer_data.total_comments = sum(len(t.comments) for t in customer_data.tickets)
    customer_data.last_updated = datetime.now().isoformat()
    
    save_customer_data(customer_data)
    return customer_data.dict()

@app.put("/api/customers/{customer_name}/notes")
async def update_customer_notes(
    customer_name: str,
    request: UpdateNotesRequest,
    api_key: str = Depends(get_api_key)
):
    """Update customer notes"""
    customer_data = load_customer_data(customer_name)
    customer_data.notes = request.notes
    customer_data.last_updated = datetime.now().isoformat()
    
    save_customer_data(customer_data)
    return customer_data.dict()

@app.delete("/api/customers/{customer_name}/tickets")
async def remove_customer_tickets(
    customer_name: str,
    ticket_keys: List[str],
    api_key: str = Depends(get_api_key)
):
    """Remove tickets from a customer"""
    customer_data = load_customer_data(customer_name)
    
    # Remove tickets
    customer_data.ticket_keys = [tk for tk in customer_data.ticket_keys if tk not in ticket_keys]
    customer_data.tickets = [t for t in customer_data.tickets if t.key not in ticket_keys]
    
    # Update metadata
    customer_data.total_tickets = len(customer_data.tickets)
    customer_data.total_comments = sum(len(ticket.comments) for ticket in customer_data.tickets)
    customer_data.last_updated = datetime.now().isoformat()
    
    save_customer_data(customer_data)
    return customer_data.dict()

@app.get("/api/customers")
async def list_customers(api_key: str = Depends(get_api_key)):
    """List all customers"""
    customers = []
    for file_path in Path(STORAGE_DIR).glob("*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                customers.append({
                    "customer": data.get("customer", file_path.stem),
                    "total_tickets": data.get("total_tickets", 0),
                    "last_updated": data.get("last_updated", "")
                })
        except Exception as e:
            logger.error(f"Error reading customer file {file_path}: {e}")
    
    return {"customers": customers}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"Starting Customer JIRA Tracker API on port {port}")
    print(f"Storage directory: {STORAGE_DIR}")
    print(f"API Key: {API_KEY}")
    print(f"Require Auth: {REQUIRE_AUTH}")
    uvicorn.run(app, host="0.0.0.0", port=port)

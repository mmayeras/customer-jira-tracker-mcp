#!/usr/bin/env python3
"""
Global Index Manager for Customer JIRA Tracker
Maintains a global index for efficient case ID and ticket lookups
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class GlobalIndexManager:
    """Manages the global index for efficient queries"""
    
    def __init__(self, storage_dir: str = "customer_jira_data"):
        self.storage_dir = Path(storage_dir)
        self.index_file = self.storage_dir / "global_index.json"
        self.index_data = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the global index from file"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_empty_index()
        except Exception as e:
            logger.error(f"Error loading global index: {e}")
            return self._create_empty_index()
    
    def _create_empty_index(self) -> Dict[str, Any]:
        """Create an empty index structure"""
        return {
            "last_updated": datetime.now().isoformat(),
            "total_customers": 0,
            "total_tickets": 0,
            "customers": {},
            "case_index": {}
        }
    
    def _save_index(self):
        """Save the global index to file"""
        try:
            self.index_data["last_updated"] = datetime.now().isoformat()
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Global index saved to {self.index_file}")
        except Exception as e:
            logger.error(f"Error saving global index: {e}")
    
    def rebuild_index(self):
        """Rebuild the entire index from all customer files"""
        logger.info("Rebuilding global index...")
        
        # Reset index
        self.index_data = self._create_empty_index()
        
        # Load all customer files
        customer_files = list(self.storage_dir.glob("*.json"))
        customer_files = [f for f in customer_files if f.name != "global_index.json"]
        
        for customer_file in customer_files:
            try:
                with open(customer_file, 'r', encoding='utf-8') as f:
                    customer_data = json.load(f)
                
                customer_name = customer_data.get("customer", customer_file.stem)
                tickets = customer_data.get("tickets", [])
                
                # Add customer to index
                self.index_data["customers"][customer_name] = {
                    "total_tickets": len(tickets),
                    "tickets": []
                }
                
                # Add tickets to customer index and case index
                for ticket in tickets:
                    ticket_info = {
                        "key": ticket.get("key", ""),
                        "title": ticket.get("title", ""),
                        "caseID": ticket.get("caseID", "XXXXXXX")
                    }
                    
                    self.index_data["customers"][customer_name]["tickets"].append(ticket_info)
                    
                    # Add to case index
                    case_id = ticket.get("caseID", "XXXXXXX")
                    if case_id != "XXXXXXX":
                        if case_id not in self.index_data["case_index"]:
                            self.index_data["case_index"][case_id] = {
                                "customer": customer_name,
                                "tickets": []
                            }
                        self.index_data["case_index"][case_id]["tickets"].append(ticket.get("key", ""))
                
                self.index_data["total_tickets"] += len(tickets)
                
            except Exception as e:
                logger.error(f"Error processing customer file {customer_file}: {e}")
        
        self.index_data["total_customers"] = len(self.index_data["customers"])
        self._save_index()
        logger.info(f"Global index rebuilt: {self.index_data['total_customers']} customers, {self.index_data['total_tickets']} tickets")
    
    def get_case_info(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get customer and tickets for a specific case ID"""
        return self.index_data["case_index"].get(case_id)
    
    def get_customer_tickets(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """Get all tickets for a customer"""
        return self.index_data["customers"].get(customer_name)
    
    def search_tickets_by_title(self, search_term: str) -> List[Dict[str, Any]]:
        """Search tickets by title (case-insensitive)"""
        results = []
        search_term_lower = search_term.lower()
        
        for customer_name, customer_info in self.index_data["customers"].items():
            for ticket in customer_info["tickets"]:
                if search_term_lower in ticket.get("title", "").lower():
                    results.append({
                        "customer": customer_name,
                        "key": ticket["key"],
                        "title": ticket["title"],
                        "caseID": ticket["caseID"]
                    })
        
        return results
    
    def get_all_case_ids(self) -> List[str]:
        """Get all case IDs in the system"""
        return list(self.index_data["case_index"].keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "total_customers": self.index_data["total_customers"],
            "total_tickets": self.index_data["total_tickets"],
            "total_cases": len(self.index_data["case_index"]),
            "last_updated": self.index_data["last_updated"]
        }

# Global instance
index_manager = GlobalIndexManager()

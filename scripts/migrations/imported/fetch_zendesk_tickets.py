"""TODO: Module docstring for FetchZendeskTickets.py

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

"""
@references:
- Core References:
  - [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning





# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[7])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import os
from typing import List, Optional, Type

from crewai_tools import BaseTool
from dotenv import load_dotenv
from pydantic.v1 import BaseModel, Field
import requests


class ZendeskTicket(BaseModel):
    id: int
    subject: str
    description: Optional[str] = None  # First comment or ticket body
    status: str
    priority: Optional[str] = None  # Ticket priority (low, normal, high, urgent)
    type: Optional[str] = None  # Ticket type (question, incident, problem, task)
    assignee_id: Optional[int] = None  # ID of the user assigned to the ticket
    requester_id: Optional[int] = None  # ID of the user who requested the ticket
    group_id: Optional[int] = None  # ID of the group assigned to the ticket
    tags: Optional[List[str]] = None  # List of tags associated with the ticket
    organization_id: Optional[int] = None  # ID of the organization
    created_at: str
    updated_at: str
    due_at: Optional[str] = None  # Due date (for tasks)
    external_id: Optional[str] = None  # Optional external ID for linking with other systems
    satisfaction_rating: Optional[dict] = None  # Satisfaction rating info
    via: Optional[dict] = None  # Information on how the ticket was created
    fields: Optional[dict] = None  # Custom fields for your Zendesk account


class ZendeskTicketSearchToolInput(BaseModel):
    """Input schema for ZendeskTicketSearchTool."""

    status: Optional[str] = Field(
        None, description="Ticket status (e.g., open, pending, solved, closed)"
    )
    created_since: Optional[str] = Field(
        None, description="ISO 8601 date for filtering tickets created after this date"
    )
    updated_since: Optional[str] = Field(
        None, description="ISO 8601 date for filtering tickets updated after this date"
    )
    priority: Optional[str] = Field(
        None, description="Ticket priority (e.g., low, normal, high, urgent)"
    )
    ticket_type: Optional[str] = Field(
        None, description="Ticket type (e.g., question, incident, problem, task)"
    )


class ZendeskTicketSearchTool(BaseTool):
    name: str = "Fetch Zendesk Tickets"
    description: str = (
        "Fetches Zendesk tickets using the API, with optional query parameters for filtering."
    )
    args_schema: Type[BaseModel] = ZendeskTicketSearchToolInput

    def _run(
        self,
        status: Optional[str] = None,
        created_since: Optional[str] = None,
        updated_since: Optional[str] = None,
        priority: Optional[str] = None,
        ticket_type: Optional[str] = None,
    ) -> List[ZendeskTicket]:
        # Load environment variables
        load_dotenv()
        ZENDESK_SUBDOMAIN = os.getenv("ZENDESK_SUBDOMAIN")
        ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
        ZENDESK_API_TOKEN = os.getenv("ZENDESK_API_TOKEN")

        if not ZENDESK_SUBDOMAIN or not ZENDESK_EMAIL or not ZENDESK_API_TOKEN:
            raise ValueError("Zendesk API credentials are not properly set.")

        # Set up the base URL and authentication
        base_url = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2/tickets.json"
        auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)

        # Query parameters
        params = {}
        if status:
            params["status"] = status
        if created_since:
            params["created_since"] = created_since
        if updated_since:
            params["updated_since"] = updated_since
        if priority:
            params["priority"] = priority
        if ticket_type:
            params["type"] = ticket_type

        tickets = []
        url = base_url

        while url:
            # Make the GET request to fetch tickets with authentication and query params
            response = requests.get(url, auth=auth, params=params)

            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                break

            data = response.json()

            # Append the tickets to the list
            tickets.extend([ZendeskTicket(**ticket) for ticket in data.get("tickets", [])])

            # Pagination: check if there's a next page
            url = data.get("next_page")

        return tickets
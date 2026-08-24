import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP


# ============================================================
# CONFIGURATION
# ============================================================

# Find .env in the same folder as server.py
ENV_FILE = Path(__file__).resolve().parent / ".env"

# Load .env
load_dotenv(dotenv_path=ENV_FILE)

# SAP API Key
SAP_API_KEY = os.getenv("SAP_API_KEY")

# SAP Business Accelerator Hub Sandbox
BASE_URL = "https://sandbox.api.sap.com"

# MCP Server
mcp = FastMCP("sap-cloud-alm")


# ============================================================
# TOOL 1 - GET LANDSCAPE OBJECTS
# ============================================================

@mcp.tool()
async def get_landscape_objects():
    """
    Get SAP Cloud ALM landscape objects.
    """

    if not SAP_API_KEY:
        return (
            "ERROR: SAP_API_KEY was not found. "
            "Check that .env exists beside server.py "
            "and contains SAP_API_KEY=YOUR_KEY."
        )

    url = f"{BASE_URL}/SAPCALM/calm-landscape/v1/landscapeObjects"

    headers = {
        "APIKey": SAP_API_KEY,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:

        response = await client.get(
            url,
            headers=headers
        )

        response.raise_for_status()

        return response.json()


# ============================================================
# TOOL 2 - GET CLOUD ALM PROJECTS
# ============================================================

@mcp.tool()
async def get_alm_projects():
    """
    Get all SAP Cloud ALM projects.
    """

    if not SAP_API_KEY:
        return (
            "ERROR: SAP_API_KEY was not found. "
            "Check that .env exists beside server.py."
        )

    url = f"{BASE_URL}/SAPCALM/calm-projects/v1/projects"

    headers = {
        "APIKey": SAP_API_KEY,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:

        response = await client.get(
            url,
            headers=headers
        )

        response.raise_for_status()

        return response.json()


# ============================================================
# TOOL 3 - GET STATUS EVENTS
# ============================================================

@mcp.tool()
async def get_status_events():
    """
    Get SAP Cloud ALM status events.
    """

    if not SAP_API_KEY:
        return (
            "ERROR: SAP_API_KEY was not found. "
            "Check that .env exists beside server.py."
        )

    url = f"{BASE_URL}/SAPCALM/bsm-service/v1/events"

    headers = {
        "APIKey": SAP_API_KEY,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:

        response = await client.get(
            url,
            headers=headers
        )

        response.raise_for_status()

        return response.json()


# ============================================================
# TOOL 4 - GET CLOUD ALM TASKS
# ============================================================

@mcp.tool()
async def get_alm_tasks(project_id: str):
    """
    Get SAP Cloud ALM tasks for a specific project.

    Args:
        project_id:
            SAP Cloud ALM project ID.
    """

    if not SAP_API_KEY:
        return (
            "ERROR: SAP_API_KEY was not found. "
            "Check that .env exists beside server.py."
        )

    url = f"{BASE_URL}/SAPCALM/calm-tasks/v1/tasks"

    headers = {
        "APIKey": SAP_API_KEY,
        "Accept": "application/json"
    }

    params = {
        "projectId": project_id
    }

    async with httpx.AsyncClient(timeout=60.0) as client:

        response = await client.get(
            url,
            headers=headers,
            params=params
        )

        response.raise_for_status()

        return response.json()


# ============================================================
# TOOL 5 - GET CLOUD ALM DELIVERABLES
# ============================================================

@mcp.tool()
async def get_alm_deliverables(project_id: str):
    """
    Get SAP Cloud ALM deliverables for a specific project.

    Args:
        project_id:
            SAP Cloud ALM project ID.
    """

    if not SAP_API_KEY:
        return (
            "ERROR: SAP_API_KEY was not found. "
            "Check that .env exists beside server.py."
        )

    url = f"{BASE_URL}/SAPCALM/calm-tasks/v1/deliverables"

    headers = {
        "APIKey": SAP_API_KEY,
        "Accept": "application/json"
    }

    params = {
        "projectId": project_id
    }

    async with httpx.AsyncClient(timeout=60.0) as client:

        response = await client.get(
            url,
            headers=headers,
            params=params
        )

        response.raise_for_status()

        return response.json()


# ============================================================
# START MCP SERVER
# ============================================================

if __name__ == "__main__":
    mcp.run()
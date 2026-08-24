# SAP Cloud ALM MCP Server

A lightweight Model Context Protocol (MCP) server that exposes selected SAP Cloud ALM Sandbox APIs as MCP tools.

## Features

The server provides the following MCP tools:

- `get_alm_projects`
- `get_landscape_objects`
- `get_status_events`
- `get_alm_tasks`
- `get_alm_deliverables`

+--------------------------+
| MCP Client               |
| (VS Code, Copilot, etc.) |
+------------+-------------+
             |
             | MCP
             v
+--------------------------+
| SAP Cloud ALM MCP Server |
+------------+-------------+
             |
             | REST APIs
             v
+--------------------------+
| SAP Business Accelerator |
| Hub Sandbox APIs         |
+--------------------------+
## Requirements

- Python 3.10+
- VS Code
- MCP Inspector
- SAP Business Accelerator Hub Sandbox API Key

## Configuration

Create a `.env` file beside `server.py`:

```text
SAP_API_KEY=YOUR_SANDBOX_API_KEY

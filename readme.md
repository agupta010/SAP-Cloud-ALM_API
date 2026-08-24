# SAP Cloud ALM MCP Server

A lightweight Model Context Protocol (MCP) server that exposes selected SAP Cloud ALM Sandbox APIs as MCP tools.
Overview
SAP Cloud ALM MCP Server exposes selected SAP Cloud ALM APIs as MCP-compatible tools, allowing AI clients such as VS Code, GitHub Copilot, Claude Desktop, MCP Inspector, and other MCP-enabled applications to interact directly with SAP Cloud ALM.
By bridging SAP Cloud ALM and MCP, users can retrieve project information, explore landscapes, track deliverables, and analyze operational status using conversational AI.

**Key Features**

Exposes SAP Cloud ALM APIs as MCP tools
Simple Python-based implementation
Uses SAP Business Accelerator Hub Sandbox APIs
Compatible with MCP-enabled AI clients
Environment-based configuration
Easy to extend with additional SAP Cloud ALM APIs

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

**Project Structure**

SAP-Cloud-ALM_API/
│
├── server.py
├── requirements.txt
├── .env
├── README.md
└── src/
    ├── projects.py
    ├── tasks.py
    ├── deliverables.py
    ├── landscapes.py
    └── status_events.py

<img width="1908" height="907" alt="image" src="https://github.com/user-attachments/assets/dee5490b-a1ac-4d8a-9ba2-2c8c7df39a16" />





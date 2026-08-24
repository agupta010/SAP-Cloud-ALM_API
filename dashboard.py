import os
import json
import asyncio
from pathlib import Path

import httpx
import requests
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

SAP_API_KEY = os.getenv("SAP_API_KEY")

SAP_BASE_URL = "https://sandbox.api.sap.com"

# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"

# IMPORTANT:
# Change this if "ollama list" shows another model.
OLLAMA_MODEL = "llama3.2:3b"


# ============================================================
# STREAMLIT PAGE
# ============================================================

st.set_page_config(
    page_title="SAP Cloud ALM AI Dashboard",
    page_icon="🟦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SAP STYLE
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f5f7fa;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .sap-header {
        background: linear-gradient(
            90deg,
            #0a6ed1,
            #0854a0
        );

        padding: 25px 30px;

        border-radius: 12px;

        color: white;

        margin-bottom: 25px;

        box-shadow: 0 3px 10px rgba(0,0,0,0.12);
    }

    .sap-header h1 {
        margin: 0;
        font-size: 32px;
        font-weight: 600;
    }

    .sap-header p {
        margin-top: 7px;
        margin-bottom: 0;
        font-size: 15px;
    }

    .metric-card {
        background: white;

        padding: 20px;

        border-radius: 12px;

        border: 1px solid #d9e2ec;

        text-align: center;

        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .metric-title {
        color: #5b6878;

        font-size: 14px;

        margin-bottom: 8px;
    }

    .metric-value {
        color: #0a6ed1;

        font-size: 32px;

        font-weight: 700;
    }

    .ai-box {
        background: white;

        padding: 20px;

        border-radius: 12px;

        border: 1px solid #d9e2ec;

        box-shadow: 0 2px 8px rgba(0,0,0,0.05);

        margin-top: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# ASYNC HELPER
# ============================================================

def run_async(coro):

    try:

        return asyncio.run(coro)

    except RuntimeError:

        loop = asyncio.new_event_loop()

        try:

            asyncio.set_event_loop(loop)

            return loop.run_until_complete(coro)

        finally:

            loop.close()


# ============================================================
# SAP API
# ============================================================

async def sap_get(endpoint, params=None):

    if not SAP_API_KEY:

        raise Exception(
            "SAP_API_KEY is missing. "
            "Check your .env file."
        )

    url = f"{SAP_BASE_URL}{endpoint}"

    headers = {
        "APIKey": SAP_API_KEY,
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=15,
            read=60,
            write=30,
            pool=30
        )
    ) as client:

        response = await client.get(
            url,
            headers=headers,
            params=params
        )

        response.raise_for_status()

        return response.json()


# ============================================================
# SAP PROJECTS
# ============================================================

async def get_projects():

    return await sap_get(
        "/SAPCALM/calm-projects/v1/projects"
    )


# ============================================================
# SAP LANDSCAPE
# ============================================================

async def get_landscape_objects():

    return await sap_get(
        "/SAPCALM/calm-landscape/v1/landscapeObjects"
    )


# ============================================================
# SAP STATUS EVENTS
# ============================================================

async def get_status_events():

    return await sap_get(
        "/SAPCALM/bsm-service/v1/events"
    )


# ============================================================
# SAP TASKS
# ============================================================

async def get_tasks(project_id):

    return await sap_get(
        "/SAPCALM/calm-tasks/v1/tasks",
        params={
            "projectid": project_id
        }
    )


# ============================================================
# SAP DELIVERABLES
# ============================================================

async def get_deliverables(project_id):

    return await sap_get(
        "/SAPCALM/calm-tasks/v1/deliverables",
        params={
            "projectid": project_id
        }
    )


# ============================================================
# EXTRACT LIST FROM SAP RESPONSE
# ============================================================

def extract_items(data):

    if isinstance(data, list):

        return data

    if isinstance(data, dict):

        possible_keys = [
            "value",
            "results",
            "items",
            "data",
            "projects",
            "tasks",
            "deliverables",
            "events",
            "landscapeObjects"
        ]

        for key in possible_keys:

            if key in data:

                if isinstance(
                    data[key],
                    list
                ):

                    return data[key]

    return []


# ============================================================
# PROJECT ID
# ============================================================

def get_project_id(project):

    if not isinstance(
        project,
        dict
    ):

        return None

    return (
        project.get("id")
        or project.get("projectId")
        or project.get("projectID")
        or project.get("projectid")
    )


# ============================================================
# PROJECT NAME
# ============================================================

def get_project_name(project):

    if not isinstance(
        project,
        dict
    ):

        return "Unnamed Project"

    return (
        project.get("name")
        or project.get("projectName")
        or project.get("description")
        or "Unnamed Project"
    )


# ============================================================
# OLLAMA AI
# ============================================================

def ask_ollama(
    question,
    sap_context
):

    prompt = f"""
You are an SAP Cloud ALM AI Assistant.

You help users understand their SAP Cloud ALM
environment.

Use ONLY the SAP Cloud ALM information provided below.

Do not invent projects, tasks, deliverables,
landscape objects or status events.

If the available information is not sufficient,
clearly say that the information is not available.

Give practical and easy-to-understand answers.

SAP CLOUD ALM DATA:

{sap_context}


USER QUESTION:

{question}
"""

    payload = {

        "model": OLLAMA_MODEL,

        "prompt": prompt,

        "stream": False
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        return result.get(
            "response",
            "Ollama returned no response."
        )

    except requests.exceptions.ConnectionError:

        return """
❌ Cannot connect to Ollama.

Please make sure Ollama is running.

You can test it with:

ollama list

or:

ollama run llama3.2:3b
"""

    except requests.exceptions.Timeout:

        return """
⏱️ Ollama took too long to respond.

Try asking a shorter question or use
a smaller model.
"""

    except Exception as e:

        return f"""
❌ Ollama error:

{str(e)}
"""


# ============================================================
# BUILD AI CONTEXT
# ============================================================

def build_ai_context():

    projects = st.session_state.get(
        "projects_data",
        {}
    )

    landscape = st.session_state.get(
        "landscape_data",
        {}
    )

    tasks = st.session_state.get(
        "tasks_data",
        {}
    )

    deliverables = st.session_state.get(
        "deliverables_data",
        {}
    )

    events = st.session_state.get(
        "events_data",
        {}
    )

    project_list = extract_items(
        projects
    )

    landscape_list = extract_items(
        landscape
    )

    task_list = extract_items(
        tasks
    )

    deliverable_list = extract_items(
        deliverables
    )

    event_list = extract_items(
        events
    )

    context = {

        "project_count": len(
            project_list
        ),

        "landscape_object_count": len(
            landscape_list
        ),

        "task_count": len(
            task_list
        ),

        "deliverable_count": len(
            deliverable_list
        ),

        "event_count": len(
            event_list
        ),

        # Keep request small
        "projects": project_list[:10],

        "landscape_objects":
            landscape_list[:10],

        "tasks":
            task_list[:10],

        "deliverables":
            deliverable_list[:10],

        "status_events":
            event_list[:10]
    }

    return json.dumps(
        context,
        indent=2,
        default=str
    )


# ============================================================
# SESSION STATE
# ============================================================

if "projects_data" not in st.session_state:

    st.session_state.projects_data = {}


if "landscape_data" not in st.session_state:

    st.session_state.landscape_data = {}


if "tasks_data" not in st.session_state:

    st.session_state.tasks_data = {}


if "deliverables_data" not in st.session_state:

    st.session_state.deliverables_data = {}


if "events_data" not in st.session_state:

    st.session_state.events_data = {}


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="sap-header">

        <h1>
            🟦 SAP Cloud ALM AI Dashboard
        </h1>

        <p>
            SAP Cloud ALM Sandbox Monitoring
            + Local Ollama AI Assistant
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🟦 SAP Cloud ALM"
    )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "📁 Projects",
            "🖥️ Landscape",
            "📋 Tasks",
            "📦 Deliverables",
            "⚠️ Status Events",
            "🤖 AI Assistant"
        ]
    )

    st.markdown("---")

    if SAP_API_KEY:

        st.success(
            "SAP API configured"
        )

    else:

        st.error(
            "SAP API key missing"
        )

    st.success(
        "🦙 Ollama configured"
    )

    st.caption(
        f"Model: {OLLAMA_MODEL}"
    )

    st.markdown("---")

    refresh_button = st.button(
        "🔄 Refresh SAP Data",
        use_container_width=True
    )


# ============================================================
# REFRESH
# ============================================================

if refresh_button:

    with st.spinner(
        "Loading SAP Cloud ALM data..."
    ):

        try:

            st.session_state.projects_data = (
                run_async(
                    get_projects()
                )
            )

            st.session_state.landscape_data = (
                run_async(
                    get_landscape_objects()
                )
            )

            st.session_state.events_data = (
                run_async(
                    get_status_events()
                )
            )

            st.success(
                "SAP data refreshed."
            )

        except Exception as e:

            st.error(
                f"SAP API error: {e}"
            )


# ============================================================
# OVERVIEW
# ============================================================

if page == "🏠 Overview":

    st.subheader(
        "SAP Cloud ALM Overview"
    )

    if not st.session_state.projects_data:

        with st.spinner(
            "Loading SAP Cloud ALM..."
        ):

            try:

                st.session_state.projects_data = (
                    run_async(
                        get_projects()
                    )
                )

                st.session_state.landscape_data = (
                    run_async(
                        get_landscape_objects()
                    )
                )

                st.session_state.events_data = (
                    run_async(
                        get_status_events()
                    )
                )

            except Exception as e:

                st.error(
                    f"Could not load SAP data: {e}"
                )

    projects = extract_items(
        st.session_state.projects_data
    )

    landscape = extract_items(
        st.session_state.landscape_data
    )

    events = extract_items(
        st.session_state.events_data
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    Projects
                </div>

                <div class="metric-value">
                    {len(projects)}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    Landscape Objects
                </div>

                <div class="metric-value">
                    {len(landscape)}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    Status Events
                </div>

                <div class="metric-value">
                    {len(events)}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-title">
                    Local AI
                </div>

                <div class="metric-value">
                    ON
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.subheader(
        "Projects"
    )

    if projects:

        rows = []

        for project in projects:

            rows.append(
                {
                    "Project ID":
                        get_project_id(project),

                    "Project Name":
                        get_project_name(project),

                    "Description":
                        project.get(
                            "description",
                            ""
                        )
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No projects found."
        )


# ============================================================
# PROJECTS
# ============================================================

elif page == "📁 Projects":

    st.subheader(
        "📁 SAP Cloud ALM Projects"
    )

    if not st.session_state.projects_data:

        try:

            st.session_state.projects_data = (
                run_async(
                    get_projects()
                )
            )

        except Exception as e:

            st.error(
                f"Error loading projects: {e}"
            )

    projects = extract_items(
        st.session_state.projects_data
    )

    if projects:

        rows = []

        for project in projects:

            rows.append(
                {
                    "Project ID":
                        get_project_id(project),

                    "Project Name":
                        get_project_name(project),

                    "Description":
                        project.get(
                            "description",
                            ""
                        )
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True
        )

        with st.expander(
            "Show raw SAP response"
        ):

            st.json(
                st.session_state.projects_data
            )

    else:

        st.info(
            "No projects found."
        )


# ============================================================
# LANDSCAPE
# ============================================================

elif page == "🖥️ Landscape":

    st.subheader(
        "🖥️ Landscape Objects"
    )

    if not st.session_state.landscape_data:

        try:

            st.session_state.landscape_data = (
                run_async(
                    get_landscape_objects()
                )
            )

        except Exception as e:

            st.error(
                f"Error loading landscape: {e}"
            )

    landscape = extract_items(
        st.session_state.landscape_data
    )

    st.metric(
        "Landscape Objects",
        len(landscape)
    )

    if landscape:

        st.dataframe(
            landscape,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No landscape objects found."
        )


# ============================================================
# TASKS
# ============================================================

elif page == "📋 Tasks":

    st.subheader(
        "📋 SAP Cloud ALM Tasks"
    )

    if not st.session_state.projects_data:

        try:

            st.session_state.projects_data = (
                run_async(
                    get_projects()
                )
            )

        except Exception as e:

            st.error(
                f"Error loading projects: {e}"
            )

    projects = extract_items(
        st.session_state.projects_data
    )

    if projects:

        project_options = {}

        for project in projects:

            project_id = get_project_id(
                project
            )

            project_name = get_project_name(
                project
            )

            if project_id:

                project_options[
                    f"{project_name} ({project_id})"
                ] = project_id

        selected_project = st.selectbox(
            "Select Project",
            list(
                project_options.keys()
            )
        )

        selected_project_id = (
            project_options[
                selected_project
            ]
        )

        if st.button(
            "Load Tasks",
            type="primary"
        ):

            with st.spinner(
                "Loading tasks..."
            ):

                try:

                    st.session_state.tasks_data = (
                        run_async(
                            get_tasks(
                                selected_project_id
                            )
                        )
                    )

                except Exception as e:

                    st.error(
                        f"Task API error: {e}"
                    )

        tasks = extract_items(
            st.session_state.tasks_data
        )

        if tasks:

            st.metric(
                "Tasks",
                len(tasks)
            )

            st.dataframe(
                tasks,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Select a project and click Load Tasks."
            )

    else:

        st.warning(
            "No projects available."
        )


# ============================================================
# DELIVERABLES
# ============================================================

elif page == "📦 Deliverables":

    st.subheader(
        "📦 SAP Cloud ALM Deliverables"
    )

    if not st.session_state.projects_data:

        try:

            st.session_state.projects_data = (
                run_async(
                    get_projects()
                )
            )

        except Exception as e:

            st.error(
                f"Error loading projects: {e}"
            )

    projects = extract_items(
        st.session_state.projects_data
    )

    if projects:

        project_options = {}

        for project in projects:

            project_id = get_project_id(
                project
            )

            project_name = get_project_name(
                project
            )

            if project_id:

                project_options[
                    f"{project_name} ({project_id})"
                ] = project_id

        selected_project = st.selectbox(
            "Select Project",
            list(
                project_options.keys()
            )
        )

        selected_project_id = (
            project_options[
                selected_project
            ]
        )

        if st.button(
            "Load Deliverables",
            type="primary"
        ):

            with st.spinner(
                "Loading deliverables..."
            ):

                try:

                    st.session_state.deliverables_data = (
                        run_async(
                            get_deliverables(
                                selected_project_id
                            )
                        )
                    )

                except Exception as e:

                    st.error(
                        f"Deliverable API error: {e}"
                    )

        deliverables = extract_items(
            st.session_state.deliverables_data
        )

        if deliverables:

            st.metric(
                "Deliverables",
                len(deliverables)
            )

            st.dataframe(
                deliverables,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Select a project and click Load Deliverables."
            )

    else:

        st.warning(
            "No projects available."
        )


# ============================================================
# STATUS EVENTS
# ============================================================

elif page == "⚠️ Status Events":

    st.subheader(
        "⚠️ SAP Cloud ALM Status Events"
    )

    if not st.session_state.events_data:

        try:

            st.session_state.events_data = (
                run_async(
                    get_status_events()
                )
            )

        except Exception as e:

            st.error(
                f"Error loading status events: {e}"
            )

    events = extract_items(
        st.session_state.events_data
    )

    st.metric(
        "Status Events",
        len(events)
    )

    if events:

        st.dataframe(
            events,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No status events found."
        )


# ============================================================
# AI ASSISTANT
# ============================================================

elif page == "🤖 AI Assistant":

    st.subheader(
        "🤖 SAP Cloud ALM AI Assistant"
    )

    st.markdown(
        """
        <div class="ai-box">

        <h3>Ask your SAP Cloud ALM AI Assistant</h3>

        Ask questions about your Projects, Landscape,
        Tasks, Deliverables and Status Events.

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    question = st.text_area(
        "Your question",
        placeholder=(
            "Example: Give me a summary of my SAP Cloud ALM environment."
        ),
        height=120
    )

    st.markdown(
        f"🦙 **Local AI model:** `{OLLAMA_MODEL}`"
    )

    if st.button(
        "🤖 Ask Ollama",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            sap_context = build_ai_context()

            with st.spinner(
                "Ollama is analyzing SAP Cloud ALM..."
            ):

                answer = ask_ollama(
                    question,
                    sap_context
                )

            st.markdown("---")

            st.subheader(
                "💬 AI Answer"
            )

            st.markdown(
                answer
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#6a6d70;
        font-size:12px;
    ">

    SAP Cloud ALM AI Dashboard
    |
    SAP Sandbox
    |
    Local Ollama AI

    </div>
    """,
    unsafe_allow_html=True
)
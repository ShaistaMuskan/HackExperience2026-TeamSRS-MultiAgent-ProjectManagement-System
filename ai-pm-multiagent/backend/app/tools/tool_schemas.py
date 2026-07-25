"""
OpenAI/Azure-AI-Foundry-compatible function/tool schemas.

These are the JSON schemas you register on the Azure AI Foundry Agent (see
docs/architecture/azure-foundry-m365-integration-guide.md Section 3.4) so the
Foundry Agent's model can decide WHEN to call each tool and with what
arguments. The Python callables they map to live in this package
(app/tools/*.py); app/agents/base.py's `dispatch_tool_call` routes a Foundry
tool_call by `name` to the matching function.
"""

TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "create_planner_task",
            "description": "Create a Microsoft Planner task in a given plan/bucket for a project task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_id": {"type": "string"},
                    "bucket_id": {"type": "string"},
                    "task_id": {"type": "string", "description": "internal Task.id to sync"},
                    "assignee_emails": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["plan_id", "bucket_id", "task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_planner_task",
            "description": "Update fields (status, due date, percent complete) on an existing Planner task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "planner_task_id": {"type": "string"},
                    "updates": {"type": "object"},
                },
                "required": ["planner_task_id", "updates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_bucket",
            "description": "Create a new bucket (column) inside a Planner plan, e.g. one per project phase.",
            "parameters": {
                "type": "object",
                "properties": {"plan_id": {"type": "string"}, "name": {"type": "string"}},
                "required": ["plan_id", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_teams_message",
            "description": "Post a plain-text notification message to a Microsoft Teams channel.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"}, "channel_id": {"type": "string"}, "message": {"type": "string"},
                },
                "required": ["project_id", "channel_id", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_channel",
            "description": "Create a new channel inside a Microsoft Teams team, e.g. for a new project.",
            "parameters": {
                "type": "object",
                "properties": {"team_id": {"type": "string"}, "name": {"type": "string"}, "description": {"type": "string"}},
                "required": ["team_id", "name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedule a Teams/Outlook meeting with the given attendees.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "attendees": {"type": "array", "items": {"type": "string"}},
                    "start": {"type": "string", "format": "date-time"},
                    "end": {"type": "string", "format": "date-time"},
                },
                "required": ["subject", "attendees", "start", "end"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "upload_document",
            "description": "Upload a document (e.g. project charter, status report) to the project's SharePoint folder.",
            "parameters": {
                "type": "object",
                "properties": {"folder_url": {"type": "string"}, "filename": {"type": "string"}},
                "required": ["folder_url", "filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_rag_documents",
            "description": "Retrieve relevant knowledge-base documents (methodology guides, templates, historical projects, risk rules) via Azure AI Search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5},
                    "category": {"type": "string", "enum": ["methodology", "template", "historical", "risk_rules", "sop"]},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_project_status",
            "description": "Recompute and persist the project's overall health status.",
            "parameters": {"type": "object", "properties": {"project_id": {"type": "string"}}, "required": ["project_id"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assign_task",
            "description": "Assign a task to a specific resource/team member.",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "string"}, "resource_id": {"type": "string"}},
                "required": ["task_id", "resource_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_project_risk",
            "description": "Recompute the project's risk/health profile (delay probability, budget risk, resource bottlenecks).",
            "parameters": {"type": "object", "properties": {"project_id": {"type": "string"}}, "required": ["project_id"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_wbs",
            "description": "Generate a full Work Breakdown Structure (phases, epics, tasks, milestones) for a project from its brief.",
            "parameters": {
                "type": "object",
                "properties": {"project_id": {"type": "string"}, "methodology": {"type": "string"}},
                "required": ["project_id", "methodology"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_dependencies",
            "description": "Infer task dependencies within a project's WBS.",
            "parameters": {"type": "object", "properties": {"project_id": {"type": "string"}}, "required": ["project_id"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_duration",
            "description": "Estimate effort/duration (hours) for a task based on its title/description.",
            "parameters": {
                "type": "object",
                "properties": {"task_title": {"type": "string"}},
                "required": ["task_title"],
            },
        },
    },
]

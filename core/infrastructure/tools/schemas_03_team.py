# -*- coding: utf-8 -*-
"""工具 schema 分片 3/9（10 个，域: team；保持旧 core/tools.py 原序，禁止重排）。"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "task_list",
            "description": "List all tasks. Optionally filter by status. Use this to see the current state of the task graph.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": [
                            "pending",
                            "in_progress",
                            "completed"
                        ]
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_get",
            "description": "Get details of a specific task by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "task_id"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_clear",
            "description": "Clear all tasks and reset the task ID counter. Use this after all tasks are completed to clean up for the next session.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_in_background",
            "description": "Run a shell command in the background. Returns immediately with a task ID. Use for long-running commands like npm install, pytest, docker build, pip install. Results delivered as background notifications in subsequent turns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string"
                    }
                },
                "required": [
                    "command"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "spawn_teammate",
            "description": "Create a persistent teammate agent that runs in its own thread with its own Agent Loop. The teammate has an independent context and can use all tools except team management tools (no recursion). Use this to delegate work to specialized agents (e.g., coder, tester, reviewer).",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Unique name for the teammate (e.g., 'coder', 'tester')"
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "System prompt defining the teammate's role and expertise"
                    }
                },
                "required": [
                    "name",
                    "system_prompt"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_to_teammate",
            "description": "Send a task message to a teammate. The teammate will process it in its own Agent Loop and send the result back to your inbox. Results arrive as <teammate-reports> in subsequent turns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_name": {
                        "type": "string",
                        "description": "Name of the teammate to send the task to"
                    },
                    "task": {
                        "type": "string",
                        "description": "The task description to send"
                    }
                },
                "required": [
                    "to_name",
                    "task"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "team_status",
            "description": "Show the current team roster with each teammate's status (idle/working/shutdown) and role. Use this to check on your team's progress.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown_teammate",
            "description": "Shut down a teammate agent. The teammate's thread will exit on its next loop iteration. Use this when a teammate's work is done and you want to clean up resources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the teammate to shut down"
                    }
                },
                "required": [
                    "name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_shutdown",
            "description": "Request a graceful shutdown of a teammate via the Shutdown Handshake Protocol. Sends a shutdown request; the teammate checks for uncommitted writes and either approves (safe exit after flushing buffers) or rejects (still has pending work). Use this instead of shutdown_teammate so the teammate gets a chance to finish/clean up. The result appears in <pending-requests> in a later turn.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the teammate to shut down gracefully"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Why the teammate is being shut down"
                    }
                },
                "required": [
                    "name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "submit_plan",
            "description": "Submit an implementation plan for leader approval (Plan Approval Protocol). High-risk changes MUST be approved before execution. If the plan is rejected, revise it and submit again. Wait for the approval result in <pending-requests> before executing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_summary": {
                        "type": "string",
                        "description": "What you plan to do"
                    },
                    "affected_files": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Files you plan to modify/create"
                    },
                    "risk_level": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high"
                        ],
                        "description": "Risk level: high = refactor/delete API/database migration"
                    },
                    "estimated_changes": {
                        "type": "integer",
                        "description": "Estimated number of changes"
                    }
                },
                "required": [
                    "plan_summary",
                    "affected_files",
                    "risk_level",
                    "estimated_changes"
                ]
            }
        }
    }
]

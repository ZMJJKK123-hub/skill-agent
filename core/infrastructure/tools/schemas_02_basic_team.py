# -*- coding: utf-8 -*-
"""工具 schema 分片 2/9（9 个，域: basic+team；保持旧 core/tools.py 原序，禁止重排）。"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents. Supports offset (1-based first line) and limit. Full MC/Forge source files under mc_java_sources are allowed; use this to inspect complete constructor/method signatures after a compile error.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path (workspace-relative; mc_java_sources/... allowed)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max lines to return (default all)"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "1-based first line to read (default 1)"
                    }
                },
                "required": [
                    "path"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    }
                },
                "required": [
                    "path",
                    "content"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace exact text in file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string"
                    },
                    "old_text": {
                        "type": "string"
                    },
                    "new_text": {
                        "type": "string"
                    }
                },
                "required": [
                    "path",
                    "old_text",
                    "new_text"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "todo",
            "description": "Update the task plan. Each item has 'content' (string) and 'status' (pending/in_progress/completed). Use this to track progress on multi-step tasks. Only ONE item should be in_progress at a time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string",
                                    "enum": [
                                        "pending",
                                        "in_progress",
                                        "completed"
                                    ]
                                }
                            },
                            "required": [
                                "content",
                                "status"
                            ]
                        }
                    }
                },
                "required": [
                    "items"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task",
            "description": "Run a subtask in an isolated context ASYNCHRONOUSLY (M4). Returns a task_id immediately without blocking the main loop; the subagent runs in the background and its final summary is injected into the next round as <background-results>. Use this for research, analysis, or any work whose intermediate output the parent does not need to see. IMPORTANT: after dispatching, continue working and check the next round's <background-results> for the summary — do not expect the result in this tool's return value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The task description for the subagent"
                    },
                    "persona": {
                        "type": "string",
                        "description": "Optional custom system prompt for the subagent (defaults to the standard research-agent persona)"
                    }
                },
                "required": [
                    "prompt"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Load domain-specific guidelines and best practices. Use this when the current task involves a specific domain like testing, git workflow, code review, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Name of the skill to load"
                    }
                },
                "required": [
                    "skill_name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compact",
            "description": "Compress the conversation history into a summary. Use when the context is getting long and you want to clean up before continuing.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_create",
            "description": "Create a new task with optional dependencies. Use this to break down complex work into a DAG of subtasks. Each task is persisted as a JSON file and can be tracked independently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "What the task is about"
                    },
                    "blocked_by": {
                        "type": "array",
                        "items": {
                            "type": "integer"
                        },
                        "description": "IDs of tasks that must complete before this one"
                    }
                },
                "required": [
                    "subject"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_update",
            "description": "Update a task's status. Set to in_progress when starting work, completed when done. Completing a task automatically unblocks downstream tasks that depend on it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer"
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "pending",
                            "in_progress",
                            "completed"
                        ]
                    },
                    "owner": {
                        "type": "string",
                        "description": "Which agent owns this task"
                    }
                },
                "required": [
                    "task_id",
                    "status"
                ]
            }
        }
    }
]

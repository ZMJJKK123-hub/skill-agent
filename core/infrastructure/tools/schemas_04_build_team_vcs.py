# -*- coding: utf-8 -*-
"""工具 schema 分片 4/9（12 个，域: build+team+vcs；保持旧 core/tools.py 原序，禁止重排）。"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "respond_to_request",
            "description": "Approve or reject a protocol request (Plan Approval Protocol). Called by the leader to respond to a teammate's plan submission. On reject, provide a reason; the teammate will revise and resubmit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "req_id": {
                        "type": "string",
                        "description": "The request ID shown in <pending-requests>"
                    },
                    "decision": {
                        "type": "string",
                        "enum": [
                            "approve",
                            "reject"
                        ],
                        "description": "approve = proceed with execution; reject = revise the plan"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the decision (especially on reject)"
                    }
                },
                "required": [
                    "req_id",
                    "decision"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "protocol_status",
            "description": "Show all protocol requests (shutdown handshakes and plan approvals) and their current status: pending/approved/rejected.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "claim_task",
            "description": "Atomically claim a task from the task board (.tasks/) so it becomes yours (in_progress + owner). Only pending, unowned, unblocked tasks can be claimed. If another agent already claimed it, this fails and you should try another task. Use task_list to see available tasks, then claim_task to grab one.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to claim"
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
            "name": "worktree_create",
            "description": "Create a git worktree for a task and bind it: the task gets an isolated working directory under <repo>/.worktrees/task-<id> and auto-advances to in_progress. Work on the task inside that directory so parallel agents never overwrite each other. If the target repo is NOT the project root (e.g. a sub-repo like demo/demo-s12), pass repo explicitly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to isolate"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Optional branch name (default: task-<id>)"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Optional git repo root to create the worktree in (default: project root)"
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
            "name": "worktree_remove",
            "description": "Tear down a task's worktree: removes the directory, unregisters it, and cleans up the branch. complete_task=True also marks the task completed; merge=True first merges the worktree branch back to the main branch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer"
                    },
                    "complete_task": {
                        "type": "boolean",
                        "description": "Mark the task completed (default true)"
                    },
                    "merge": {
                        "type": "boolean",
                        "description": "Merge the worktree branch back to main before removing (default false)"
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
            "name": "worktree_run",
            "description": "Run a shell command inside a task's worktree directory without switching your working base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer"
                    },
                    "command": {
                        "type": "string"
                    }
                },
                "required": [
                    "task_id",
                    "command"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_use",
            "description": "Switch THIS agent's working base to a task's worktree (thread-isolated). After switching, all your bash/read_file/write_file/edit_file operations are confined to that worktree. Pass task_id=0 or omit to switch back to the main directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "Task whose worktree to switch into; 0 or null switches back to main"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_list",
            "description": "Show the worktree registry: each worktree's task binding, branch, status and whether its directory exists.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "worktree_recover",
            "description": "Rebuild state after a crash by cross-checking the event stream, the worktree registry and the disk: roll back half-finished create ops, clean orphaned registry entries and flag orphaned directories.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "build_mod_jar_forge",
            "description": "Build the Forge mod project into an installable jar by running the Gradle wrapper (gradlew build). This takes several minutes on first build (downloads deps + remaps). On success, copies the jar(s) from build/libs/ into the project's dist/ folder so they can be placed directly in .minecraft/mods/. Parameters: gradle_task (default 'build').",
            "parameters": {
                "type": "object",
                "properties": {
                    "gradle_task": {
                        "type": "string"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_game_test_server",
            "description": "Compile and run the Forge GameTestServer (gradlew runGameTestServer) to execute ALL @GameTest tests in the mod project. Run after writing your mod code + game tests, then call read_game_test_log to inspect run/logs/latest.log and fix failures. First run takes minutes (Gradle downloads + remap). Ensures run/eula.txt automatically. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gradle_task": {
                        "type": "string",
                        "description": "Optional gradle task name (default 'runGameTestServer')"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_game_test_log",
            "description": "Read the tail of <mod working dir>/run/logs/latest.log (produced by run_game_test_server) to see GameTest results and errors. Use this after running GameTestServer: errors are almost always at the end of the log. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "integer",
                        "description": "Optional number of lines from the end to read (default 200, max 2000)"
                    }
                }
            }
        }
    }
]

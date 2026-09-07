# -*- coding: utf-8 -*-
"""工具 schema 分片 8/9（10 个，域: diag+game+vcs；保持旧 core/tools.py 原序，禁止重排）。"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "start_mc_test_client",
            "description": "Start the TEST client (gradlew runTestClient — loads BOTH src/main and src/test, non-blocking, tracked like mc-client). Use it only when you need src/test helper code in the client; for AgentBridge/bridge_command use plain start_mc_client instead — AgentBridge lives in src/main (per bridge_command setup), which is already on the runClient classpath. Wait for readiness with wait_for_log pattern 'Sound engine started' (timeout 180); stop with stop_mc_process.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {
                        "type": "string",
                        "description": "Optional MOD project dir (default current worktree)"
                    },
                    "handle": {
                        "type": "string",
                        "description": "Process handle (default mc-client)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mc_status",
            "description": "Show tracked Minecraft server/client processes, open ports, and latest log readiness hints.",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {
                        "type": "string",
                        "description": "Optional handle filter (e.g. mc-server, mc-client)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop_mc_process",
            "description": "Stop a tracked Minecraft process by handle, or all with 'all' (default). Uses taskkill /T to kill the process tree.",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {
                        "type": "string",
                        "description": "handle (mc-server/mc-client) or 'all' (default all)"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force kill (default true)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "kill_game",
            "description": "Force kill all (or a named) Minecraft dev process. Alias for stop_mc_process(force=true).",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {
                        "type": "string",
                        "description": "Optional handle; default 'all'"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "server_console",
            "description": "Send a console command to the local Minecraft server process via stdin if possible, otherwise fallback to RCON.",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {
                        "type": "string",
                        "description": "Process handle (default mc-server)"
                    },
                    "command": {
                        "type": "string",
                        "description": "Command to send (e.g. 'list', 'save-all')"
                    },
                    "text": {
                        "type": "string",
                        "description": "Alias of command"
                    },
                    "rcon_password": {
                        "type": "string",
                        "description": "Optional RCON password for fallback"
                    },
                    "rcon_port": {
                        "type": "integer",
                        "description": "Optional RCON port (default 25575)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait_for_port",
            "description": "Wait until a TCP port is open (e.g. 25565 server or 25575 RCON).",
            "parameters": {
                "type": "object",
                "properties": {
                    "port": {
                        "type": "integer",
                        "description": "TCP port to probe"
                    },
                    "host": {
                        "type": "string",
                        "description": "Host (default 127.0.0.1)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Max seconds (default 60)"
                    }
                },
                "required": [
                    "port"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tail_log",
            "description": "Read the tail of a log file (default run/logs/latest.log). Useful for quick diagnostics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "log_path": {
                        "type": "string",
                        "description": "Optional custom log path"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of tail lines (default 80)"
                    },
                    "base": {
                        "type": "string",
                        "description": "Optional project dir"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait_for_mc_ready",
            "description": "Wait until a Minecraft server/client process is ready: log pattern matched or port open.",
            "parameters": {
                "type": "object",
                "properties": {
                    "handle": {
                        "type": "string",
                        "description": "Process handle (default mc-server)"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Regex readiness pattern (default 'Done (')"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Max seconds (default 120)"
                    },
                    "check_port": {
                        "type": "boolean",
                        "description": "Also check server port (default true)"
                    },
                    "port": {
                        "type": "integer",
                        "description": "Port to check (default 25565)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Show git working tree status (git status --short).",
            "parameters": {
                "type": "object",
                "properties": {
                    "workdir": {
                        "type": "string",
                        "description": "Optional project dir"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_diff",
            "description": "Show git diff (--stat by default) for the working tree.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workdir": {
                        "type": "string",
                        "description": "Optional project dir"
                    },
                    "stat": {
                        "type": "boolean",
                        "description": "Use --stat (default true)"
                    }
                },
                "required": []
            }
        }
    }
]

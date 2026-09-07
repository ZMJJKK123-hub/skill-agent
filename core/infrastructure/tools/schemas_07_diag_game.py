# -*- coding: utf-8 -*-
"""工具 schema 分片 7/9（9 个，域: diag+game；保持旧 core/tools.py 原序，禁止重排）。"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_game_command",
            "description": "Send a Minecraft RCON command to a running server/client (e.g. /give, /tp, /reload). Requires RCON enabled and password.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to send, e.g. 'give @p minecraft:diamond 1'"
                    },
                    "host": {
                        "type": "string",
                        "description": "RCON host (default 127.0.0.1)"
                    },
                    "port": {
                        "type": "integer",
                        "description": "RCON port (default 25575)"
                    },
                    "password": {
                        "type": "string",
                        "description": "RCON password; if omitted uses DSH_RCON_PASSWORD"
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
            "name": "game_input",
            "description": "Generic game input. action='key' with key name, or action='type' with text. Sends input to the focused game window.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "key",
                            "type"
                        ],
                        "description": "key=press single key, type=type text"
                    },
                    "key": {
                        "type": "string",
                        "description": "Key name for key action (e.g. enter, e, esc)"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type for type action"
                    }
                },
                "required": [
                    "action"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Press and release a single key in the focused window (e.g. 'e' to open inventory, 'esc').",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Key name (enter, esc, e, space, f1, etc.)"
                    }
                },
                "required": [
                    "key"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type Unicode text into the focused window (useful for chat commands or search boxes).",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    }
                },
                "required": [
                    "text"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait_for_log",
            "description": "Wait until a regex pattern appears in a log file (default run/logs/latest.log). Useful for waiting for server/client startup or test completion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Max seconds to wait (default 60)"
                    },
                    "log_path": {
                        "type": "string",
                        "description": "Optional custom log path"
                    }
                },
                "required": [
                    "pattern"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait_for_screen",
            "description": "Wait a few seconds, take a screenshot, and optionally analyze it with the vision API. Use to let the game render before checking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {
                        "type": "integer",
                        "description": "Seconds to wait (default 5)"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Optional vision analysis prompt"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_visual_loop",
            "description": "Run a visual verification loop: optionally send RCON commands, screenshot, analyze with vision, repeat. Returns all screenshot paths and analyses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Vision analysis prompt (e.g. 'is the item icon rendered correctly?')"
                    },
                    "max_attempts": {
                        "type": "integer",
                        "description": "Number of attempts (default 3)"
                    },
                    "interval": {
                        "type": "integer",
                        "description": "Seconds between attempts (default 5)"
                    },
                    "command": {
                        "type": "string",
                        "description": "Optional RCON command to send before each screenshot"
                    },
                    "rcon_password": {
                        "type": "string",
                        "description": "Optional RCON password"
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
            "name": "start_mc_server",
            "description": "Start the Forge dedicated server (gradlew runServer) in the background. Non-blocking; use mc_status / wait_for_log / wait_for_port to check readiness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "base": {
                        "type": "string",
                        "description": "Optional MOD project dir (default current worktree)"
                    },
                    "handle": {
                        "type": "string",
                        "description": "Process handle (default mc-server)"
                    },
                    "rcon_port": {
                        "type": "integer",
                        "description": "If set, write enable-rcon/rcon.port to run/server.properties"
                    },
                    "rcon_password": {
                        "type": "string",
                        "description": "If set, write rcon.password to run/server.properties and remember for RCON"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_mc_client",
            "description": "Start the Minecraft GUI client (gradlew runClient) in the background. Non-blocking; use mc_status / wait_for_screen to observe.",
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
    }
]

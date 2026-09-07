# -*- coding: utf-8 -*-
"""工具 schema 分片 6/9（11 个，域: basic+build+diag+game；保持旧 core/tools.py 原序，禁止重排）。"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "press_keys",
            "description": "Execute a deterministic keyboard sequence on the focused window (code-level UI navigation — no screenshot needed to decide each step). Each item is: a key name (tab/enter/esc/e/t/up/down...), 'wait:ms' to pause, or 'type:text' to type text. Use for fixed vanilla menu flows, e.g. main menu -> Singleplayer -> Create New World. Verify the RESULT with ONE wait_for_screen after the sequence instead of screenshotting per step.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sequence": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Ordered steps, e.g. ['tab', 'enter', 'wait:1500', 'type:My World']"
                    }
                },
                "required": [
                    "sequence"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_resources",
            "description": "Validate all MOD resource files (item model definitions, models, textures, blockstates, recipes, lang, pack.mcmeta) and report missing/invalid references. Use after writing assets to catch purple-missing-texture issues before running the game.",
            "parameters": {
                "type": "object",
                "properties": {
                    "modid": {
                        "type": "string",
                        "description": "Optional mod id; auto-detected from mods.toml/@Mod when omitted"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "parse_gametest_results",
            "description": "Parse the latest GameTest log and return a concise pass/fail summary with failed test names and error lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines": {
                        "type": "integer",
                        "description": "Tail lines to scan (default 200, max 2000)"
                    },
                    "log_path": {
                        "type": "string",
                        "description": "Optional custom log path; default run/logs/latest.log"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_crash_report",
            "description": "Read the latest crash report from crash-reports/ and return the head of the report for debugging.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_lines": {
                        "type": "integer",
                        "description": "Lines to return (default 120)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_crash",
            "description": "Extract key facts from the latest crash report: description, exception, caused by, stack frames.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_lines": {
                        "type": "integer",
                        "description": "Max stack frames to include (default 60)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_environment",
            "description": "Detect current workspace environment: Java version, Gradle wrapper, mod loader, mod id, MC/Forge version, source layout, resource namespaces.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_artifact",
            "description": "Verify built jar(s) and source zip contain required metadata/resources and no forbidden runtime directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "jar_path": {
                        "type": "string",
                        "description": "Optional specific jar path; default uses latest dist/*.jar"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "download_file",
            "description": "Download a URL to a workspace path. Use for reference files, textures, or external resources.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to download"
                    },
                    "dest_path": {
                        "type": "string",
                        "description": "Destination path inside workspace"
                    }
                },
                "required": [
                    "url",
                    "dest_path"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_archive",
            "description": "Extract a zip/tar.gz/jar archive into a workspace directory (zip-slip safe).",
            "parameters": {
                "type": "object",
                "properties": {
                    "archive_path": {
                        "type": "string",
                        "description": "Archive path inside workspace"
                    },
                    "dest_path": {
                        "type": "string",
                        "description": "Destination directory inside workspace"
                    }
                },
                "required": [
                    "archive_path",
                    "dest_path"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cleanup_workspace",
            "description": "Clean build/runtime artifacts. mode='cache' removes build/.gradle/__pycache__/agent.log; mode='all' also removes run/run-data/.worktrees/.team/.tasks/.transcripts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": [
                            "cache",
                            "all"
                        ],
                        "description": "Cleanup mode (default cache)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_auto_mode",
            "description": "Toggle auto mode for the current agent process. When enabled, ask_user_question will not block and the agent uses reasonable defaults.",
            "parameters": {
                "type": "object",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "description": "true to enable auto mode, false to disable"
                    }
                },
                "required": [
                    "enabled"
                ]
            }
        }
    }
]

# -*- coding: utf-8 -*-
"""工具 schema 分片 9/9（6 个，域: basic+build+vcs；保持旧 core/tools.py 原序，禁止重排）。"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Stage all (or given files) and commit. Optionally push.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Commit message"
                    },
                    "workdir": {
                        "type": "string",
                        "description": "Optional project dir"
                    },
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Optional specific files to commit; default -A"
                    },
                    "push": {
                        "type": "boolean",
                        "description": "Also git push (default false)"
                    }
                },
                "required": [
                    "message"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "snapshot",
            "description": "Create a git checkpoint commit (snapshot). Returns short HEAD hash.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Snapshot name (default checkpoint)"
                    },
                    "workdir": {
                        "type": "string",
                        "description": "Optional project dir"
                    },
                    "message": {
                        "type": "string",
                        "description": "Optional commit message; default 'snapshot: <name>'"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restore_snapshot",
            "description": "Hard reset to a previous snapshot/commit. Destructive: discards uncommitted changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ref": {
                        "type": "string",
                        "description": "Commit hash/branch/tag to restore"
                    },
                    "workdir": {
                        "type": "string",
                        "description": "Optional project dir"
                    }
                },
                "required": [
                    "ref"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "parse_build_output",
            "description": "Extract compile errors and FAILED Gradle tasks from build log or raw text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "log_path": {
                        "type": "string",
                        "description": "Optional path to build log"
                    },
                    "raw_text": {
                        "type": "string",
                        "description": "Optional raw build output"
                    },
                    "base": {
                        "type": "string",
                        "description": "Optional project dir for relative log_path"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_mod_test_cycle",
            "description": "One-call MOD test loop: validate_resources -> build jar -> run_test_gametest -> parse results. Returns full status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "modid": {
                        "type": "string",
                        "description": "Optional modid for resource validation"
                    },
                    "validate": {
                        "type": "boolean",
                        "description": "Run validate_resources (default true)"
                    },
                    "build": {
                        "type": "boolean",
                        "description": "Run gradlew build (default true)"
                    },
                    "run_tests": {
                        "type": "boolean",
                        "description": "Run run_test_gametest (default true)"
                    },
                    "build_timeout": {
                        "type": "integer",
                        "description": "Build timeout seconds (default 900)"
                    },
                    "test_timeout": {
                        "type": "integer",
                        "description": "GameTest timeout seconds (default 180)"
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
            "name": "activate_test_mode",
            "description": "Unlock the full toolset for this session. Call this when you need to build, run GameTest, start server/client, use game input/visual verification, or use Git snapshots. After calling, all remaining tools and their usage guide become visible for the rest of the session.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

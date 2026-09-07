# -*- coding: utf-8 -*-
"""工具 schema 分片 1/9（8 个，域: basic；保持旧 core/tools.py 原序，禁止重排）。"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Run a shell command.",
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
            "name": "grep",
            "description": "Search file contents with a regex across the workspace (skips build/runtime dirs). Returns 'relative/path:line: content'. Useful for finding exact APIs/errors in mc_java_sources, skills, or generated code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex to search for"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory or file to search (default workspace root)"
                    },
                    "glob_filter": {
                        "type": "string",
                        "description": "Optional filename glob filter, e.g. *.java"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max matches to return (default 50)"
                    },
                    "context_lines": {
                        "type": "integer",
                        "description": "Number of surrounding lines to include per match (default 0)"
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
            "name": "search_api",
            "description": "Focused API dictionary lookup: search MC/Forge source for a literal symbol (auto regex-escaped) and return match lines. Set context_lines>0 to see surrounding lines. If you need the full constructor/method/record signature, DO use read_file on the reported .java file — full source reading is allowed in the fix loop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Exact class/method/field name or error symbol, e.g. isClientSide or FMLClientSetupEvent.getBus"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search (default mc_java_sources)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max match lines to return (default 10)"
                    },
                    "context_lines": {
                        "type": "integer",
                        "description": "Number of surrounding lines to include per match (default 0)"
                    }
                },
                "required": [
                    "symbol"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "Find files by glob pattern under the workspace (skips build/runtime dirs).",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern, e.g. **/*.java"
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
            "name": "web_search",
            "description": "Search the web (best-effort DuckDuckGo HTML). Returns a list of title + URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max results (default 5)"
                    }
                },
                "required": [
                    "query"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_minecraft_docs",
            "description": "Search Minecraft/Forge-specific documentation sites (Minecraft Wiki, Forge Docs, NeoForged, GitHub) for exact APIs, versions, JSON formats, and mod development references.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query, e.g. 'item model definition 1.21.11'"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max results (default 5)"
                    }
                },
                "required": [
                    "query"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetch a URL and return its text/HTML content (capped).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch"
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "Max characters to return (default 100000)"
                    }
                },
                "required": [
                    "url"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ask_user_question",
            "description": "Ask the user one or more clarifying questions and wait for their answers. Use when the requirement is ambiguous and you need the user to choose or clarify. Pass 'questions' as an array to ask several at once (the user sees them all together, can answer each with a preset option or free text, and confirms once); each item has 'question' (string) and optional 'options' (list of preset choices). For a single question you may also use the legacy 'question' + 'options' form. The return value is a JSON array of {'question', 'answer'} pairs — one per question, in the order you asked them.",
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                    "description": "The question to ask"
                                },
                                "options": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    },
                                    "description": "Optional preset choices"
                                }
                            },
                            "required": [
                                "question"
                            ]
                        },
                        "description": "Multiple questions to ask at once (recommended)"
                    },
                    "question": {
                        "type": "string",
                        "description": "[legacy] Single question to ask"
                    },
                    "options": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "[legacy] Optional preset choices for the single question"
                    }
                },
                "required": []
            }
        }
    }
]

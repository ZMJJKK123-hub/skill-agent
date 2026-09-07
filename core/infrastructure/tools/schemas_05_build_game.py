# -*- coding: utf-8 -*-
"""工具 schema 分片 5/9（10 个，域: build+game；保持旧 core/tools.py 原序，禁止重排）。"""
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_client",
            "description": "Run 'gradlew runClient' in the BACKGROUND (non-blocking). Launches the GUI Minecraft client using ONLY src/main production code. Use mc_status / wait_for_screen to observe; stop with stop_mc_process(handle='mc-client'). Does not block the agent loop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Kept for compatibility; ignored because startup is now background"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_server",
            "description": "Run 'gradlew runServer' in the BACKGROUND (non-blocking). Launches a headless dedicated server using ONLY src/main code. Use wait_for_log('Done (') / wait_for_port(25565) to check boot; stop with stop_mc_process(handle='mc-server'). Does not block the agent loop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Kept for compatibility; ignored because startup is now background"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_data_gen",
            "description": "Run 'gradlew runData' - runs Data Generators against src/main to auto-generate model/recipe/loot/lang JSON assets from DataProvider code. Use after writing/updating DataProviders. Detect failure: 'BUILD SUCCESSFUL' absent in log means DataGen error; extract failing class+line. DIFFERENT from run_test_data: run_test_data also loads src/test and generates test-only placeholders without polluting shipped assets. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 120)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_test_client",
            "description": "Run 'gradlew runTestClient' - launches GUI client loading BOTH src/main and src/test. Use when you need src/test helper tools (spawn/cheat command mods) for manual in-game debugging. DIFFERENT from run_client: run_client is production-only and never contains test helpers; run_test_client is the isolated-testing variant. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 90)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_test_server",
            "description": "Run 'gradlew runTestServer' - launches a headless dedicated server loading BOTH src/main and src/test. Use to exercise network sync / multi-player simulations that depend on isolated test code. DIFFERENT from run_server: run_server is production-only dedicated server; run_test_server loads src/test helpers. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 90)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_test_data",
            "description": "Run 'gradlew runTestData' - Data Generator loading BOTH src/main and src/test. Use when you wrote DataGen scripts inside src/test for test placeholders/temporary recipes; generates them WITHOUT polluting the shipped jar assets. DIFFERENT from run_data_gen: run_data_gen targets production assets only. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 120)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_test_gametest",
            "description": "RUN THIS FOR AGENT SELF-VERIFICATION: 'gradlew runTestGameTestServer' - GameTest automation server loading BOTH src/main and src/test, runs every @GameTest under src/test/java (isolated; never packaged into the final jar). THE core of the write->run->fix loop: write assertion tests in src/test, run this, parse Passed/Failed, fix src/main logic, re-run until pass. DIFFERENT from run_game_test_server: the latter only scans src/main @GameTest (shipped in jar as egg/getreward tests); for Agent validation you MUST use run_test_gametest. Leader/MAIN agent tool only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "integer",
                        "description": "Optional seconds (default 180)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "screenshot",
            "description": "Capture the current screen (full screen by default, or a region) and save it under .screenshots/ in the workspace. Returns the image path. Use together with analyze_image to inspect game/MOD visuals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {
                        "type": "object",
                        "description": "Optional screen region to capture.",
                        "properties": {
                            "left": {
                                "type": "integer",
                                "description": "Left pixel coordinate"
                            },
                            "top": {
                                "type": "integer",
                                "description": "Top pixel coordinate"
                            },
                            "width": {
                                "type": "integer",
                                "description": "Region width in pixels"
                            },
                            "height": {
                                "type": "integer",
                                "description": "Region height in pixels"
                            }
                        },
                        "required": [
                            "left",
                            "top",
                            "width",
                            "height"
                        ]
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_image",
            "description": "Analyze an image file (e.g. a screenshot saved by the screenshot tool) using the separately configured vision API. Returns the model's textual description. Useful for checking whether a game/MOD screen looks normal, shows errors, or has rendered correctly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the image file (absolute or relative to workspace)"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Optional specific question/instruction about the image"
                    }
                },
                "required": [
                    "image_path"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bridge_command",
            "description": "In-process UI automation via the AgentBridge mod (requires 3 setup steps, ALL mandatory): 1) copy starter/bridge/AgentBridge.java to src/main/java/com/agentbridge/AgentBridge.java (MAIN sources — test sources load in a duplicate classloader and break); 2) at the end of your main @Mod constructor add EXACTLY: if (net.minecraftforge.fml.loading.FMLEnvironment.dist.isClient()) { new com.agentbridge.AgentBridge(); } — the dist guard is MANDATORY: without it runTestGameTestServer crashes with 'Attempted to load class ... for invalid dist DEDICATED_SERVER' (DISTXFORM); 3) start the client with start_mc_client. ops: screen_info (list current screen's buttons with index/label — read the UI as CODE, no screenshot), click {index} (invoke the button's onPress handler directly, not a simulated mouse), set_text {index,value} (fill an EditBox), chat {text} (send '/give @s <modid>:<item>' etc.), screenshot {name} (game-renderer screenshot, works in background window).",
            "parameters": {
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "enum": [
                            "screen_info",
                            "click",
                            "set_text",
                            "chat",
                            "screenshot"
                        ]
                    },
                    "index": {
                        "type": "integer",
                        "description": "widget index from screen_info (click/set_text)"
                    },
                    "value": {
                        "type": "string",
                        "description": "text value (set_text)"
                    },
                    "text": {
                        "type": "string",
                        "description": "chat/command text (chat)"
                    },
                    "name": {
                        "type": "string",
                        "description": "screenshot file name (screenshot)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "seconds to wait for result (default 10)"
                    }
                },
                "required": [
                    "op"
                ]
            }
        }
    }
]

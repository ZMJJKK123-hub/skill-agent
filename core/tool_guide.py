# -*- coding: utf-8 -*-
"""Base and extended tool usage guides (English).

The agent initially only receives BASE_TOOL_GUIDE. When it calls
activate_test_mode, EXTENDED_TOOL_GUIDE is appended to the system prompt and
all tools become visible for the rest of the session.
"""

BASE_TOOL_GUIDE = r"""## TOOL USAGE RULES (Development Phase)

1. Staged tools: right now only the base development tools are available. When you need to build/test/verify the
   mod in-game, call `activate_test_mode` first to unlock ALL tools (stays unlocked for this session).
2. Prefer existing tools. Only use `bash` when no dedicated tool exists. Always use read_file / write_file / edit_file
   / glob / grep for files; NEVER write files via bash redirection.
3. Full tool manual: docs/agent/TOOL_GUIDE.md (read_file/grep the relevant section when needed).
4. On any error or thinking loop: first read docs/agent/ERROR_LIST.md; if the fix is not there, resolve it and append it.
5. Naming: derive modid/package/class/item/block names from the user's request. NEVER keep template defaults
   (examplemod / example_item / example_block).
6. Build-file guard: NEVER change build system/plugins (e.g. don't switch to NeoGradle/NeoForge), Forge version,
   dependency versions, Gradle wrapper (gradle-wrapper.properties), settings.gradle pluginManagement structure, or
   gradle.properties daemon/JVM/cache settings. You ARE allowed to edit ONLY modid/namespace references in
   build.gradle/settings.gradle when renaming the mod (e.g. `forge.enabledGameTestNamespaces`, DataGen `--mod`,
   group/modId, `rootProject.name`, `archivesName`). If a build-system change seems needed, do not make it — report it.
"""

EXTENDED_TOOL_GUIDE = r"""## EXTENDED TOOL GUIDE (Testing / Verification Phase)

You unlocked the full 80-tool set via `activate_test_mode`. Continue following the tool-first rule: prefer a
dedicated tool; use bash only when no tool exists.

### Build / Data / GameTest
- build_mod_jar_forge: runs `gradlew build` and copies the jar to dist/. Use to verify compilation/packaging.
- run_data_gen: Forge DataGen for production assets (models/recipes/loot/lang).
- run_test_data: DataGen that also loads src/test (test-only placeholders, does NOT pollute production assets).
- run_game_test_server: generic GameTest server; prefer run_test_gametest for self-checks.
- run_test_gametest: CORE verifier - runs runTestGameTestServer and returns pass/fail. MUST use after code changes.
- run_test_server: test dedicated server (loads src/test).
- run_test_client: test GUI client (loads src/test).
- parse_gametest_results: parses run/logs/latest.log into pass/fail/error summary (RESULT).
- read_game_test_log: read the GameTest log directly.
- parse_build_output: extract error: and FAILED tasks from build logs to locate compile errors fast.
- run_mod_test_cycle: ONE-CALL loop = validate_resources -> build_mod_jar_forge -> run_test_gametest -> parse. Prefer it;
  do NOT re-call the steps it already runs.

### Server / Client lifecycle
- run_server: start production dedicated server in background (src/main), equals start_mc_server (default).
- run_client: start production GUI client in background (src/main), equals start_mc_client (default).
- start_mc_server: start server in background; if rcon_port/rcon_password are given it auto-writes server.properties
  (enable-rcon/rcon.port/rcon.password/online-mode=false).
- start_mc_client: start client in background; observe with wait_for_screen / screenshot / analyze_image.
- mc_status: show tracked processes, open ports and log readiness hints. Call after every start.
- stop_mc_process: stop a process by handle (mc-server/mc-client), default all.
- kill_game: force kill all/named game processes (taskkill tree).
- server_console: write a command to the server stdin; falls back to RCON if stdin is unavailable.
- wait_for_mc_ready: wait until a process is ready (log pattern match OR port open).
- wait_for_port: wait until a TCP port is open (e.g. 25565 / 25575).

### In-game interaction
- send_game_command: send an RCON command to a running server (needs RCON password + port).
- game_input: generic input; action=key (single key) or action=type (text).
- press_key: press a single key into the focused window (e.g. e / esc).
- type_text: type Unicode text into the focused window.
- wait_for_log: wait until a regex appears in a log.
- wait_for_screen: wait a few seconds, screenshot, optionally analyze_image.
- verify_visual_loop: visual loop = optional RCON command -> screenshot -> analyze_image, repeated. It already
  screenshots and analyzes internally; do NOT stack manual screenshot+analyze_image on top.

### Screenshot / vision
- screenshot: capture the current screen, returns a path.
- analyze_image: ask the vision model about an image. Use together with screenshot/verify_visual_loop.

### Logs / crash / artifact
- read_crash_report: read the latest crash report.
- analyze_crash: analyze a crash report (cause/stack).
- verify_artifact: check a jar/zip for mods.toml/pack.mcmeta/assets/data and junk files.
- tail_log: quickly read the end of a log (better than read_file for live output).

### Git / snapshot
- git_status / git_diff: inspect working tree.
- git_commit: commit all changes (default git add -A).
- snapshot: create a git checkpoint commit, returns HEAD.
- restore_snapshot: hard reset to a previous snapshot (DESTRUCTIVE - only when you are sure).

### In-process UI automation (bridge_command — PREFERRED, no focus stealing)
- Before client verification: copy `starter/bridge/AgentBridge.java` to `src/test/java/com/agentbridge/AgentBridge.java` and add ONE line at the end of your main @Mod constructor (reflection, so production runClient compiles without the test classpath): `try { Class.forName("com.agentbridge.AgentBridge").getConstructor().newInstance(); } catch (Throwable ignored) {}`. Rebuild, then start the client with `start_mc_test_client` (NOT run_client/run_test_client — the bridge is only on the runTestClient classpath, and start_mc_test_client is non-blocking + properly killable via stop_mc_process).
- Then drive the UI as CODE, no screenshots needed to decide:
  1) `bridge_command op=screen_info` → returns screen class + widgets [{index,label,active,editable}]. Read labels to decide.
  2) `bridge_command op=click index=<n>` → invokes the button's onPress handler directly (background window OK).
  3) `bridge_command op=set_text index=<n> value=<name>` → fill world-name boxes.
  4) `bridge_command op=chat text="/give @s <modid>:<item>"` then `op=chat text="/give @s minecraft:stone_pickaxe"` (so it can mine if needed).
  5) ONE `bridge_command op=screenshot name=icon_check` + analyze_image at the END for the icon verdict — game-renderer screenshots work even when the window is unfocused/minimized.
- Typical flow: title screen → click "Singleplayer" → screen_info → click "Create New World" → set_text world name → click "Create New World" → wait_for_log "joined the game" (timeout 180) → give item → screenshot → analyze.
- Indexes change between screens: always screen_info after a screen transition, then click.

### Deterministic client menu navigation (press_keys — FALLBACK when bridge not compiled)
- Use press_keys for vanilla menu flows instead of screenshot->decide->press loops. Verify each SCREEN transition with ONE wait_for_screen, not one screenshot per button.
- Recipe (Tab order is layout-based and locale-independent; if focus lands elsewhere, adjust the number of 'tab' steps ONCE from the verification screenshot and re-run the sequence):
  - Main menu -> world list: press_keys ["tab", "enter"] (first Tab focuses Singleplayer), then wait:800.
  - World list -> Create New World screen: 'tab' steps until "Create New World" is focused, then "enter".
  - Create screen: the world-name field starts focused -> ["type:verify"]; then 'tab' steps to "Create New World" and "enter".
  - World loaded: wait_for_log pattern "joined the game" (timeout 180), then interact.
- In-world item check: press_keys ["t"] opens chat; ["type:/give @s <modid>:<item>", "enter"]; ["e"] opens inventory; then ONE screenshot and ask analyze_image whether your item icon renders correctly in the inventory grid.
- First client boot compiles shaders/caches (1-3 min): run wait_for_mc_ready(handle="mc-client", pattern="Sound engine started") first, then wait:10000, then interact. NEVER screenshot repeatedly during the loading splash — the menu buttons do not exist yet.
- The screenshot auto-focuses and maximizes the Minecraft window; game_input/press_keys go to the focused window, so do not switch windows during a verify loop.

### Couplings / pitfalls
- run_mod_test_cycle already includes validate/build/gametest/parse. Do not repeat them.
- If start_mc_server got RCON params, send_game_command works directly; do not hand-edit server.properties.
- server_console and send_game_command both send commands; prefer server_console (stdin), fallback RCON.
- wait_for_mc_ready already checks log+port; do not call wait_for_log + wait_for_port separately.
- git_commit/snapshot both do git add -A; don't git add first then call them.
- Prefer dedicated tools over bash for gradlew, git, findstr, curl, etc.
- COMPLETION: when run_test_gametest prints "All required tests passed" AND dist/*.jar exists -> the task is DONE.
  One aggregated @GameTest is enough; test count is NOT completion. Do not keep verifying/enhancing passing code.
"""
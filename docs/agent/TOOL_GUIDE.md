# Agent Tool Guide

> This is the agent's full tool manual. It exists so no information is lost after context compaction.
> The system prompt only keeps a slim version; to see details for a tool, `read_file` the relevant section
> or `grep` for the tool name.

## General Rules

1. Prefer existing tools; use `bash` only when no dedicated tool exists.
2. Use `read_file` / `write_file` / `edit_file` / `glob` / `grep` for files; never write files via bash redirection.
3. Staged tools: initially only base development tools are unlocked. To build/test/verify in-game, call
   `activate_test_mode` to unlock everything.
4. On any error or thinking loop, first read `docs/agent/ERROR_LIST.md`; if not solved, resolve and append.
5. Typical self-loop:
   `validate_resources` -> `activate_test_mode` -> `run_mod_test_cycle`
   -> on failure `read_game_test_log` / `read_crash_report` / `analyze_crash` / `tail_log`
   -> fix -> verify again -> `git_commit` / `snapshot`.

## Tool Groups

### Base development tools (initially unlocked)

Files/code: `read_file` `write_file` `edit_file` `glob` `grep`
Shell: `bash` `run_in_background`
Worktrees: `worktree_create` `worktree_list` `worktree_use` `worktree_remove` `worktree_run` `worktree_recover`
Search: `web_search` `web_fetch` `search_minecraft_docs`
Environment/utilities: `detect_environment` `validate_resources` `download_file` `extract_archive` `cleanup_workspace`
Tasks/team/protocol: `todo` `task` `task_create` `task_get` `task_list` `task_update` `task_clear` `claim_task`
`spawn_teammate` `send_to_teammate` `shutdown_teammate` `team_status` `protocol_status`
`request_shutdown` `respond_to_request` `submit_plan`
Session/memory: `set_auto_mode` `compact` `load_skill` `ask_user_question`
Unlock entry: `activate_test_mode`

### Extended tools (after activate_test_mode)

Build/Data/GameTest: `build_mod_jar_forge` `run_data_gen` `run_test_data`
`run_game_test_server` `run_test_gametest` `run_test_server` `run_test_client`
`parse_gametest_results` `read_game_test_log` `parse_build_output` `run_mod_test_cycle`
Server/Client: `run_server` `run_client` `start_mc_server` `start_mc_client`
`mc_status` `stop_mc_process` `kill_game` `server_console`
`wait_for_mc_ready` `wait_for_port`
In-game: `send_game_command` `game_input` `press_key` `type_text`
`wait_for_log` `wait_for_screen` `verify_visual_loop`
Vision: `screenshot` `analyze_image`
Logs/Crash/Artifact: `read_crash_report` `analyze_crash` `verify_artifact` `tail_log`
Git/Snapshot: `git_status` `git_diff` `git_commit` `snapshot` `restore_snapshot`

## Frequent Couplings

- `run_mod_test_cycle` = `validate_resources` + `build_mod_jar_forge` + `run_test_gametest` + `parse_gametest_results`
- `start_mc_server` with `rcon_port` / `rcon_password` auto-writes `server.properties`
- `server_console` writes to stdin first, falls back to RCON on failure
- `wait_for_mc_ready` = log match + port probe; do not wait twice
- `verify_visual_loop` already screenshots and analyzes internally
- `git_commit` / `snapshot` both do `git add -A`

## Forbidden

- Never `taskkill /f /im python.exe` (kills the agent itself)
- Never run bare `gradlew runServer/runClient` via bash; use `start_mc_server` / `start_mc_client`
- Never write files via bash; use `write_file` / `edit_file`
- Never keep guessing the same error without reading the error list

---

## Appendix A: Windows / Environment Hard Rules

- Windows cmd only; use Windows syntax:
  - mkdir without `-p`; `dir` not `ls`; `type` not `cat`; `copy`/`xcopy` not `cp`;
    `del` for files, `rd /s /q` for folders; `where`/`dir /s /b` not `find`/`which`
  - path separators `\` or `/` OK, but do not mix them in one command.
- Write files ONLY via write_file / edit_file (UTF-8). Never bash redirection (`echo >`, `python x.py > out.txt`):
  Windows GBK corrupts Chinese/emoji. If you must save command output, capture it via bash then write with write_file.
- NEVER `taskkill /f /im python.exe` or `node.exe` — the agent itself runs inside python.exe.
- To verify HTTP services, NEVER start them standalone (30s timeout & force kill). Use this single combined command
  (replace PORT):
  ```
  start /b cmd /c "node server.js > server.log 2>&1" & timeout /t 3 /nobreak >nul & curl -s http://localhost:3000/api/users & for /f "tokens=5" %a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %a
  ```
  Breakdown: `start /b` background + redirect; `timeout /t 3` wait; `curl` test; `for /f` kill by port.

## Appendix B: Forge 1.21.11 Hard Facts

- Target: MC `1.21.11`, Forge build `1.21.11-61.2.0`.
- `1.21.11-61.2.0` is a valid version string; never claim it is invalid/wrong.
- The forge dependency is pinned in build.gradle; never change it. Old mapping knowledge does not apply.
- ForgeGradle downloads dependencies on first build to `~/.gradle/`; that is normal. Never curl to look up/rewrite versions.
- On build failure: never change the forge version; if MC classes are missing check the compile classpath
  (local recompiled.jar); on "Could not resolve" check the cache / retry the network; don't rewrite build files
  because of a single error.
- 1.21.11 mapping essentials (full detail in ERROR_LIST.md / forge-simple-min-mod skill):
  - `Item.Properties.humanoidArmor(ArmorMaterial, ArmorType)`; there is NO `ArmorItem` class.
  - `ResourceLocation` is now `Identifier` (`net.minecraft.resources.Identifier`).
  - Registry lookup uses `lookupOrThrow` (not `registryOrThrow`).
  - `@GameTest` has no `template` parameter.

## Appendix C: System Capabilities (todo / DAG / background / team / protocol / worktree)

- todo: lightweight linear list; use for multi-step work; only one in_progress at a time.
- Task DAG (task_create/task_update/task_list/task_get): express dependencies with `blocked_by`; completed tasks
  auto-unblock downstream; todo is in-memory linear, task_* is a persisted DAG.
- Background execution (run_in_background): for commands expected >5s (npm install, big builds, long tests);
  returns an id immediately, result injected next round as `<background-results>`. Fast commands use bash.
- Team (spawn_teammate/send_to_teammate/team_status): give independent parallel subtasks to teammates (own thread,
  own context); results injected as `<teammate-reports>`; roster resets each run (no persistent memory).
- Protocol: request-response state machine (pending -> approved/rejected).
  - Shutdown: use `request_shutdown`, not direct shutdown; a teammate rejects until its writes are flushed.
  - Plan: teammates use `submit_plan`; leader approves via `respond_to_request`; `<pending-requests>` is protocol
    traffic, not user input; inspect with protocol_status.
- Worktree isolation: parallel tasks use worktrees. worktree_create -> worktree_use switches this agent's working
  base (bash/read/write confined to that worktree); worktree_run runs inside a task's worktree;
  worktree_remove(complete_task, merge) tears down; worktree_list/recover inspect/rebuild after a crash.

## Appendix D: Action-Driven Workflow (prevent analysis loops)

- Order: read -> write -> verify -> read again only on failure.
  1. In the first round run_read KNOWN_ISSUES.md + load the relevant skill(s);
  2. start writing code/resources immediately, no heavy exploration first;
  3. after writing, verify with compile/test (compileTestJava / run_test_gametest);
  4. only if tests/compile fail, go back to skills or mc_java_sources to fix and re-verify.
- Never pure-analysis loop: if the same problem (an API error, a WARN) is speculated for 3+ rounds with zero
  concrete action, stop. Each round must lead to an executable next step; when unsure, do the smallest verification
  (read latest.log / run one command).
- For annotations on classes not read at runtime, do not repeatedly javap; run
  `gradlew clean compile... --rerun-tasks` and judge from actual logs.

## Appendix E: SIMPLE MOD FAST PATH (simple item/block + recipe)

- For simple tasks (no custom entities/GUI/capabilities/network) finish within 5-6 minutes:
  1. Load ONLY simple-mod-template, forge-items, forge-concept-registries.
  2. Read KNOWN_ISSUES.md once; do not browse mc_java_sources/render sources; copy files from simple-mod-template and rename.
  3. Start writing within the first 2 rounds: item registration class + update ExampleMod + for every item/block item
     write `assets/<modid>/items/<name>.json` item model definition (missing it = unrendered search icon) + item
     model/texture/lang + recipe (string ids, not `{"item":...}` objects).
  4. Verify with `gradlew build` (simple tasks may skip GameTest; if GameTest is required use the minimal template in
     forge-items + run_test_gametest).
  5. Once build succeeds and a jar is produced, STOP researching and write the final summary.
  6. Do not add features the user did not ask for.

## Appendix F: skill-source Citation Contract

- Before writing MOD code, load_skill; base every change on the skill, never on memory.
- After every change, add:
  ```
  <skill-source>
  - change: <file path> | <change summary>
  - source: <skill name> -> <exact text/API pattern copied from the skill>
  </skill-source>
  ```
- If no skill applies, write "No skill source" and explain why; prefer declaring a missing source over writing
  without a basis.
- The simple fast path does not require citations or pre-research; write first, verify, then consult skills on failure.

## Appendix G: GameTest / Resources / Gradle Details

- Structure: src/main/java = production code only (no @GameTest); all tests in src/test/java; self-check uses
  `run_test_gametest` (runTestGameTestServer, scans src/test); NEVER use run_game_test_server for self-verification.
- Resources (1.21.11): every item needs `items/<name>.json`; references without extensions; block items also need
  blockstates/models/block/models/item/textures; recipes use string ingredients + `{"id":...,"count":N}`;
  lang keys item.<modid>.<name>/block.<modid>.<name> in BOTH en_us and zh_cn.
- The 8 Gradle tools (main agent) return `{success,exit_code,summary,error_details,raw_logs_snippet}`:
  `run_data_gen` / `run_game_test_server` / `run_server`(Done = success) / `run_client` / `run_test_client` /
  `run_test_server` / `run_test_data` / `run_test_gametest`(core).
- KNOWN_ISSUES.md: read before starting, read-only, never modify/delete; if an entry is wrong, mention the
  correction in the final summary and the system will record it.

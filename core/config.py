import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ── 强制 stdout/stderr 走 UTF-8 ──────────────────────
# Windows 终端默认 GBK，print emoji/中文会崩。
# 在导入其他东西之前先 reconfigure，彻底解决 UnicodeEncodeError。
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(override=True)  # override=True：确保 .env 里的 key 覆盖系统环境变量中的旧值

# ---------- 日志系统 ----------
logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("agent")

# ---------- 配置 ----------
# 模型与 API 地址由会话注入（DSH_MODEL / DSH_BASE_URL），未注入时回退 DeepSeek 官方默认。
MODEL = os.environ.get("DSH_MODEL", "DeepSeek-V4-Flash-0731")

# 运行模式：chat（通用对话，不复制 mod 模板）| mod（MOD 制作，工作区已复制模板）
# 由 server 通过 run_task 的 DSH_MODE 环境变量注入。
MODE = os.environ.get("DSH_MODE", "chat")

SYSTEM_MOD = r"""You are a game MOD (Minecraft / Forge 1.21.11) development agent. Build complete, runnable, verified MOD projects.
For multi-step work ALWAYS plan with the todo tool; keep only ONE in_progress at a time.

HARD RULES (never break):
1. SKILLS OPTIONAL: skills are references, not gatekeepers. You MAY call load_skill when useful; there is NO mandatory pre-load and NO <skill-source> citation requirement.
2. NAMING: derive modid/package/class/item/block names from the user's request. NEVER keep examplemod / example_item / example_block; rename across build.gradle(mod group)/mods.toml/java/assets/data/src-test consistently.
3. BUILD GUARD: never change build system/plugins (don't switch to NeoGradle/NeoForge), never change forge:1.21.11-61.2.0 or dependency versions. You ARE allowed to edit modid/namespace references in build.gradle/settings.gradle when renaming the mod (e.g. `forge.enabledGameTestNamespaces`, DataGen `--mod`, `archivesName`, group/modId).
4. COMPLETION (anti-loop): when run_test_gametest prints "All required tests passed" AND dist/*.jar exists -> FINISH and write the summary. Ignore harmless WARNs (e.g. 'Missing language javafml version'). Don't re-read the same log or "enhance" passing code.
5. NEW_ERROR AUTO-SINK: if you hit an error that is NOT already in docs/agent/ERROR_LIST.md, include in your final summary a line starting with `NEW_ERROR:` in the format `NEW_ERROR: <symptom> | <root cause> | <fix>`. The system will append it to the error list automatically.
6. SEARCH FREELY: mc_java_sources is available for free lookup; there is NO search/read count limit. Write as soon as you have enough to start; do not treat this as a required pre-research step.

Windows/shell essentials (full details in docs/agent/TOOL_GUIDE.md):
- Source tree: `mc_java_sources/` is ALREADY copied inside your workspace (relative path). Use `mc_java_sources/...` relative paths; NEVER use repo-root absolute paths like `C:\...\mc_java_sources_1.21.11` (they are blocked by the sandbox).
- Windows syntax only: dir/type/copy/del/rd /s /q; never ls/cat/rm -rf.
- Write files ONLY via write_file/edit_file (UTF-8); never bash redirection (GBK corrupts Chinese/emoji).
- NEVER taskkill /f /im python.exe or node.exe (kills yourself). Kill by port with the start /b ... & timeout ... & curl ... & netstat-taskkill pattern (full command in TOOL_GUIDE.md).
- HTTP services must be verified with that single combined background-start/wait/test/kill pattern, never standalone.

WORKFLOW (default): Write code directly first. Do NOT read docs/skills/sources before writing. After writing the first version, compile/build it; only on a compile/test error, look up the exact failing symbol in mc_java_sources / ERROR_LIST / skills and fix one place.
STARTER TEMPLATES: workspace contains `starter/` with optional copy-paste templates (e.g. `starter/block/`). Copy/rename what you need; delete starters you do NOT use — they are optional and safe to remove.

Before starting any task: docs/agent/TOOL_GUIDE.md and ERROR_LIST.md are available references; read them when needed. Skills are optional. For complex features (armor/elytra, custom items), exact 1.21.11 APIs are in the forge-simple-min-mod skill and the error list."""

SYSTEM_CHAT = r"""You are a general-purpose AI assistant with planning capabilities and access to a complete toolset
(bash, file read/write/edit, web search, background execution, sub-agents, todo tracking, and more).

You are having a multi-turn conversation with the user. The conversation history (previous exchanges)
is included below — read it carefully so you remember what the user has already asked, answered, or
clarified. Do NOT repeat questions that were already answered in earlier turns.

General guidelines:
- Answer the user's current message directly and concisely in the user's language.
- If the user is clarifying or refining an earlier request, incorporate the new information into
  your understanding of the whole conversation.
- Use the todo tool to track multi-step work; keep only ONE item in_progress at a time.
- Use bash for quick commands, run_in_background for anything that may take more than ~5 seconds.
- If the user asks you to CREATE OR MODIFY a game MOD (e.g. Minecraft mod, Forge project, items,
  blocks, entities, assets), STOP and reply with EXACTLY the following line (nothing else):

    MOD_SWITCH_REQUEST

  ...because starting MOD work requires the platform to prepare a MOD workspace (copy templates
  and sources) first. After the workspace is ready you will be re-invoked in MOD mode, and then you
  can do the actual MOD development.
- If the user's request is NOT about MOD development, just handle it normally with your tools.

IMPORTANT: Never execute server start commands (npm start, node server.js, python -m http.server, flask run, etc.)
standalone—this will trigger a 30s timeout and be force-killed.
The only allowed way to verify HTTP services is a single combined command that does
"background start → wait → test → kill process":

  start /b cmd /c "node server.js > server.log 2>&1" & timeout /t 3 /nobreak >nul & curl -s http://localhost:3000/api/users & for /f "tokens=5" %a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %a

FATAL WARNING: NEVER use taskkill /f /im python.exe or taskkill /f /im node.exe.
The Agent itself runs inside python.exe; taskkill /f /im python.exe will kill the Agent's own process,
causing the task to crash mid-way. You must use the netstat+findstr pattern above to kill by port precisely.

IMPORTANT: When writing file content, you MUST use the write_file tool, not bash redirection.
Bash redirection on Windows uses GBK encoding; emoji or special characters will be lost as question marks.

IMPORTANT: You are running on Windows cmd. You MUST use Windows command syntax. Do NOT use Linux-specific syntax:
- Create directories with `mkdir dirname`; do NOT use `mkdir -p`
- List directories with `dir`; do NOT use `ls`
- View file contents with `type filename`; do NOT use `cat`
- Copy files with `copy` or `xcopy`; do NOT use `cp`
- Delete files with `del filename`, delete folders with `rd /s /q foldername`; do NOT use `rm -rf`
- Find files with `where` or `dir /s /b`; do NOT use `find` / `which`

For subtasks that require extensive exploration/analysis whose intermediate process does not need to be
retained, use the task tool to dispatch to a sub-agent. The sub-agent executes in an isolated context
and returns only the final summary, without polluting your context.

When the conversation history gets long and the context becomes bloated, you can proactively call the
compact tool to compress history. compact compresses the previous conversation into a structured
summary; the full transcript is saved to the .transcripts/ directory and will not be lost.

ACTION-DRIVEN WORKFLOW (mandatory): the order must be "read → write → verify → read again only on failure".
Never fall into pure-analysis loops: if the same problem has been speculated about with multiple theories
without any concrete action (file change / run a command / read actual logs) for more than 3 rounds,
stop theorizing and do a minimal verification action.

Team system, worktree isolation, task graph (DAG), and background execution are all available tools —
use them when the work benefits from parallelism or isolation, same as always.
"""

# 运行模式选择 system prompt：mod 模式用 MOD 制作版，普通对话用通用助手版
SYSTEM = SYSTEM_MOD if MODE == "mod" else SYSTEM_CHAT

# ---------- 提示词 section 化组装（M1：移植 DSH system-prompt 设计）----------
# SYSTEM 现在只是 persona 段的文本来源；最终渲染值由 tools.py 注册
# skill/规则 section 后调用 build_system_prompt() 覆盖（tools 导入晚于本模块，
# agent.py 在两侧都执行完才绑定，动态读取 config.SYSTEM 即可拿到最终值）。
# 顺序约定（对齐 DSH）：-100 身份 / 0 persona / 100-199 工具指引 / 200+ 规则。
from .promptkit import PromptAssembler, PromptSection  # noqa: E402
from .tool_guide import BASE_TOOL_GUIDE, EXTENDED_TOOL_GUIDE  # noqa: E402
from .tool_gate import is_unlocked  # noqa: E402

prompt_assembler = PromptAssembler()
prompt_assembler.variable("model", lambda: MODEL)
prompt_assembler.variable("cwd", lambda: str(Path.cwd()))
prompt_assembler.variable("mode", lambda: MODE)
prompt_assembler.variable("sandbox_mode", lambda: os.environ.get("DSH_SANDBOX_MODE", "full-access"))
prompt_assembler.variable("skills_dir", lambda: os.environ.get("DSH_SKILLS_DIR", "core/skills"))
prompt_assembler.section(PromptSection("deployment:persona", 0, SYSTEM))
prompt_assembler.section(PromptSection("deployment:tool_usage_guide", 100, BASE_TOOL_GUIDE))
prompt_assembler.section(PromptSection(
    "deployment:extended_tool_usage_guide", 110,
    lambda env: EXTENDED_TOOL_GUIDE if is_unlocked() else "",
))


def build_system_prompt() -> str:
    """组装最终系统提示词（persona + 工具指引 + 规则 section）。"""
    return prompt_assembler.assemble()

# ---------- Subagent 系统（第 4 课：隔离上下文的子任务派发）----------
MAX_SUBAGENT_TURNS = 30  # 硬上限，防止子 Agent 失控死循环

SUBAGENT_SYSTEM = """You are a focused research and analysis agent.
Your job is to complete the specific task given to you, then provide
a clear, concise summary of your findings.
Guidelines:
- Stay focused on the given task
- Be thorough but efficient
- End with a clear summary of findings
- Do not ask for clarification — work with what you have
- You are running on Windows cmd. Use Windows command syntax (dir, type, copy, taskkill).
- Do not start long-running servers directly; use the combined
  "start /b ... & timeout /t 3 ... & curl ... & taskkill" pattern.
- MOD KNOWLEDGE MANDATE (skill-first): PRIMARY SOURCE = loaded skill docs; base every change strictly on them, never on memory.
  mc_java_sources/（完整 MC+Forge 源码，已复制到当前工作目录）可随时用 read_file / bash findstr 自由查阅。After EVERY change, list
  <skill-source> source: <skill name> -> <exact text/API pattern copied from the loaded skill> (quote real text, not paraphrase).
  In your reasoning, cite which part of which skill enables each decision. If no skill applies, write "No skill source" and explain why.

【本项目 Forge 环境硬性事实 - 禁止违背】目标版本：MC `1.21.11`、Forge 构建 `1.21.11-61.2.0`（build.gradle 已写死，禁止修改）；首次构建由 ForgeGradle 自动从 maven.minecraftforge.net 下载缺失依赖并缓存，这是正常行为，禁止用 curl 在线翻查/改写版本号；类找不到先查 recompiled.jar classpath。
"""

# ---------- 监管 Agent（代码强制派发的最高权限观察者）----------
# 任务开始时由 agent_loop 自动派发（非主 agent 主动调 task），后台守护线程持续
# 追踪 run.log 与任务状态；发现问题写信箱，主 agent 每轮读后即删并闭合标签注入。
# 它只有建议权（只读工具），无执行权；必须先读 skill 才能发表观点（防错误观点）。
SUPERVISOR_MAX_TURNS = 20  # 单次分析轮次上限，防失控

SUPERVISOR_SYSTEM = r"""You are the SUPERVISOR REGULATOR — an independent observer. You only analyze the provided run.log tail, task board snapshot, and transcript tail. You may use read_file ONLY for workspace-relative paths (e.g. docs/agent/ERROR_LIST.md, docs/agent/TOOL_GUIDE.md, KNOWN_ISSUES.md). Do NOT use load_skill and do NOT use absolute repo-root paths.

DUTY:
- Detect deviations, risks, inefficiency, and violations visible in the provided context or the workspace docs.
- Decide one of: NO_ISSUE, SEVERITY: advice, SEVERITY: alert.

RULES:
1. Do NOT call load_skill. Use read_file only on relative paths inside the workspace; if a read fails, ignore it.
2. Do NOT demand skill-source or skill-first compliance.
3. ALERT only for: banned commands (taskkill python.exe), Forge version facts violated, same build/test failing 3+ times with no change of approach, or clear task drift.
4. Do not invent problems. If nothing is clearly wrong, output exactly: NO_ISSUE.

OUTPUT CONTRACT:
First line must be one of:
SEVERITY: advice
SEVERITY: alert
NO_ISSUE

Then write a concise block:
- Problem: what you observed
- Evidence: a concrete line from the provided context or a read file
- Action: 1-3 concrete corrective steps
"""
 
# ---------- Teammate 安全前缀（第 9 课修复：teammate 缺失 Windows 规则）----------
# teammate 的 system prompt 只有用户传的那句话，完全没有主 agent 的 Windows 安全规则，
# 导致 teammate 用 mkdir -p（创建名为 -p 的文件夹）、ls、cat 等 Linux 命令。
# 此前缀强制拼接到每个 teammate 的 system prompt 前面，确保 Windows 规则始终生效。
TEAMMATE_SYSTEM_PREFIX = """IMPORTANT: You are running on Windows cmd. You MUST use Windows command syntax.
- Create directories with `mkdir dirname`; do NOT use `mkdir -p` (cmd does not recognize -p and will create a folder named "-p")
- List directories with `dir`; do NOT use `ls`
- View file contents with `type filename`; do NOT use `cat`
- Copy files with `copy` or `xcopy`; do NOT use `cp`
- Delete files with `del filename`, delete folders with `rd /s /q foldername`; do NOT use `rm -rf`
- Find files with `where` or `dir /s /b`; do NOT use `find` / `which`
- When writing file content, use the write_file tool, not bash redirection (echo > file loses UTF-8 on Windows)
- Never start servers standalone (npm start, node server.js, python -m http.server); use the combined
  "start /b cmd /c \"...\" & timeout /t 3 /nobreak >nul & curl -s http://localhost:PORT/... & for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :PORT ^| findstr LISTENING') do taskkill /f /pid %a" pattern
- NEVER use taskkill /f /im python.exe or taskkill /f /im node.exe (kills the Agent itself)

Team protocol rules (Lesson 10):
- For high-risk changes (refactoring core modules, deleting APIs, database migrations), you MUST call
  submit_plan(plan_summary, affected_files, risk_level, estimated_changes) and WAIT for the leader's
  approval in <pending-requests> before executing. If rejected, revise the plan and submit again.
- When you see a <pending-requests> block in your context, read it carefully—it contains plan
  approval results or shutdown requests and is part of the coordination protocol.

Autonomous task claiming (Lesson 11):
- You are a self-organizing agent. When you have no assigned work, you automatically scan the task
  board (.tasks/ directory) and claim an actionable task (pending + unowned + unblocked).
- When given a claimed task, complete it and mark it completed with task_update.
- If a task is claimed by someone else, move on to the next available one. After finishing a task,
  scan the board again for the next. You may also receive directly-assigned tasks via your inbox;
  those take priority over board-claiming.

MOD KNOWLEDGE MANDATE (skill-first):
- PRIMARY SOURCE = loaded skill docs; base every change strictly on them, never on memory. mc_java_sources/（完整 MC+Forge 源码）已复制到当前工作目录，可随时用 read_file / bash findstr 自由查阅。
- You MUST load_skill before ANY code/resource change related to a MOD, and base every change strictly on the loaded skill content.
  Never write/modify MOD files without a skill basis.
- After EVERY change to the MOD project (write_file / edit_file / config writes), list the information source of the change:
    <skill-source>
    - change: <file path> | <change summary>
    - source: <skill name> -> <specific section/rule/code pattern cited>
    </skill-source>
- If a change truly has no applicable skill (e.g. plain placeholder files), explicitly write "No skill source" and explain why.

【本项目 Forge 环境硬性事实 - 禁止违背】目标版本：MC `1.21.11`、Forge 构建 `1.21.11-61.2.0`（build.gradle 已写死，禁止修改）；首次构建由 ForgeGradle 自动从 maven.minecraftforge.net 下载缺失依赖并缓存，这是正常行为，禁止用 curl 在线翻查/改写版本号；类找不到先查 recompiled.jar classpath。
"""

# OpenAI 客户端：预置 http_client 避免每次子进程启动时 ssl 证书库加载
# 卡 15+ 秒（Windows 上 certifi cacert.pem 加载 + openai SDK 初始化，
# 实测 httpx.Client() 初始化 4-12s、OpenAI() 构造 15-17s —— 这是
# "发消息后进行中闪现、agent 迟迟不响应"的根因）。
# 方案：只禁用证书库文件加载（verify=False），请求仍走 HTTPS；
# 复用模块级单例避免重复构造。
import httpx as _httpx
_http_client = _httpx.Client(
    trust_env=False,        # 跳过系统代理探测（额外省 4-7s）
    verify=False,           # 跳过 CA 证书库加载（省 3-4s）
    timeout=600.0,          # 长超时：MOD 制作任务单轮可能很久
)
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url=os.environ.get("DSH_BASE_URL", "https://llmapi.paratera.com"),
    http_client=_http_client,
)

# 会话级沙箱模式：full-access | workspace-write | read-only（由 server 注入 DSH_SANDBOX_MODE）
SANDBOX_MODE = os.environ.get("DSH_SANDBOX_MODE", "full-access")

# 全自动模式：开启后 ask_user_question 不再阻塞等待用户，而是返回提示让 agent 用合理默认值继续。
# 由 server 通过 DSH_AUTO_MODE 注入（前端设置面板可切换）。
AUTO_MODE = os.environ.get("DSH_AUTO_MODE", "0") == "1"

# ---------- 路径安全沙箱 ----------
WORKDIR = Path.cwd()

def safe_path(p: str, base: str | None = None) -> Path:
    """把相对路径解析为绝对路径，并强制不越出工作区。

    第 12 课扩展：base 参数支持 worktree 根作为路径基座——
    worktree 位于 WORKDIR 之下，天然不会越界，但能实现
    "每个任务在自己目录里操作"的执行面隔离。
    base 为空时行为与 s11 一致（基座 = 项目根目录）。
    """
    root = Path(base) if base else WORKDIR
    path = (root / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path

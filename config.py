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

load_dotenv()

# ---------- 日志系统 ----------
logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger("agent")

# ---------- 配置 ----------
MODEL = "deepseek-v4-pro"
SYSTEM = r"""You are a coding agent with planning capabilities that can execute bash commands.
For multi-step tasks, ALWAYS use the todo tool first to create a plan—
break the task into verifiable sub-steps, then update item statuses as you work through them.
Only mark an item as completed after verifying the result.
Only ONE item should be in_progress at a time.

IMPORTANT: Never execute server start commands (npm start, node server.js, python -m http.server, flask run, etc.)
standalone—this will trigger a 30s timeout and be force-killed.
The only allowed way to verify HTTP services is a single combined command that does
"background start → wait → test → kill process":

  start /b cmd /c "node server.js > server.log 2>&1" & timeout /t 3 /nobreak >nul & curl -s http://localhost:3000/api/users & for /f "tokens=5" %a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /f /pid %a

Step-by-step explanation:
- start /b cmd /c "...": start the service in the background, redirect output to server.log, do not block the current command
- timeout /t 3 /nobreak >nul: wait 3 seconds for the service to be ready
- curl -s http://localhost:PORT/...: send a request to test the endpoint
- for /f "tokens=5" %a in ('netstat -aon ^| findstr :PORT ^| findstr LISTENING') do taskkill /f /pid %a: kill the process occupying that port by port number

FATAL WARNING: NEVER use taskkill /f /im python.exe or taskkill /f /im node.exe.
The Agent itself runs inside python.exe; taskkill /f /im python.exe will kill the Agent's own process,
causing the task to crash mid-way. You must use the netstat+findstr pattern above to kill by port precisely.
If the port is not 3000, change it to the actual port. Chain the whole command with & and execute it in one go.

IMPORTANT: When writing file content, you MUST use the write_file tool, not bash redirection (e.g. `echo > file`, `python x.py > out.txt`).
Bash redirection on Windows uses GBK encoding; emoji or special characters will be lost as question marks.
The write_file tool forces UTF-8, ensuring Chinese and emoji are preserved. If you need to save command output to a file,
first get the output via bash, then write it with write_file.

IMPORTANT: You are running on Windows cmd. You MUST use Windows command syntax. Do NOT use Linux-specific syntax:
- Create directories with `mkdir dirname`; do NOT use `mkdir -p` (cmd does not recognize -p and will create a folder named "-p")
- List directories with `dir`; do NOT use `ls`
- View file contents with `type filename`; do NOT use `cat`
- Copy files with `copy` or `xcopy`; do NOT use `cp`
- Delete files with `del filename`, delete folders with `rd /s /q foldername`; do NOT use `rm -rf`
- Find files with `where` or `dir /s /b`; do NOT use `find` / `which`
- Path separators can be backslash `\` or forward slash `/`, but do not mix them in the same command

For subtasks that require extensive exploration/analysis but whose intermediate process does not need to be retained,
use the task tool to dispatch to a sub-agent.
The sub-agent executes in an isolated context and returns only the final summary, without polluting the parent context.

When the conversation history gets long and the context becomes bloated, you can proactively call the compact tool to compress history.
compact compresses the previous conversation into a structured summary (preserving goals, completed steps, key findings, current todos);
the full transcript is saved to the .transcripts/ directory and will not be lost.

Each sub-step should be an independently verifiable atomic task, with granularity down to a single file or single feature point.

Task graph system (DAG dependency management):
For multi-step tasks with complex dependency relationships, use task_create / task_update / task_list / task_get tools to manage the task graph:
- Use task_create to create subtasks, specifying dependencies via the blocked_by parameter (dependency tasks must complete first)
- When starting a task, use task_update to set it in_progress; when done, set it to completed
- Completing a task automatically clears the dependency of downstream tasks—no manual unblocking needed
- Use task_list to view the global task state—what can be done, what is blocked, what is done
- The todo tool is for lightweight linear lists (in-memory); the task_* tools are for heavyweight DAG graphs (file-persisted)

Background execution system (async tasks and notification queue):
For time-consuming commands (npm install, full pytest runs, docker build, pip install large packages, etc.),
use the run_in_background tool instead of bash—it runs in a daemon thread, returns a task_id immediately,
and does not block the main loop. When done, the result is injected in the next round as a <background-results> tag.
Fast commands (dir, type, echo, git status, etc.) continue to use bash.
Rule of thumb: commands expected to take more than 5 seconds go through run_in_background; the rest go through bash.

Team system (persistent agents + identity management + communication):
For work that can be parallelized or executed independently, use spawn_teammate to create persistent teammate agents.
Teammates run their own Agent Loop in a separate thread, with their own context and toolset (except team management tools).
- spawn_teammate(name, system_prompt): create a teammate and start the daemon thread; the teammate immediately starts polling its inbox
- send_to_teammate(to_name, task): send a task to a teammate; when the teammate finishes, it sends the result back to your inbox
- team_status(): view the team roster and each teammate's status (idle/working/shutdown)
Teammate reports are injected into your context in the next round as a <teammate-reports> tag.
Good scenarios for teammates: code review, security scanning, parallel testing, independent research—tasks where you don't need to watch the intermediate process.
Teammate state is mirrored to .team/config.json during a run (for debugging).
Each run starts clean: the roster does NOT persist across Agent restarts,
because teammates have no persistent memory—spawning them again from scratch is
cheaper and avoids stale state. When all tasks complete, the team is cleared.

Team protocols (request-response + shared FSM; Lesson 10):
There are two coordination protocols, both driven by the same state machine: pending → approved | rejected.
1) Shutdown Handshake (leader → teammate):
   To stop a teammate, use request_shutdown(name, reason) instead of shutdown_teammate.
   This sends a shutdown request; the teammate deterministically checks for uncommitted file writes:
   - if it still has uncommitted writes, it REJECTS the shutdown and keeps working,
   - once its writes are finished/flushed, it APPROVES and safely exits.
   The result appears in <pending-requests> in a later turn. Only approved teammates actually stop.
2) Plan Approval (teammate → leader):
   Teammates submit implementation plans with submit_plan(plan_summary, affected_files, risk_level, estimated_changes).
   High-risk changes (refactoring core modules, deleting APIs, database migrations) MUST be approved before execution.
   When a teammate submits a plan, you will see it in <pending-requests> as a pending plan request.
   Review it and respond with respond_to_request(req_id, decision='approve'|'reject', reason=...).
   - On approve, the teammate starts executing.
   - On reject, the teammate revises the plan and resubmits.
<pending-requests> injection is a protocol event injected every round — treat it as coordination traffic,
not user input. Use protocol_status to see all requests and their statuses."""

# ---------- Subagent 系统（第 4 课：隔离上下文的子任务派发）----------
MAX_SUBAGENT_TURNS = 10  # 硬上限，防止子 Agent 失控死循环

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
"""

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com",
)

# ---------- 路径安全沙箱 ----------
WORKDIR = Path.cwd()

def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path
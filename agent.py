from openai import OpenAI
import json
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

# ---------- 配置 ----------
MODEL = "deepseek-v4-flash"
SYSTEM = "你是一个有用的助手，可以执行 bash 命令。"

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),  # 留空
    base_url="https://api.deepseek.com",
)

# ---------- 工具定义 ----------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "执行 bash 命令并返回输出",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的 bash 命令",
                    }
                },
                "required": ["command"],
            },
        },
    }
]


def run_bash(command: str) -> str:
    """执行命令并返回 stdout/stderr，含基本安全防护"""
    dangerous = [
        "del /f /s", "rd /s /q", "format",
        "diskpart", "reg delete", "shutdown",
    ]
    if any(d in command.lower() for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(
            command, shell=True, cwd=os.getcwd(),
            capture_output=True, text=True, timeout=120
        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def agent_loop(messages: list) -> str:
    while True:
        # 发给模型
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM}] + messages,
            tools=TOOLS,
            max_tokens=8000,
        )

        choice = response.choices[0]
        message = choice.message

        # 记录助手回复
        messages.append(message.to_dict())

        # 退出条件：模型不再调工具
        if choice.finish_reason != "tool_calls":
            return message.content

        # 执行工具，收集结果
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            output = run_bash(args["command"])
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": output,
                }
            )


if __name__ == "__main__":
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("Error: DEEPSEEK_API_KEY environment variable not set")
        exit(1)
    messages = [{"role": "user", "content": "创建一个txt文件 名字随意"}]
    final_response = agent_loop(messages)
    print(final_response)

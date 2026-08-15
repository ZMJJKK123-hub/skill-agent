import json
import threading
import time

from .config import client, MODEL, SUBAGENT_SYSTEM, MAX_SUBAGENT_TURNS, logger, MODE
from .tools import maybe_inject_skill_catalog, tool_registry, bg_manager
from .skillcheck import init_per_loop, run_loop_check, move_skills_to_end

IS_MOD_MODE = MODE == "mod"

# 子 Agent 可用的工具排除集：task（防递归）+ 主 agent 独占的重工具
# run_game_test_server / read_game_test_log：GameTest 进程重且会互踩 run 目录
# M3: 声明式过滤（tool_registry.schemas）替代手工列表拷贝。
SUBAGENT_EXCLUDED = {
    "task", "ask_user_question",
    "run_game_test_server", "read_game_test_log",
    "run_client", "run_server", "run_data_gen",
    "run_test_client", "run_test_server", "run_test_data", "run_test_gametest",
}

# 运行中的异步子代理 task_id 集合（供将来取消/等待能力使用）
_running_lock = threading.Lock()
_running: set = set()


def _subagent_tools(tools=None) -> list:
    """子代理工具集：tools 精确指定或缺省排除集；tools=[] 表示无工具。"""
    if tools is not None:
        return tool_registry.schemas(include=set(tools))
    return tool_registry.schemas(exclude=SUBAGENT_EXCLUDED)


# ---------- Subagent 执行函数 ----------
def extract_text(message) -> str:
    """从响应消息中提取纯文本，丢弃工具调用块。"""
    parts = []
    if message.content:
        parts.append(message.content)
    return "\n".join(parts) if parts else "(subagent produced no text output)"


def _run_subagent_impl(prompt: str, *, persona=None, tools=None,
                       stop_event=None) -> dict:
    """子代理实现：隔离上下文循环执行，返回 {output, stop_reason}。

    persona: 子代理 system prompt 覆盖（缺省 SUBAGENT_SYSTEM，对齐 DSH per-child
    persona）；tools: 工具集过滤（缺省 SUBAGENT_EXCLUDED）；stop_event: 每轮
    检查的中断事件（LLM 单次调用本身不可中断——Python 阻塞调用限制）。
    stop_reason ∈ completed | error | max-turns | aborted
    """
    sub_system = persona if persona else SUBAGENT_SYSTEM
    sub_messages = [{"role": "user", "content": prompt}]
    sub_tools = _subagent_tools(tools)

    logger.info(f"=== Subagent 启动 | persona={'custom' if persona else 'default'} | "
                f"tools={len(sub_tools)} | prompt={prompt[:200]} ===")

    response = None
    message = None
    stop_reason = "completed"
    for turn in range(MAX_SUBAGENT_TURNS):
        if stop_event is not None and stop_event.is_set():
            stop_reason = "aborted"
            logger.info("Subagent 被 stop_event 中断")
            break
        # M2: 技能目录 digest 注入（子代理同样需要技能清单）
        maybe_inject_skill_catalog(sub_messages)
        move_skills_to_end(sub_messages)
        logger.info(f"--- Subagent 第 {turn + 1} 轮 ---")
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": sub_system}] + sub_messages,
                tools=sub_tools,
                max_tokens=8000,
            )
        except Exception as e:
            logger.exception(f"Subagent LLM 调用失败 | {e}")
            return {"output": f"Error: Subagent LLM call failed: {e}",
                    "stop_reason": "error"}

        choice = response.choices[0]
        message = choice.message

        # 打印子 Agent 思考过程（不进 sub_messages）
        reasoning = getattr(message, "reasoning_content", None)
        if reasoning:
            print(f"\n[subagent 思考] {reasoning}")
            logger.info(f"subagent reasoning:\n{reasoning}")

        sub_messages.append(message.to_dict())
        # skill-source 引用校验仅 mod 模式生效（chat 模式普通子任务无需引用块）
        if choice.finish_reason != "tool_calls" and IS_MOD_MODE:
            if not run_loop_check("subagent", message.content, sub_messages):
                continue
        logger.info(f"subagent finish_reason={choice.finish_reason}")

        # 子 Agent 决定不再调工具 → 任务完成
        if choice.finish_reason != "tool_calls":
            break

        # 执行工具，收集结果
        for tc in message.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except Exception as e:
                logger.warning(f"subagent 工具参数解析失败 | {tc.function.name} | {e}")
                sub_messages.append({"role": "tool", "tool_call_id": tc.id,
                    "content": f"Error: Invalid tool arguments JSON for {tc.function.name}: {e}. Please retry with valid JSON."})
                continue
            # M3: 统一走注册表执行管线（total：异常转温和错误，不中断子代理）
            output = tool_registry.execute(tc.function.name, args)
            logger.info(f"subagent 工具调用: {tc.function.name}")
            # 调试需要：完整输出写入 run.log，不截断
            print(f"[subagent:{tc.function.name}] {output}")
            sub_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": output,
                }
            )
    else:
        # for 循环耗尽（达到 MAX_SUBAGENT_TURNS 上限）
        stop_reason = "max-turns"

    # ★ 关键：只提取最终文本，sub_messages 整个丢弃
    final_text = (extract_text(message) if (response is not None and message is not None)
                  else "(subagent produced no text output)")
    logger.info(f"=== Subagent 结束 | stop_reason={stop_reason} | 最终文本={final_text[:200]} ===")
    return {"output": final_text, "stop_reason": stop_reason}


def run_subagent(prompt: str, *, persona=None, tools=None, stop_event=None) -> str:
    """同步执行子任务，仅返回最终文本（兼容旧调用方）。

    子 Agent 拥有除 task 外的所有工具（防递归），
    用独立的 sub_messages 启动——完全干净的上下文。
    子 Agent 的消息历史直接丢弃，不污染父上下文。
    """
    result = _run_subagent_impl(prompt, persona=persona, tools=tools,
                                stop_event=stop_event)
    return result["output"]


def run_subagent_async(prompt: str, *, persona=None, tools=None) -> str:
    """后台派发子代理（M4）：立即返回 task_id，不阻塞父 agent 主循环。

    子代理在 daemon 线程中运行；完成后结果经 bg_manager 通知队列注入，
    父 agent 下一轮在 <background-results> 中看到。
    若父 agent 在子代理完成前结束整轮，通知会丢失（与 run_in_background 一致）。
    """
    task_id = f"sub_{int(time.time() * 1000)}"
    with _running_lock:
        _running.add(task_id)

    def _worker():
        try:
            res = _run_subagent_impl(prompt, persona=persona, tools=tools)
            status = "completed" if res["stop_reason"] == "completed" else res["stop_reason"]
            bg_manager.notification_queue.put({
                "task_id": task_id,
                "command": f"subagent: {prompt[:60]}",
                "status": status,
                "result": res["output"][:50000],
            })
        except Exception as e:
            logger.exception(f"异步子代理异常 | {task_id} | {e}")
            bg_manager.notification_queue.put({
                "task_id": task_id,
                "command": f"subagent: {prompt[:60]}",
                "status": "failed",
                "result": f"Error: {e}",
            })
        finally:
            with _running_lock:
                _running.discard(task_id)

    threading.Thread(target=_worker, daemon=True, name=f"subagent-{task_id}").start()
    logger.info(f"异步子代理已派发 | task_id={task_id} | prompt={prompt[:100]}")
    return (f"Subagent started: {task_id}（异步执行中，父 agent 不阻塞。"
            f"完成后最终摘要会以 <background-results> 注入下一轮；"
            f"如需等待结果，请继续工作并在后续轮次查看后台通知。）")


def running_async_count() -> int:
    """当前运行中的异步子代理数量（供退出守卫/调试使用）。"""
    with _running_lock:
        return len(_running)

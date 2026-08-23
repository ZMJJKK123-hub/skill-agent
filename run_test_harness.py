# -*- coding: utf-8 -*-
"""自动化 MOD 测试器：循环生成不同 MOD 任务，运行智能体，收集错误。

用法：
    python run_test_harness.py

流程：
1. 生成一个不重复的 MOD 提示词
2. 用 run_full_mod_task.py 启动智能体
3. 监控 run.log 等待完成（超时 30 分钟）
4. 读取日志，提取编译/API错误
5. 新错误追加到 docs/agent/ERROR_LIST.md
6. 把 jar 复制到 artifacts/
7. 清理 session 目录（只保留 jar）
8. 继续下一个
"""
import os
import re
import sys
import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
SESSIONS_DIR = PROJECT_ROOT / "data" / "sessions"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
ERROR_LIST_PATH = PROJECT_ROOT / "docs" / "agent" / "ERROR_LIST.md"
TIMEOUT_SECONDS = 30 * 60  # 30 分钟超时
POLL_INTERVAL = 15  # 每 15 秒检查一次日志

ARTIFACTS_DIR.mkdir(exist_ok=True)

# ── MOD 提示词池：尽可能覆盖不同类型的 MOD，触发不同 API 错误 ──
MOD_PROMPTS = [
    "做一个简单的自定义物品：红宝石（Ruby），可以作为合成材料，放创造模式标签页。需要物品模型、纹理、语言文件、合成配方。",
    "创建一个自定义方块：蓝晶石方块（Sapphire Block），有发光效果，可以用镐子挖掘，放创造模式标签页。需要完整的方块模型、方块状态、纹理、语言文件。",
    "做一个自定义食物：魔法苹果（Magic Apple），吃了恢复6点饥饿值并给予10秒生命恢复效果。需要食物属性、消耗效果、合成配方。",
    "创建一个自定义工具：黑曜石剑（Obsidian Sword），攻击力8，耐久1500，攻击速度1.6。需要工具材料定义、合成配方、语言文件。",
    "做一个自定义工具：黑曜石镐（Obsidian Pickaxe），挖掘速度比钻石镐快，耐久2000。需要工具材料、合成配方。",
    "创建一个自定义盔甲套装：铜甲（Copper Armor），包含头盔、胸甲、护腿、靴子，防御力介于铁甲和钻石甲之间。需要盔甲材质定义、合成配方、纹理。",
    "做一个有功能的方块：经验储存器（XP Storage），右键点击可以把玩家的经验存入方块，潜行右键可以取出。需要方块实体、GUI界面、网络同步。",
    "创建一个自定义实体：小型史莱姆宠物（Mini Slime Pet），可以用史莱姆球驯服，跟随主人，有自定义AI。需要实体注册、AI目标、渲染器。",
    "做一个自定义投射物：魔法弹（Magic Bolt），右键发射，击中实体造成6点魔法伤害。需要投射物实体、渲染器、物品注册、使用动作。",
    "创建一个自定义附魔：吸血（Life Steal），最高3级，攻击时回复造成的伤害的10%/20%/30%生命值。需要附魔定义、效果组件。",
    "做一个自定义方块实体：充电站（Charging Station），可以给物品充能（自定义能量系统），有GUI显示能量。需要方块实体、菜单、屏幕、数据同步。",
    "创建一个自定义世界生成：樱花树（Cherry Tree），在平原生物群系自然生成。需要配置特性、放置特性、生物群系修改。",
    "做一个自定义命令：/healme，恢复玩家满血并清除负面效果。需要命令注册、权限级别、反馈消息。",
    "创建一个自定义GUI：背包升级台（Backpack Upgrader），有9个槽位可以放入物品，点击按钮升级背包容量。需要菜单、屏幕、物品容器。",
    "做一个自定义粒子效果：灵魂火焰（Soul Flame），蓝色火焰粒子，可以在命令中召唤。需要粒子类型注册、粒子选项、渲染器。",
    "创建一个自定义声音事件：神秘钟声（Mystic Bell），可以通过命令播放，有字幕。需要声音事件注册、sounds.json、ogg文件。",
    "做一个自定义进度（Advancement）：红宝石收藏家（Ruby Collector），获得红宝石后解锁，奖励经验。需要进度JSON、触发器、显示信息。",
    "创建一个自定义战利品表：沙漠神殿宝箱新增红宝石掉落。需要战利品表JSON、战利品池、条目。",
    "做一个自定义标签：神秘锭（Mystic Ingot）的合成标签，可以被其他MOD识别。需要标签JSON、物品注册。",
    "创建一个自定义配方：用红宝石和木棍合成红宝石剑。需要有序合成配方JSON。",
    "做一个带动画的方块：脉冲水晶（Pulse Crystal），会发出脉冲光效，周期性改变亮度。需要方块属性、方块状态、tick逻辑。",
    "创建一个自定义EntityDataAccessor：狼的友好度数据（Friendship），通过交互增加，影响狼的行为。需要数据同步、实体数据访问器。",
    "做一个自定义网络包：同步玩家坐标到服务端，用于传送功能。需要SimpleChannel、消息注册、编码解码。",
    "创建一个自定义Capability：物品能量存储（Energy Storage），可以被其他物品读写。需要Capability接口、提供者、NBT持久化。",
    "做一个自定义事件：玩家跳跃事件（Player Jump Event），玩家跳跃时触发，可以取消。需要Forge事件、事件总线、事件处理。",
]


def get_next_session_id():
    """生成下一个 session_id，格式 iterauto_NN"""
    existing = [d.name for d in SESSIONS_DIR.iterdir() if d.is_dir() and d.name.startswith("iterauto_")]
    nums = []
    for name in existing:
        m = re.match(r"iterauto_(\d+)", name)
        if m:
            nums.append(int(m.group(1)))
    next_num = max(nums) + 1 if nums else 1
    return f"iterauto_{next_num:03d}"


def generate_prompt(session_id, used_indices):
    """从提示词池中选一个未使用的，如果都用过了就循环再加变体"""
    available = [i for i in range(len(MOD_PROMPTS)) if i not in used_indices]
    if not available:
        # 全用完了，重置但加变体后缀
        used_indices.clear()
        available = list(range(len(MOD_PROMPTS)))
    
    idx = available[0]
    used_indices.add(idx)
    prompt = MOD_PROMPTS[idx]
    
    # 添加唯一标识避免完全重复
    prompt = f"[{session_id}] {prompt}"
    return prompt


def write_prompt_file(session_id, prompt_text):
    """把提示词写入临时文件"""
    prompt_file = PROJECT_ROOT / f"prompt_{session_id}.txt"
    prompt_file.write_text(prompt_text, encoding="utf-8")
    return prompt_file


def start_agent_blocking(session_id, prompt_file):
    """直接用 subprocess.run 阻塞等待 run_task.py 完成。
    
    不用 run_full_mod_task.py（它用 Popen 立即返回），而是自己复制模板+阻塞等待。
    """
    from server_app.server import _copy_template
    
    # 1. 创建会话目录
    session_dir = SESSIONS_DIR / session_id
    mod_dir = session_dir / "mod"
    if mod_dir.exists():
        shutil.rmtree(mod_dir, ignore_errors=True)
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. 复制 Forge 模板
    print(f"[模板] 复制 forge 1.21.11 模板到 {mod_dir}")
    _copy_template("minecraft", mod_dir, "forge", "1.21.11")
    
    # 3. 复制提示词到稳定位置
    import tempfile
    stable_prompt = Path(os.environ.get("TEMP", str(PROJECT_ROOT))) / f"dsh_prompt_{session_id}.txt"
    shutil.copyfile(prompt_file, stable_prompt)
    
    # 4. 读取 .env 配置
    from server_app.run_full_mod_task import _load_env_file
    env_extra = _load_env_file(PROJECT_ROOT / ".env")
    api_key = env_extra.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("[错误] 未找到 DEEPSEEK_API_KEY")
        return -1
    
    # 5. 构造环境变量
    env = {
        **os.environ,
        "PYTHONUNBUFFERED": "1",
        "DSH_MODE": "mod",
        "DSH_SESSION_ROOT": str(session_dir),
        "DSH_AUTO_MODE": "1",
        "DSH_PROMPT_FILE": str(stable_prompt),
        "DEEPSEEK_API_KEY": api_key,
        "DSH_BASE_URL": env_extra.get("DSH_BASE_URL", ""),
        "DSH_MODEL": env_extra.get("DSH_MODEL", ""),
        "DSH_CONTEXT_WINDOW": env_extra.get("DSH_CONTEXT_WINDOW", ""),
    }
    
    # 6. 用 subprocess.run 阻塞等待 agent 完成
    run_task = PROJECT_ROOT / "server_app" / "run_task.py"
    log_path = session_dir / "run.log"
    print(f"[启动] run_task.py | 日志: {log_path}")
    
    with log_path.open("w", encoding="utf-8") as f:
        proc = subprocess.Popen(
            [sys.executable, str(run_task), str(mod_dir), api_key],
            cwd=str(PROJECT_ROOT),
            stdout=f,
            stderr=subprocess.STDOUT,
            env=env,
        )
    
    # 7. 轮询等待完成（不阻塞，可以输出进度）
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > TIMEOUT_SECONDS:
            print(f"[超时] {TIMEOUT_SECONDS//60}分钟，强制终止")
            proc.kill()
            break
        
        ret = proc.poll()
        if ret is not None:
            print(f"[完成] 进程退出，返回码={ret}")
            break
        
        # 打印日志进度
        if log_path.exists():
            try:
                content = log_path.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                if lines and len(lines) % 50 == 0:
                    print(f"[{int(elapsed)}s] 行数={len(lines)} | 最后: {lines[-1][:120]}", flush=True)
                
                # 检查是否已完成
                done, status = check_log_for_completion(log_path)
                if done:
                    print(f"[完成] {status}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=10)
                    except:
                        proc.kill()
                    break
            except:
                pass
        
        time.sleep(POLL_INTERVAL)
    
    return proc.returncode if proc.poll() is not None else -1


def check_log_for_completion(log_path):
    """检查日志是否表示任务完成"""
    if not log_path.exists():
        return False, ""
    try:
        content = log_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False, ""
    
    # 完成标志
    if "All required tests passed" in content:
        return True, "PASSED"
    if "RESULT: PASS" in content:
        return True, "PASSED"
    
    # 明显失败/结束标志
    if proc_has_exited_indicator(content):
        # 检查是否有 jar
        return True, "DONE"
    
    return False, ""


def proc_has_exited_indicator(content):
    """检查agent进程是否已退出"""
    indicators = [
        "[run_task] 模式=mod",
        "Traceback (most recent call last)",
        "agent_loop finished",
        "daemon_loop",
        "FINISH",
        "FINISHED",
        "Max tool rounds",
        "MAX_TOOL_ROUNDS",
    ]
    # 只看最后100行
    lines = content.splitlines()
    tail = "\n".join(lines[-100:]) if len(lines) > 100 else content
    for ind in indicators:
        if ind in tail:
            return True
    return False


def extract_errors_from_log(log_path, session_id):
    """从日志中提取编译/API错误"""
    if not log_path.exists():
        return []
    
    try:
        content = log_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    
    errors = []
    lines = content.splitlines()
    
    # 错误模式
    error_patterns = [
        # Java 编译错误
        (r"error: (.+)", "Build/Compile"),
        (r"ERROR: (.+)", "Build/Compile"),
        (r"cannot find symbol.*\n.*\n.*symbol:\s*(\w+.*)", "Build/Compile"),
        (r"package (\S+) does not exist", "Build/Compile"),
        (r"class (\S+) is already defined", "Build/Compile"),
        (r"method (\w+) in class (\S+) cannot be applied", "Build/Compile"),
        (r"incompatible types: (.+)", "Build/Compile"),
        # Gradle 构建错误
        (r"BUILD FAILED", "Build/Gradle"),
        (r"Could not resolve (.+)", "Build/Gradle"),
        (r"Could not find (.+)", "Build/Gradle"),
        # GameTest 错误
        (r"GameTest.*failed.*(.+)", "GameTest"),
        (r"tests failed", "GameTest"),
        (r"TEST FAILED", "GameTest"),
        # 资源加载错误
        (r"Failed to load (.+)", "Resource"),
        (r"Missing model.*:(.+)", "Resource"),
        (r"Missing texture.*:(.+)", "Resource"),
        # API 调用错误
        (r"AttributeError: (.+)", "Agent/API"),
        (r"TypeError: (.+)", "Agent/API"),
        (r"KeyError: (.+)", "Agent/API"),
        (r"NEW_ERROR: (.+)", "Agent/SelfReported"),
    ]
    
    for i, line in enumerate(lines):
        for pattern, category in error_patterns:
            m = re.search(pattern, line)
            if m:
                # 获取上下文（前后各2行）
                ctx_start = max(0, i - 2)
                ctx_end = min(len(lines), i + 3)
                context = "\n".join(lines[ctx_start:ctx_end])
                error_msg = m.group(0) if m.lastindex else line.strip()
                errors.append({
                    "session": session_id,
                    "category": category,
                    "message": error_msg[:200],  # 截断
                    "context": context[:500],
                    "line_num": i + 1,
                })
                break  # 一行只匹配一个模式
    
    return errors


def update_error_list(new_errors):
    """把新错误追加到 ERROR_LIST.md"""
    if not new_errors:
        return 0
    
    try:
        existing = ERROR_LIST_PATH.read_text(encoding="utf-8")
    except Exception:
        existing = "# Agent Error List\n"
    
    added = 0
    for err in new_errors:
        # 去重：检查错误消息是否已存在
        if err["message"][:80] in existing:
            continue
        
        # 找到对应分类的section，没有就新建
        section_header = f"## {err['category']}"
        if section_header not in existing:
            existing += f"\n{section_header}\n"
        
        # 在对应section末尾追加
        section_pos = existing.index(section_header)
        # 找到下一个section或文件末尾
        next_section = existing.find("\n## ", section_pos + len(section_header))
        if next_section == -1:
            insert_pos = len(existing)
        else:
            insert_pos = next_section
        
        entry = f"\n- **[{err['session']}] {err['message']}**\n"
        entry += f"  - Context: `{err['context'][:200]}`\n"
        
        existing = existing[:insert_pos] + entry + existing[insert_pos:]
        added += 1
    
    ERROR_LIST_PATH.write_text(existing, encoding="utf-8")
    return added


def copy_jar_to_artifacts(session_id):
    """把 jar 文件复制到 artifacts/"""
    mod_dir = SESSIONS_DIR / session_id / "mod"
    jar_files = list(mod_dir.glob("dist/*.jar")) + list(mod_dir.glob("build/libs/*.jar"))
    
    if not jar_files:
        return False
    
    # 取最大的jar（排除 sources/javadoc）
    jar_files = [f for f in jar_files if "sources" not in f.name and "javadoc" not in f.name]
    if not jar_files:
        return False
    
    jar = max(jar_files, key=lambda f: f.stat().st_size)
    dest = ARTIFACTS_DIR / f"{session_id}_{jar.name}"
    shutil.copy2(jar, dest)
    return True


def cleanup_session(session_id):
    """清理 session 目录，只保留 jar（已复制到 artifacts）"""
    session_dir = SESSIONS_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
    # 清理临时提示词文件
    prompt_file = PROJECT_ROOT / f"prompt_{session_id}.txt"
    if prompt_file.exists():
        prompt_file.unlink()


def run_one_iteration(used_indices, iteration_num):
    """运行一次完整的MOD测试"""
    session_id = get_next_session_id()
    print(f"\n{'='*60}")
    print(f"[迭代 {iteration_num}] Session: {session_id}")
    print(f"{'='*60}")
    
    # 1. 生成提示词
    prompt_text = generate_prompt(session_id, used_indices)
    print(f"[提示词] {prompt_text[:100]}...")
    
    prompt_file = write_prompt_file(session_id, prompt_text)
    
    # 2. 启动 agent（阻塞等待）
    print(f"[启动] run_task.py {session_id}")
    retcode = start_agent_blocking(session_id, prompt_file)
    print(f"[返回码] {retcode}")
    
    # 4. 提取错误
    print(f"[分析] 读取日志...")
    errors = extract_errors_from_log(log_path, session_id)
    print(f"[错误] 发现 {len(errors)} 个错误")
    
    # 5. 更新 ERROR_LIST.md
    if errors:
        added = update_error_list(errors)
        print(f"[更新] ERROR_LIST.md 新增 {added} 条")
    
    # 6. 复制 jar
    has_jar = copy_jar_to_artifacts(session_id)
    if has_jar:
        print(f"[产物] jar 已复制到 artifacts/")
    else:
        print(f"[产物] 未找到 jar 文件")
    
    # 7. 清理
    cleanup_session(session_id)
    print(f"[清理] session {session_id} 已清理")
    
    return len(errors), has_jar


def main():
    print("=" * 60)
    print("  自动化 MOD 测试器")
    print("  API: https://llmapi.paratera.com")
    print("  Model: GLM-4.5-Flash")
    print("=" * 60)
    
    # 验证 .env
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        print("[错误] .env 文件不存在")
        return
    
    env_content = env_file.read_text(encoding="utf-8")
    if "sk--W4L3s3oK6DfN8FSwjBxCg" not in env_content:
        print("[警告] API Key 不是 paratera 的，请检查 .env")
    
    used_indices = set()
    total_errors = 0
    total_jars = 0
    iteration = 1
    
    while True:
        try:
            errors, has_jar = run_one_iteration(used_indices, iteration)
            total_errors += errors
            if has_jar:
                total_jars += 1
            iteration += 1
            
            print(f"\n[统计] 已完成 {iteration-1} 次迭代 | 总错误: {total_errors} | 总JAR: {total_jars}")
            print("[等待] 5秒后开始下一次...\n")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print(f"\n[中断] 用户停止 | 共完成 {iteration-1} 次迭代")
            break
        except Exception as e:
            print(f"\n[异常] {e}")
            print("[等待] 30秒后重试...")
            time.sleep(30)


if __name__ == "__main__":
    main()

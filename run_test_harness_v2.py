# -*- coding: utf-8 -*-
"""自动化 MOD 测试器 v2：不依赖 server.py，直接复制模板+junction。

用法：
    python run_test_harness_v2.py
"""
import os, re, sys, time, shutil, subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SESSIONS_DIR = PROJECT_ROOT / "data" / "sessions"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
ERROR_LIST_PATH = PROJECT_ROOT / "docs" / "agent" / "ERROR_LIST.md"
TEMPLATE_DIR = PROJECT_ROOT / "mod_templates" / "minecraft" / "forge-1.21.11"
MC_SOURCES = PROJECT_ROOT / "mc_java_sources_1.21.11"
DOCS_AGENT = PROJECT_ROOT / "docs" / "agent"
TIMEOUT_SECONDS = 30 * 60
POLL_INTERVAL = 20

ARTIFACTS_DIR.mkdir(exist_ok=True)

MOD_PROMPTS = [
    "做一个简单的自定义物品：红宝石（Ruby），可以作为合成材料，放创造模式标签页。需要物品模型、纹理、语言文件、合成配方。",
    "创建一个自定义方块：蓝晶石方块（Sapphire Block），有发光效果，可以用镐子挖掘。需要完整的方块模型、方块状态、纹理、语言文件。",
    "做一个自定义食物：魔法苹果（Magic Apple），吃了恢复6点饥饿值并给予10秒生命恢复效果。",
    "创建一个自定义工具：黑曜石剑（Obsidian Sword），攻击力8，耐久1500，攻击速度1.6。",
    "做一个自定义工具：黑曜石镐（Obsidian Pickaxe），挖掘速度比钻石镐快，耐久2000。",
    "创建一个自定义盔甲套装：铜甲（Copper Armor），包含头盔、胸甲、护腿、靴子，防御力介于铁甲和钻石甲之间。",
    "做一个有功能的方块：经验储存器（XP Storage），右键点击可以把玩家的经验存入方块，潜行右键可以取出。",
    "创建一个自定义实体：小型史莱姆宠物（Mini Slime Pet），可以用史莱姆球驯服，跟随主人。",
    "做一个自定义投射物：魔法弹（Magic Bolt），右键发射，击中实体造成6点魔法伤害。",
    "创建一个自定义附魔：吸血（Life Steal），最高3级，攻击时回复造成的伤害的10%/20%/30%生命值。",
    "做一个自定义方块实体：充电站（Charging Station），有GUI显示能量，可以给物品充能。",
    "创建一个自定义世界生成：樱花树（Cherry Tree），在平原生物群系自然生成。",
    "做一个自定义命令：/healme，恢复玩家满血并清除负面效果。",
    "创建一个自定义GUI：背包升级台（Backpack Upgrader），有9个槽位可以放入物品。",
    "做一个自定义粒子效果：灵魂火焰（Soul Flame），蓝色火焰粒子。",
    "创建一个自定义声音事件：神秘钟声（Mystic Bell），可以通过命令播放。",
    "做一个自定义进度：红宝石收藏家（Ruby Collector），获得红宝石后解锁。",
    "做一个带动画的方块：脉冲水晶（Pulse Crystal），会发出脉冲光效。",
    "做一个自定义网络包：同步玩家坐标到服务端，用于传送功能。",
    "做一个自定义事件：玩家跳跃事件（Player Jump Event），玩家跳跃时触发。",
]

def load_env():
    env = {}
    p = PROJECT_ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def get_next_session_id():
    existing = [d.name for d in SESSIONS_DIR.iterdir() if d.is_dir() and d.name.startswith("iterauto_")]
    nums = [int(re.match(r"iterauto_(\d+)", n).group(1)) for n in existing if re.match(r"iterauto_(\d+)", n)]
    return f"iterauto_{(max(nums)+1 if nums else 1):03d}"

def setup_session(session_id, prompt_text):
    """创建会话目录，复制模板，建junction，写提示词文件"""
    session_dir = SESSIONS_DIR / session_id
    mod_dir = session_dir / "mod"
    if mod_dir.exists():
        shutil.rmtree(mod_dir, ignore_errors=True)
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制模板
    shutil.copytree(TEMPLATE_DIR, mod_dir, dirs_exist_ok=True)
    
    # mc_java_sources junction
    mc_link = mod_dir / "mc_java_sources"
    if MC_SOURCES.is_dir() and not mc_link.exists():
        subprocess.run(["cmd", "/c", "mklink", "/J", str(mc_link), str(MC_SOURCES)], check=True, capture_output=True)
    
    # docs/agent junction
    docs_link = mod_dir / "docs" / "agent"
    if DOCS_AGENT.is_dir() and not docs_link.exists():
        docs_link.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cmd", "/c", "mklink", "/J", str(docs_link), str(DOCS_AGENT)], check=True, capture_output=True)
    
    # 提示词文件
    prompt_file = Path(os.environ.get("TEMP", str(PROJECT_ROOT))) / f"dsh_prompt_{session_id}.txt"
    prompt_file.write_text(prompt_text, encoding="utf-8")
    
    return session_dir, mod_dir, prompt_file

def run_agent(session_dir, mod_dir, prompt_file, env_extra):
    """启动 run_task.py 并阻塞等待完成"""
    api_key = env_extra.get("DEEPSEEK_API_KEY", "")
    log_path = session_dir / "run.log"
    
    env = {
        **os.environ,
        "PYTHONUNBUFFERED": "1",
        "DSH_MODE": "mod",
        "DSH_SESSION_ROOT": str(session_dir),
        "DSH_AUTO_MODE": "1",
        "DSH_PROMPT_FILE": str(prompt_file),
        "DEEPSEEK_API_KEY": api_key,
        "DSH_BASE_URL": env_extra.get("DSH_BASE_URL", ""),
        "DSH_MODEL": env_extra.get("DSH_MODEL", ""),
        "DSH_CONTEXT_WINDOW": env_extra.get("DSH_CONTEXT_WINDOW", ""),
    }
    
    run_task = PROJECT_ROOT / "server_app" / "run_task.py"
    print(f"[启动] {run_task} | 模型={env['DSH_MODEL']}")
    
    with log_path.open("w", encoding="utf-8") as f:
        proc = subprocess.Popen(
            [sys.executable, str(run_task), str(mod_dir), api_key],
            cwd=str(PROJECT_ROOT),
            stdout=f, stderr=subprocess.STDOUT, env=env,
        )
    
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > TIMEOUT_SECONDS:
            print(f"[超时] {TIMEOUT_SECONDS//60}分钟")
            proc.kill()
            break
        
        ret = proc.poll()
        if ret is not None:
            print(f"[退出] 返回码={ret} | 耗时={int(elapsed)}s")
            break
        
        if log_path.exists():
            try:
                lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
                if len(lines) > 0 and len(lines) % 100 == 0:
                    print(f"[{int(elapsed)}s] {len(lines)}行 | {lines[-1][:100]}", flush=True)
                
                content = "\n".join(lines)
                if "All required tests passed" in content or "RESULT: PASS" in content:
                    print(f"[成功] GameTest通过！耗时={int(elapsed)}s")
                    proc.terminate()
                    try: proc.wait(timeout=10)
                    except: proc.kill()
                    break
                if "RESULT: FAIL" in content and "daemon_loop" in content[-500:]:
                    print(f"[失败] 任务结束 | 耗时={int(elapsed)}s")
                    break
            except: pass
        
        time.sleep(POLL_INTERVAL)
    
    return log_path

def extract_errors(log_path, session_id):
    if not log_path.exists():
        return []
    content = log_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    errors = []
    
    patterns = [
        (r"error: (.+)", "Build/Compile"),
        (r"cannot find symbol", "Build/Compile"),
        (r"package (\S+) does not exist", "Build/Compile"),
        (r"incompatible types", "Build/Compile"),
        (r"BUILD FAILED", "Build/Gradle"),
        (r"Could not resolve", "Build/Gradle"),
        (r"GameTest.*failed", "GameTest"),
        (r"tests failed", "GameTest"),
        (r"Missing model", "Resource"),
        (r"Missing texture", "Resource"),
        (r"NEW_ERROR: (.+)", "Agent/SelfReported"),
    ]
    
    for i, line in enumerate(lines):
        for pattern, category in patterns:
            if re.search(pattern, line):
                ctx = "\n".join(lines[max(0,i-2):i+3])
                errors.append({"session": session_id, "category": category, "message": line.strip()[:200], "context": ctx[:300]})
                break
    return errors

def update_error_list(errors):
    if not errors:
        return 0
    existing = ERROR_LIST_PATH.read_text(encoding="utf-8") if ERROR_LIST_PATH.exists() else "# Agent Error List\n"
    added = 0
    for err in errors:
        if err["message"][:60] in existing:
            continue
        header = f"## {err['category']}"
        if header not in existing:
            existing += f"\n{header}\n"
        pos = existing.index(header)
        nxt = existing.find("\n## ", pos + len(header))
        insert_pos = len(existing) if nxt == -1 else nxt
        entry = f"\n- **[{err['session']}] {err['message']}**\n  - Context: `{err['context'][:200]}`\n"
        existing = existing[:insert_pos] + entry + existing[insert_pos:]
        added += 1
    ERROR_LIST_PATH.write_text(existing, encoding="utf-8")
    return added

def copy_jar(session_id):
    mod_dir = SESSIONS_DIR / session_id / "mod"
    jars = [f for f in list(mod_dir.glob("dist/*.jar")) + list(mod_dir.glob("build/libs/*.jar")) 
            if "sources" not in f.name and "javadoc" not in f.name]
    if not jars:
        return False
    jar = max(jars, key=lambda f: f.stat().st_size)
    shutil.copy2(jar, ARTIFACTS_DIR / f"{session_id}_{jar.name}")
    return True

def main():
    print("=" * 60)
    print("  自动化 MOD 测试器 v2")
    print("=" * 60)
    
    env_extra = load_env()
    print(f"  API: {env_extra.get('DSH_BASE_URL', '?')}")
    print(f"  Model: {env_extra.get('DSH_MODEL', '?')}")
    
    used = set()
    iteration = 1
    total_errors = 0
    total_jars = 0
    
    while True:
        session_id = get_next_session_id()
        prompt_idx = (iteration - 1) % len(MOD_PROMPTS)
        prompt_text = f"[{session_id}] {MOD_PROMPTS[prompt_idx]}"
        
        print(f"\n{'='*60}")
        print(f"[迭代 {iteration}] {session_id}")
        print(f"[提示] {prompt_text[:80]}...")
        
        try:
            session_dir, mod_dir, prompt_file = setup_session(session_id, prompt_text)
            print(f"[模板] 已复制到 {mod_dir}")
            
            log_path = run_agent(session_dir, mod_dir, prompt_file, env_extra)
            
            errors = extract_errors(log_path, session_id)
            print(f"[错误] {len(errors)} 个")
            if errors:
                added = update_error_list(errors)
                print(f"[更新] ERROR_LIST.md +{added} 条")
            
            has_jar = copy_jar(session_id)
            print(f"[产物] {'JAR已保存' if has_jar else '无JAR'}")
            total_errors += len(errors)
            if has_jar: total_jars += 1
            
            # 清理session（jar已复制到artifacts）
            shutil.rmtree(session_dir, ignore_errors=True)
            if prompt_file.exists(): prompt_file.unlink()
            print(f"[清理] 完成")
            
        except Exception as e:
            print(f"[异常] {e}")
            import traceback
            traceback.print_exc()
        
        iteration += 1
        print(f"\n[统计] 完成{iteration-1}次 | 错误{total_errors} | JAR{total_jars}")
        print("[等待] 5秒...")
        time.sleep(5)

if __name__ == "__main__":
    main()

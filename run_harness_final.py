# -*- coding: utf-8 -*-
import os, sys, shutil, subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SESSIONS_DIR = PROJECT_ROOT / "data" / "sessions"
TEMPLATE_DIR = PROJECT_ROOT / "mod_templates" / "minecraft" / "forge-1.21.11"
MC_SOURCES = PROJECT_ROOT / "mc_java_sources_1.21.11"
DOCS_AGENT = PROJECT_ROOT / "docs" / "agent"

def load_env():
    env = {}
    p = PROJECT_ROOT / ".env"
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def run_one(session_id, prompt_text):
    session_dir = SESSIONS_DIR / session_id
    mod_dir = session_dir / "mod"
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制模板
    shutil.copytree(TEMPLATE_DIR, mod_dir, dirs_exist_ok=True)
    
    # junction
    mc_link = mod_dir / "mc_java_sources"
    if not mc_link.exists():
        subprocess.run(["cmd", "/c", "mklink", "/J", str(mc_link), str(MC_SOURCES)], check=True, capture_output=True)
    docs_link = mod_dir / "docs" / "agent"
    if not docs_link.exists():
        docs_link.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cmd", "/c", "mklink", "/J", str(docs_link), str(DOCS_AGENT)], check=True, capture_output=True)
    
    # 提示词文件
    prompt_file = Path(os.environ.get("TEMP", str(PROJECT_ROOT))) / f"prompt_{session_id}.txt"
    prompt_file.write_text(prompt_text, encoding="utf-8")
    
    # 加载配置
    env_extra = load_env()
    api_key = env_extra["DEEPSEEK_API_KEY"]
    
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
    
    log_path = session_dir / "run.log"
    run_task = PROJECT_ROOT / "server_app" / "run_task.py"
    
    print(f"[启动] {session_id} | 模型={env['DSH_MODEL']} | 日志={log_path}", flush=True)
    
    with log_path.open("w", encoding="utf-8") as f:
        proc = subprocess.run(
            [sys.executable, str(run_task), str(mod_dir), api_key],
            cwd=str(PROJECT_ROOT),
            stdout=f, stderr=subprocess.STDOUT, env=env,
            timeout=1800,  # 30分钟超时
        )
    
    print(f"[完成] 返回码={proc.returncode}", flush=True)
    return log_path

if __name__ == "__main__":
    prompts = [
        "做一个简单的自定义物品：红宝石（Ruby），可以作为合成材料，放创造模式标签页。需要物品模型、纹理、语言文件、合成配方。",
        "创建一个自定义方块：蓝晶石方块（Sapphire Block），有发光效果，可以用镐子挖掘。需要完整的方块模型、方块状态、纹理、语言文件。",
        "做一个自定义食物：魔法苹果（Magic Apple），吃了恢复6点饥饿值并给予10秒生命恢复效果。",
        "创建一个自定义工具：黑曜石剑（Obsidian Sword），攻击力8，耐久1500，攻击速度1.6。",
        "做一个自定义工具：黑曜石镐（Obsidian Pickaxe），挖掘速度比钻石镐快，耐久2000。",
        "创建一个自定义盔甲套装：铜甲（Copper Armor），包含头盔、胸甲、护腿、靴子，防御力介于铁甲和钻石甲之间。",
        "做一个有功能的方块：经验储存器（XP Storage），右键点击可以把玩家的经验存入方块。",
        "创建一个自定义实体：小型史莱姆宠物（Mini Slime Pet），可以用史莱姆球驯服，跟随主人。",
        "做一个自定义投射物：魔法弹（Magic Bolt），右键发射，击中实体造成6点魔法伤害。",
        "创建一个自定义附魔：吸血（Life Steal），最高3级，攻击时回复造成的伤害的10%/20%/30%生命值。",
        "做一个自定义方块实体：充电站（Charging Station），有GUI显示能量。",
        "做一个自定义命令：/healme，恢复玩家满血并清除负面效果。",
        "做一个自定义粒子效果：灵魂火焰（Soul Flame），蓝色火焰粒子。",
        "做一个自定义进度：红宝石收藏家（Ruby Collector），获得红宝石后解锁。",
        "做一个自定义网络包：同步玩家坐标到服务端，用于传送功能。",
    ]
    
    import re, time
    from datetime import datetime
    
    ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    ERROR_LIST_PATH = PROJECT_ROOT / "docs" / "agent" / "ERROR_LIST.md"
    
    for i, prompt in enumerate(prompts, 1):
        session_id = f"iterauto_{i:03d}"
        full_prompt = f"[{session_id}] {prompt}"
        
        print(f"\n{'='*60}", flush=True)
        print(f"[迭代 {i}/{len(prompts)}] {session_id}", flush=True)
        print(f"[提示] {prompt[:80]}...", flush=True)
        
        try:
            log_path = run_one(session_id, full_prompt)
            
            # 提取错误
            if log_path.exists():
                content = log_path.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                
                error_patterns = [
                    r"error: .+", r"cannot find symbol", r"package \S+ does not exist",
                    r"incompatible types", r"BUILD FAILED", r"Could not resolve",
                    r"GameTest.*failed", r"tests failed", r"Missing model", r"Missing texture",
                    r"NEW_ERROR: .+",
                ]
                
                found_errors = []
                for ln in lines:
                    for pat in error_patterns:
                        if re.search(pat, ln):
                            found_errors.append(ln.strip()[:200])
                            break
                
                # 追加到ERROR_LIST.md
                if found_errors:
                    existing = ERROR_LIST_PATH.read_text(encoding="utf-8") if ERROR_LIST_PATH.exists() else ""
                    added = 0
                    for err in found_errors:
                        if err[:60] not in existing:
                            # 简单追加到末尾
                            existing += f"\n- **[{session_id}] {err}**\n"
                            added += 1
                    if added > 0:
                        ERROR_LIST_PATH.write_text(existing, encoding="utf-8")
                        print(f"[错误] 发现{len(found_errors)}条，新增{added}条到ERROR_LIST.md", flush=True)
                    else:
                        print(f"[错误] 发现{len(found_errors)}条，全已存在", flush=True)
                else:
                    print("[错误] 无", flush=True)
                
                # 检查jar
                mod_dir = SESSIONS_DIR / session_id / "mod"
                jars = [f for f in list(mod_dir.glob("dist/*.jar")) + list(mod_dir.glob("build/libs/*.jar"))
                        if "sources" not in f.name and "javadoc" not in f.name]
                if jars:
                    jar = max(jars, key=lambda f: f.stat().st_size)
                    dest = ARTIFACTS_DIR / f"{session_id}_{jar.name}"
                    shutil.copy2(jar, dest)
                    print(f"[产物] {jar.name} -> {dest.name}", flush=True)
                else:
                    print("[产物] 无JAR", flush=True)
                
                # 检查是否通过测试
                if "All required tests passed" in content:
                    print("[结果] GameTest通过 ✓", flush=True)
                else:
                    print("[结果] 未通过或未运行测试", flush=True)
            
            # 清理session
            shutil.rmtree(session_dir, ignore_errors=True)
            prompt_file = Path(os.environ.get("TEMP", str(PROJECT_ROOT))) / f"prompt_{session_id}.txt"
            if prompt_file.exists():
                prompt_file.unlink()
            print(f"[清理] 完成", flush=True)
            
        except subprocess.TimeoutExpired:
            print(f"[超时] 30分钟，跳过", flush=True)
            shutil.rmtree(session_dir, ignore_errors=True)
        except Exception as e:
            print(f"[异常] {e}", flush=True)
            import traceback
            traceback.print_exc()
        
        print("[等待] 5秒...", flush=True)
        time.sleep(5)
    
    print("\n[完成] 所有迭代结束", flush=True)
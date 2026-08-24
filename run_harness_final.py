# -*- coding: utf-8 -*-
import os, sys, shutil, subprocess, re, time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SESSIONS_DIR = PROJECT_ROOT / "data" / "sessions"
TEMPLATE_DIR = PROJECT_ROOT / "mod_templates" / "minecraft" / "forge-1.21.11"
MC_SOURCES = PROJECT_ROOT / "mc_java_sources_1.21.11"
DOCS_AGENT = PROJECT_ROOT / "docs" / "agent"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
ERROR_LIST_PATH = PROJECT_ROOT / "docs" / "agent" / "ERROR_LIST.md"

ARTIFACTS_DIR.mkdir(exist_ok=True)

# paratera config (hardcoded, not touching .env)
API_KEY = "sk--W4L3s3oK6DfN8FSwjBxCg"
BASE_URL = "https://llmapi.paratera.com"
MODEL = "GLM-5.2"
CTX_WINDOW = "1000000"

PROMPTS = [
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

START_FROM = 1  # restart from beginning

def run_one(session_id, prompt_text):
    session_dir = SESSIONS_DIR / session_id
    mod_dir = session_dir / "mod"
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)
    session_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(TEMPLATE_DIR, mod_dir, dirs_exist_ok=True)

    mc_link = mod_dir / "mc_java_sources"
    if not mc_link.exists():
        subprocess.run(["cmd", "/c", "mklink", "/J", str(mc_link), str(MC_SOURCES)], check=True, capture_output=True)
    docs_link = mod_dir / "docs" / "agent"
    if not docs_link.exists():
        docs_link.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cmd", "/c", "mklink", "/J", str(docs_link), str(DOCS_AGENT)], check=True, capture_output=True)

    prompt_file = Path(os.environ.get("TEMP", str(PROJECT_ROOT))) / f"prompt_{session_id}.txt"
    prompt_file.write_text(prompt_text, encoding="utf-8")

    env = {
        **os.environ,
        "PYTHONUNBUFFERED": "1",
        "DSH_MODE": "mod",
        "DSH_SESSION_ROOT": str(session_dir),
        "DSH_AUTO_MODE": "1",
        "DSH_PROMPT_FILE": str(prompt_file),
        "DEEPSEEK_API_KEY": API_KEY,
        "DSH_BASE_URL": BASE_URL,
        "DSH_MODEL": MODEL,
        "DSH_CONTEXT_WINDOW": CTX_WINDOW,
    }

    log_path = session_dir / "run.log"
    run_task = PROJECT_ROOT / "server_app" / "run_task.py"

    print(f"[start] {session_id} | model={MODEL} | log={log_path}", flush=True)

    with log_path.open("w", encoding="utf-8") as f:
        proc = subprocess.Popen(
            [sys.executable, str(run_task), str(mod_dir), API_KEY],
            cwd=str(PROJECT_ROOT),
            stdout=f, stderr=subprocess.STDOUT, env=env,
        )

    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed > 1800:
            print(f"[timeout] 30min, kill", flush=True)
            proc.kill()
            proc.wait()
            break

        ret = proc.poll()
        if ret is not None:
            print(f"[done] ret={ret} | {int(elapsed)}s", flush=True)
            break

        # just monitor, dont kill on GameTest pass - let agent finish and build jar
        if log_path.exists() and int(elapsed) % 60 == 0:
            try:
                content = log_path.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                if lines:
                    print(f"[{int(elapsed)}s] {len(lines)} lines | {lines[-1][:80]}", flush=True)
            except:
                pass

        time.sleep(15)

    # process finished, wait a bit for file flush
    time.sleep(3)
    return log_path

def extract_and_record_errors(log_path, session_id):
    if not log_path.exists():
        print("[errors] no log", flush=True)
        return 0
    content = log_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    patterns = [
        r"error: .+", r"cannot find symbol", r"package \S+ does not exist",
        r"incompatible types", r"BUILD FAILED", r"Could not resolve",
        r"GameTest.*failed", r"tests failed", r"Missing model", r"Missing texture",
        r"NEW_ERROR: .+",
    ]

    found = []
    for ln in lines:
        for pat in patterns:
            if re.search(pat, ln):
                if any(x in ln for x in ["WRITE FIRST", "read the first", "do not speculate", "On compile error:"]):
                    continue
                found.append(ln.strip()[:200])
                break

    if not found:
        print("[errors] none", flush=True)
        return 0

    existing = ERROR_LIST_PATH.read_text(encoding="utf-8") if ERROR_LIST_PATH.exists() else "# Agent Error List\n"
    added = 0
    for err in found:
        if err[:60] not in existing:
            existing += f"\n- **[{session_id}] {err}**\n"
            added += 1
    if added > 0:
        ERROR_LIST_PATH.write_text(existing, encoding="utf-8")
    print(f"[errors] {len(found)} found, {added} new added to ERROR_LIST.md", flush=True)
    return added

def copy_jar(session_id):
    mod_dir = SESSIONS_DIR / session_id / "mod"
    jars = [f for f in list(mod_dir.glob("dist/*.jar")) + list(mod_dir.glob("build/libs/*.jar"))
            if "sources" not in f.name and "javadoc" not in f.name]
    if not jars:
        print("[jar] none", flush=True)
        return False
    jar = max(jars, key=lambda f: f.stat().st_size)
    dest = ARTIFACTS_DIR / f"{session_id}_{jar.name}"
    shutil.copy2(jar, dest)
    print(f"[jar] {jar.name} -> {dest.name} ({jar.stat().st_size} bytes)", flush=True)
    return True

def main():
    print(f"=== MOD Test Harness | {MODEL} @ {BASE_URL} ===", flush=True)
    print(f"Starting from iteration {START_FROM}", flush=True)

    for i in range(START_FROM, len(PROMPTS) + 1):
        session_id = f"iterauto_{i:03d}"
        prompt = PROMPTS[i - 1]
        full_prompt = f"[{session_id}] {prompt}"

        print(f"\n{'='*60}", flush=True)
        print(f"[iter {i}/{len(PROMPTS)}] {session_id}", flush=True)
        print(f"[prompt] {prompt[:80]}...", flush=True)

        try:
            log_path = run_one(session_id, full_prompt)
            extract_and_record_errors(log_path, session_id)
            copy_jar(session_id)

            if log_path.exists():
                content = log_path.read_text(encoding="utf-8", errors="replace")
                if "All required tests passed" in content:
                    print("[result] GameTest PASS", flush=True)
                else:
                    print("[result] not passed", flush=True)

            # cleanup session
            session_dir = SESSIONS_DIR / session_id
            shutil.rmtree(session_dir, ignore_errors=True)
            prompt_file = Path(os.environ.get("TEMP", str(PROJECT_ROOT))) / f"prompt_{session_id}.txt"
            if prompt_file.exists():
                prompt_file.unlink()
            print("[cleanup] done", flush=True)

        except Exception as e:
            print(f"[error] {e}", flush=True)
            import traceback
            traceback.print_exc()

        print("[wait] 5s...", flush=True)
        time.sleep(5)

    print("\n=== ALL DONE ===", flush=True)

if __name__ == "__main__":
    main()

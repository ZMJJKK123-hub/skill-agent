# -*- coding: utf-8 -*-
"""MOD test harness: GLM-5.2 @ paratera, run agent, collect errors, save jars."""
import os, sys, re, time, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SESSIONS = ROOT / "data" / "sessions"
TPL = ROOT / "mod_templates" / "minecraft" / "forge-1.21.11"
MCSRC = ROOT / "mc_java_sources_1.21.11"
DOCS = ROOT / "docs" / "agent"
ART = ROOT / "artifacts"
ERRLIST = DOCS / "ERROR_LIST.md"
ART.mkdir(exist_ok=True)

API_KEY = "sk--W4L3s3oK6DfN8FSwjBxCg"
BASE_URL = "https://llmapi.paratera.com"
MODEL = "GLM-5.2"

PROMPTS = [
    "做一个自定义物品：蓝宝石（Sapphire），可做合成材料，放创造模式标签页。需要物品模型、纹理、语言文件、合成配方。",
    "创建一个自定义方块：红石方块（Redstone Block），有发光效果，可被镐子挖掘。需要方块模型、方块状态、纹理、语言文件。",
    "做一个自定义食物：黄金苹果派（Golden Pie），吃了恢复8点饥饿值并给予30秒生命恢复II效果。需要食物属性、合成配方。",
    "创建一个自定义工具：翡翠剑（Emerald Sword），攻击力9，耐久1800，攻击速度1.8。需要工具材料、合成配方。",
    "做一个自定义工具：翡翠镐（Emerald Pickaxe），挖掘速度比钻石快，耐久2200。需要工具材料、合成配方。",
    "创建一个自定义盔甲套装：暗影甲（Shadow Armor），头盔/胸甲/护腿/靴子，防御力高于钻石甲。需要盔甲材质、合成配方。",
    "做一个有功能的方块：物品 sorter（Item Sorter），右键打开GUI，有9个槽位自动排序。需要方块实体、菜单、屏幕。",
    "创建一个自定义实体：火焰精灵（Fire Sprite），会飞，攻击玩家造成火焰伤害。需要实体注册、AI、渲染器。",
    "做一个自定义投射物：冰霜箭（Frost Arrow），击中实体造成6点伤害并减速。需要投射物、渲染器、物品。",
    "创建一个自定义附魔：雷击（Thunder Strike），最高3级，攻击时有概率召唤闪电。需要附魔定义、效果组件。",
    "做一个自定义方块实体：储物箱（Storage Box），有27格存储，右键打开GUI。需要方块实体、菜单、屏幕、数据同步。",
    "做一个自定义命令：/fly，切换玩家飞行模式。需要命令注册、权限、反馈消息。",
    "做一个自定义粒子效果：魔法星尘（Magic Dust），紫色闪烁粒子。需要粒子注册、渲染器。",
    "做一个自定义进度：翡翠猎人（Emerald Hunter），获得翡翠物品后解锁，奖励50经验。需要进度JSON。",
    "做一个自定义网络包：客户端请求服务端传送，服务端验证后传送玩家。需要SimpleChannel、编码解码。",
    "做一个自定义事件监听：玩家挖矿时获得双倍掉落（Fortune效果），持续10秒。需要Forge事件、事件处理。",
    "创建一个自定义液体：液态翡翠（Liquid Emerald），流动比水慢，接触变绿宝石块。需要流体注册、方块状态。",
    "做一个自定义附魔：传送（Teleport），攻击时将目标传送至随机位置。需要附魔、实体效果。",
    "创建一个自定义村民职业：翡翠商人（Emerald Merchant），交易翡翠物品。需要职业注册、交易列表。",
    "做一个自定义药水：飞行药水（Potion of Flight），饮用后获得10秒飞行能力。需要药水效果注册、酿造配方。",
]

def setup(sess_id, prompt):
    sd = SESSIONS / sess_id
    md = sd / "mod"
    if sd.exists(): shutil.rmtree(sd, ignore_errors=True)
    sd.mkdir(parents=True)
    shutil.copytree(TPL, md, dirs_exist_ok=True)
    # junctions
    for name, src in [("mc_java_sources", MCSRC), ("docs/agent", DOCS)]:
        link = md / name
        if not link.exists():
            link.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["cmd","/c","mklink","/J",str(link),str(src)], check=True, capture_output=True)
    pf = Path(os.environ.get("TEMP",str(ROOT))) / f"p_{sess_id}.txt"
    pf.write_text(f"[{sess_id}] {prompt}", encoding="utf-8")
    return sd, md, pf

def run(sess_id, md, pf):
    env = {**os.environ,
        "PYTHONUNBUFFERED":"1", "DSH_MODE":"mod",
        "DSH_SESSION_ROOT":str(SESSIONS/sess_id), "DSH_AUTO_MODE":"1",
        "DSH_PROMPT_FILE":str(pf),
        "DEEPSEEK_API_KEY":API_KEY, "DSH_BASE_URL":BASE_URL,
        "DSH_MODEL":MODEL, "DSH_CONTEXT_WINDOW":"1000000",
        "DSH_DISABLE_CLIENT_TOOLS":"1", "DSH_VISION_ENABLED":"0"}
    log = SESSIONS / sess_id / "run.log"
    rt = ROOT / "server_app" / "run_task.py"
    print(f"[start] {sess_id} model={MODEL}", flush=True)
    with log.open("w",encoding="utf-8") as f:
        p = subprocess.Popen([sys.executable,str(rt),str(md),API_KEY],
            cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, env=env)
    t0 = time.time()
    while True:
        el = time.time() - t0
        if el > 1800:
            print(f"[timeout] 30min", flush=True)
            p.kill(); p.wait()
            break
        r = p.poll()
        if r is not None:
            print(f"[exit] ret={r} {int(el)}s", flush=True)
            break
        # progress
        if log.exists() and int(el) % 120 == 0:
            try:
                ls = log.read_text(encoding="utf-8",errors="replace").splitlines()
                if ls: print(f"[{int(el)}s] {len(ls)} lines | {ls[-1][:80]}", flush=True)
            except: pass
        time.sleep(15)
    time.sleep(3)  # flush
    return log

def extract(log, sid):
    if not log.exists(): return []
    c = log.read_text(encoding="utf-8",errors="replace")
    ls = c.splitlines()
    pats = [r"error: .+", r"cannot find symbol", r"package \S+ does not exist",
        r"incompatible types", r"BUILD FAILED", r"Could not resolve",
        r"GameTest.*failed", r"tests failed", r"Missing model", r"Missing texture",
        r"NEW_ERROR: .+"]
    found = []
    for ln in ls:
        for p in pats:
            if re.search(p, ln):
                if any(x in ln for x in ["WRITE FIRST","read the first","do not speculate","On compile error:"]):
                    continue
                found.append(ln.strip()[:200]); break
    if not found: return []
    # append to ERROR_LIST
    ex = ERRLIST.read_text(encoding="utf-8") if ERRLIST.exists() else ""
    added = 0
    for e in found:
        if e[:60] not in ex:
            ex += f"\n- **[{sid}] {e}**\n"; added += 1
    if added: ERRLIST.write_text(ex, encoding="utf-8")
    print(f"[errors] {len(found)} found, {added} new", flush=True)
    return found

def save_jar(sid):
    md = SESSIONS / sid / "mod"
    jars = [f for f in list(md.glob("dist/*.jar"))+list(md.glob("build/libs/*.jar"))
            if "sources" not in f.name and "javadoc" not in f.name]
    if not jars:
        print("[jar] none", flush=True); return False
    j = max(jars, key=lambda f: f.stat().st_size)
    d = ART / f"{sid}_{j.name}"
    shutil.copy2(j, d)
    print(f"[jar] {j.name} -> {d.name} ({j.stat().st_size}B)", flush=True)
    return True

def cleanup(sid):
    sd = SESSIONS / sid
    if sd.exists(): shutil.rmtree(sd, ignore_errors=True)
    pf = Path(os.environ.get("TEMP",str(ROOT))) / f"p_{sid}.txt"
    if pf.exists(): pf.unlink()

def main():
    print(f"=== GLM-5.2 Test Harness ===", flush=True)
    for i, p in enumerate(PROMPTS, 1):
        sid = f"iterauto_{i:03d}"
        print(f"\n{'='*50}\n[{i}/{len(PROMPTS)}] {sid}\n{'='*50}", flush=True)
        print(f"[prompt] {p[:70]}...", flush=True)
        try:
            sd, md, pf = setup(sid, p)
            log = run(sid, md, pf)
            extract(log, sid)
            save_jar(sid)
            if log.exists():
                c = log.read_text(encoding="utf-8",errors="replace")
                print("[result] " + ("PASS" if "All required tests passed" in c else "incomplete"), flush=True)
            cleanup(sid)
        except Exception as e:
            print(f"[err] {e}", flush=True)
            import traceback; traceback.print_exc()
            cleanup(sid)
        print("[wait] 5s", flush=True)
        time.sleep(5)
    print("\n=== DONE ===", flush=True)

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""MOD test harness v3: focus on API changes, collect errors, save jars."""
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

# Prompts designed to trigger different API surfaces and common 1.21.11 migration errors
PROMPTS = [
    # Registry / item registration API changes
    "做一个自定义物品：钛锭（Titanium Ingot），用DeferredRegister注册，放创造模式标签页。需要物品模型、纹理、语言文件、合成配方。",
    "创建一个自定义方块：虚空石（Voidstone），用DeferredRegister<Block>注册，有发光效果。需要方块模型、方块状态、纹理、语言文件。",
    # Tool material / weapon API (no SwordItem in 1.21.11)
    "做一个自定义武器：星辰剑（Astral Blade），攻击力10，耐久3000，攻击速度2.0。使用Item.Properties.sword()方法，不要用SwordItem类。",
    "做一个自定义工具：星辰镐（Astral Pickaxe），挖掘速度比下界合金快，耐久3000。使用Item.Properties.pickaxe()方法。",
    "做一个自定义斧头：星辰斧（Astral Axe），攻击力9，耐久3000。使用AxeItem类和ToolMaterial。",
    # Creative tab API (BuildCreativeModeTabContentsEvent vs old API)
    "做一个自定义物品：银粒（Silver Nugget），注册到自定义创造模式标签页。使用BuildCreativeModeTabContentsEvent事件。",
    # BlockEntity / menu / screen (GUI API)
    "做一个自定义方块实体：储物柜（Locker），右键打开9格GUI界面。需要BlockEntity、MenuType、AbstractContainerMenu、AbstractContainerScreen。",
    "做一个自定义方块实体：熔炉升级版（Enhanced Furnace），冶炼速度2倍。需要BlockEntity、tick逻辑、GUI。",
    # Networking API (SimpleChannel / ChannelBuilder)
    "做一个自定义网络包：客户端按键同步，按G键在服务端生成闪电。需要SimpleChannel、ChannelBuilder、编码解码、客户端事件。",
    # Entity registration and rendering
    "做一个自定义实体：魔法蝴蝶（Magic Butterfly），会飞行，有自定义AI。需要EntityType注册、实体渲染器、实体模型。",
    "做一个自定义投射物：能量弹（Energy Bolt），右键发射，击中方块产生爆炸。需要投射物实体、渲染器、碰撞检测。",
    # Capability system
    "做一个自定义Capability：给物品添加能量存储能力（Energy Capability），可以通过物品交互充放电。需要ICapabilityProvider、LazyOptional、NBT持久化。",
    # Event system (Forge 1.21.11 typed events)
    "做一个自定义事件监听：玩家攻击实体时触发闪电效果。使用typed event bus（LivingHurtEvent.BUS.addListener），不要用旧@SubscribeEvent。",
    "做一个自定义事件监听：方块被破坏时掉落额外物品。使用BlockEvent.BUS.addListener。",
    # Data components (1.21.11 component system)
    "做一个自定义物品：变形药水（Polymorph Potion），使用DataComponents.POTION_CONTENTS存储药水效果。需要药水效果注册、物品组件。",
    "做一个自定义物品：附魔书（Custom Enchanted Book），使用DataComponents.STORED_ENCHANTMENTS存储附魔。需要附魔定义、物品组件。",
    # World gen (configured feature / placed feature)
    "做一个自定义世界生成：水晶树（Crystal Tree），在末地生物群系生成。需要configured_feature、placed_feature、biome修改。",
    # Recipe system
    "做一个自定义配方：无序合成，用3个钛锭合成1个钛块。需要recipe JSON、tag引用。",
    "做一个自定义熔炼配方：熔炼钛矿石得到钛锭，需要熔炉配方JSON。",
    # Advancement system
    "做一个自定义进度：星辰猎人（Astral Hunter），获得星辰剑后解锁，奖励100经验。需要advancement JSON、trigger。",
    # Particle / sound system
    "做一个自定义粒子：星辰粒子（Astral Particle），蓝紫色闪烁粒子。需要ParticleType注册、ParticleProvider、渲染器。",
    "做一个自定义声音：星辰钟声（Astral Chime），可通过命令播放。需要SoundEvent注册、sounds.json。",
    # Block state / property system
    "做一个自定义方块：变色方块（Chroma Block），有6种颜色状态，右键切换。需要BlockState属性、Property、交互逻辑。",
    # Enchantment system (data-driven)
    "做一个自定义附魔：经验汲取（Experience Drain），攻击时从目标汲取经验。需要enchantment JSON、effect components。",
    # Command system
    "做一个自定义命令：/setday，设置时间为白天（1000）。需要命令注册、权限级别、参数解析。",
    # Fluid system
    "做一个自定义流体：液态星辰（Liquid Astral），蓝色流动液体。需要Fluid注册、FluidState、方块状态。",
    # Mob effect / potion
    "做一个自定义药水效果：浮空（Levitation Plus），让目标浮空10秒。需要MobEffect注册、药水物品、酿造配方。",
    # Tag system
    "做一个自定义标签：钛制品标签（Titanium Items Tag），包含钛锭、钛块等。需要tag JSON、物品引用。",
    # Model / rendering (BakedModel, BEWLR)
    "做一个自定义物品渲染：能量剑（Energy Sword），使用BEWLR动态渲染，根据耐久度改变颜色。需要BlockEntityWithoutLevelRenderer、BakedModel#isCustomRenderer。",
    # Dimension / portal
    "做一个自定义传送门：星辰传送门，用星辰块搭建，点燃后传送到自定义维度。需要维度注册、传送门逻辑。",
    # Loot table
    "做一个自定义战利品表：僵尸掉落钛锭（10%概率）。需要loot_table JSON、条件、条目。",
    # Data storage (SavedData)
    "做一个自定义数据存储：世界统计（World Stats），记录服务器在线时间。需要SavedData、Codec、NBT持久化。",
    # Access Transformer
    "做一个使用Access Transformer的MOD：修改MinecraftServer的tick方法可见性。需要AT文件、build.gradle配置。",
    # Mixed: multiple systems at once
    "做一个综合MOD：星辰工具套装（Astral Tools），包含剑、镐、斧、铲、锄，加上自定义创造模式标签页和合成配方。需要工具材料、物品注册、创造标签、资源文件。",
]

def setup(sess_id, prompt):
    sd = SESSIONS / sess_id
    md = sd / "mod"
    if sd.exists(): shutil.rmtree(sd, ignore_errors=True)
    sd.mkdir(parents=True)
    shutil.copytree(TPL, md, dirs_exist_ok=True)
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
        "DSH_DISABLE_CLIENT_TOOLS":"1", "DSH_VISION_ENABLED":"0",
        "DSH_DAEMON_IDLE_TIMEOUT":"120"}
    log = SESSIONS / sess_id / "run.log"
    rt = ROOT / "server_app" / "run_task.py"
    print(f"[start] {sess_id}", flush=True)
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
        if log.exists() and int(el) % 120 == 0:
            try:
                ls = log.read_text(encoding="utf-8",errors="replace").splitlines()
                if ls: print(f"[{int(el)}s] {len(ls)} lines | {ls[-1][:80]}", flush=True)
            except: pass
        time.sleep(15)
    time.sleep(3)
    return log

def extract(log, sid):
    if not log.exists(): return []
    c = log.read_text(encoding="utf-8",errors="replace")
    ls = c.splitlines()
    pats = [
        r"error: .+", r"cannot find symbol", r"package \S+ does not exist",
        r"incompatible types", r"BUILD FAILED", r"Could not resolve",
        r"GameTest.*failed", r"tests failed", r"Missing model", r"Missing texture",
        r"NEW_ERROR: .+",
        r"method .+ cannot be applied",
        r"class .+ is not public",
        r"variable .+ might not have been initialized",
        r"\.class.*expected",
        r"illegal start of (type|expression)",
    ]
    found = []
    for ln in ls:
        for p in pats:
            if re.search(p, ln):
                if any(x in ln for x in ["WRITE FIRST","read the first","do not speculate","On compile error:"]):
                    continue
                found.append(ln.strip()[:250]); break
    if not found: return []
    ex = ERRLIST.read_text(encoding="utf-8") if ERRLIST.exists() else ""
    added = 0
    for e in found:
        # Use first 80 chars as dedup key
        key = e[:80]
        if key not in ex:
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
    print(f"=== GLM-5.2 API Test Harness v3 ===", flush=True)
    print(f"Prompts: {len(PROMPTS)}", flush=True)
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
    print("\n=== ALL DONE ===", flush=True)

if __name__ == "__main__":
    main()

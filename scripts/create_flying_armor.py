# -*- coding: utf-8 -*-
"""Generate a working Flying Armor MOD workspace (manual fallback for complex task)."""
import json
import os
import shutil
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root
TARGET = ROOT / "build_workspace" / "flyingarmor"
MODID = "flyingarmor"
PACKAGE = "com.flyingarmor.flyingarmor"
PKG_PATH = Path("src/main/java") / PACKAGE.replace(".", "/")
TEST_PKG = "com.flyingarmor.flyingarmor.tests"
TEST_PATH = Path("src/test/java") / TEST_PKG.replace(".", "/")

MATERIALS = [
    ("leather", "minecraft:leather_chestplate", "ArmorMaterials.LEATHER", (139, 90, 43, 255)),
    ("chainmail", "minecraft:chainmail_chestplate", "ArmorMaterials.CHAINMAIL", (192, 192, 192, 255)),
    ("iron", "minecraft:iron_chestplate", "ArmorMaterials.IRON", (220, 220, 220, 255)),
    ("gold", "minecraft:golden_chestplate", "ArmorMaterials.GOLD", (250, 210, 60, 255)),
    ("diamond", "minecraft:diamond_chestplate", "ArmorMaterials.DIAMOND", (80, 220, 240, 255)),
    ("netherite", "minecraft:netherite_chestplate", "ArmorMaterials.NETHERITE", (70, 60, 60, 255)),
]

ASSET = Path("src/main/resources/assets") / MODID
DATA = Path("src/main/resources/data") / MODID


def clean_target():
    for sub in ["src", "build", "run", ".gradle", "dist", "run-data"]:
        p = TARGET / sub
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
    (TARGET / "src").mkdir(parents=True, exist_ok=True)


def write(path, content):
    p = TARGET / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def write_png(path, rgba):
    p = TARGET / path
    p.parent.mkdir(parents=True, exist_ok=True)
    w = h = 16
    raw = b"".join(b"\x00" + bytes(rgba) * w for _ in range(h))

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    p.write_bytes(png)


def build_gradle():
    p = TARGET / "build.gradle"
    s = p.read_text(encoding="utf-8")
    s = s.replace("group = 'com.example.simplemod'", "group = 'com.flyingarmor.flyingarmor'")
    s = s.replace("forge.enabledGameTestNamespaces', 'simplemod'", "forge.enabledGameTestNamespaces', 'flyingarmor'")
    s = s.replace("args '--mod', 'simplemod'", "args '--mod', 'flyingarmor'")
    p.write_text(s, encoding="utf-8")


def settings_gradle():
    p = TARGET / "settings.gradle"
    s = p.read_text(encoding="utf-8")
    s = s.replace("rootProject.name = 'simplemod'", "rootProject.name = 'flyingarmor'")
    p.write_text(s, encoding="utf-8")


def mods_toml():
    p = TARGET / "src/main/resources/META-INF/mods.toml"
    if not p.exists():
        return
    s = p.read_text(encoding="utf-8")
    s = s.replace("simplemod", "flyingarmor")
    p.write_text(s, encoding="utf-8")


def java_main():
    items = "".join(
        f'    public static final RegistryObject<Item> FLYING_{m[0].upper()}_CHESTPLATE = '
        f'ITEMS.register("flying_{m[0]}_chestplate", () -> new FlyingChestplateItem({m[2]}, '
        f'ArmorType.CHESTPLATE, new Item.Properties().setId(ITEMS.key("flying_{m[0]}_chestplate"))));\n'
        for m in MATERIALS
    )
    write(PKG_PATH / "FlyingArmorMod.java", f"""package {PACKAGE};

import net.minecraft.world.item.Item;
import net.minecraft.world.item.equipment.ArmorMaterials;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

@Mod(FlyingArmorMod.MODID)
public class FlyingArmorMod {{
    public static final String MODID = "{MODID}";
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MODID);

{items}
    public FlyingArmorMod(FMLJavaModLoadingContext context) {{
        ITEMS.register(context.getModBusGroup());
    }}
}}
""")
    write(PKG_PATH / "FlyingChestplateItem.java", f"""package {PACKAGE};

import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;

public class FlyingChestplateItem extends Item {{
    public FlyingChestplateItem(ArmorMaterial material, ArmorType type, Properties properties) {{
        super(properties.humanoidArmor(material, type));
    }}

    @Override
    public boolean canElytraFly(ItemStack stack, LivingEntity entity) {{
        return true;
    }}

    @Override
    public boolean elytraFlightTick(ItemStack stack, LivingEntity entity, int flightTicks) {{
        if (!entity.level().isClientSide()) {{
            int next = flightTicks + 1;
            if (next % 10 == 0) {{
                stack.hurtAndBreak(1, entity, EquipmentSlot.CHEST);
            }}
        }}
        return true;
    }}
}}
""")


def assets():
    en = {}
    zh_names = {
        "leather": "皮革", "chainmail": "锁链", "iron": "铁", "gold": "金", "diamond": "钻石", "netherite": "下界合金"
    }
    zh = {}
    for name, vanilla, mat, color in MATERIALS:
        en[f"item.{MODID}.flying_{name}_chestplate"] = f"Flying {name.title()} Chestplate"
        zh[f"item.{MODID}.flying_{name}_chestplate"] = f"飞行{zh_names[name]}胸甲"
        item_id = f"flying_{name}_chestplate"
        write(ASSET / "items" / f"{item_id}.json", json.dumps({
            "model": {"type": "minecraft:model", "model": f"{MODID}:item/{item_id}"}
        }, ensure_ascii=False, indent=2))
        write(ASSET / "models/item" / f"{item_id}.json", json.dumps({
            "parent": "minecraft:item/generated",
            "textures": {"layer0": f"{MODID}:item/{item_id}"}
        }, ensure_ascii=False, indent=2))
        write_png(ASSET / "textures/item" / f"{item_id}.png", color)
        write(DATA / "recipe" / f"{item_id}.json", json.dumps({
            "type": "minecraft:crafting_shapeless",
            "ingredients": [vanilla, "minecraft:elytra"],
            "result": {"id": f"{MODID}:{item_id}", "count": 1}
        }, ensure_ascii=False, indent=2))
    write(ASSET / "lang/en_us.json", json.dumps(en, ensure_ascii=False, indent=2))
    write(ASSET / "lang/zh_cn.json", json.dumps(zh, ensure_ascii=False, indent=2))


def test():
    checks = "\n".join(
        f'        check(helper, "{MODID}:flying_{name}_chestplate");'
        for name, *_ in MATERIALS
    )
    write(TEST_PATH / "FlyingArmorTest.java", f"""package {TEST_PKG};

import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.Item;
import net.minecraftforge.gametest.GameTest;
import net.minecraftforge.gametest.GameTestNamespace;

@GameTestNamespace("{MODID}")
public class FlyingArmorTest {{
    @GameTest
    public static void all_items_registered(GameTestHelper helper) {{
{checks}
        helper.succeed();
    }}

    private static void check(GameTestHelper helper, String id) {{
        ResourceKey<Item> key = ResourceKey.create(Registries.ITEM,
            Identifier.fromNamespaceAndPath("{MODID}", id.split(":")[1]));
        if (helper.getLevel().registryAccess().lookupOrThrow(Registries.ITEM).get(key).isEmpty()) {{
            helper.fail(id + " 未注册");
        }}
    }}
}}
""")


def main():
    clean_target()
    build_gradle()
    settings_gradle()
    shutil.rmtree(TARGET / "src/main/java", ignore_errors=True)
    shutil.rmtree(TARGET / "src/main/resources", ignore_errors=True)
    shutil.rmtree(TARGET / "src/test", ignore_errors=True)
    (TARGET / "src/main").mkdir(parents=True, exist_ok=True)
    (TARGET / "src/test").mkdir(parents=True, exist_ok=True)
    write("src/main/resources/pack.mcmeta", json.dumps({
        "pack": {"description": "Flying Armor", "pack_format": 61, "min_format": 48, "max_format": 61}
    }, indent=2))
    write("src/main/resources/META-INF/mods.toml", f"""# Forge 1.21.11 mod metadata
modLoader="javafml"
loaderVersion="[61,)"
license="MIT"

[[mods]]
modId="{MODID}"
version="1.0.0"
displayName="Flying Armor"
description="Chestplates that can fly like elytra."

[[dependencies.{MODID}]]
    modId="forge"
    mandatory=true
    versionRange="[61,)"
    ordering="NONE"
    side="BOTH"

[[dependencies.{MODID}]]
    modId="minecraft"
    mandatory=true
    versionRange="[1.21.11,1.22)"
    ordering="NONE"
    side="BOTH"
""")
    mods_toml()
    java_main()
    assets()
    test()
    print("Generated MOD workspace at", TARGET)


if __name__ == "__main__":
    main()

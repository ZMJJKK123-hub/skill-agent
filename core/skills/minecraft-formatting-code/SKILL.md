---

name: minecraft-formatting-code
description: "Minecraft Formatting Code 格式化代码（Legacy § 格式化系统、已弃用 仍可用但不推荐、Java文本系统和Bedrock Ore UI不再支持）：Usage 使用（§ 后跟字符格式化文本、十六进制数字切换颜色、Java颜色代码重置先前格式代码、Bedrock格式代码在颜色代码后仍有效、§r 重置样式）、Color Codes 颜色代码（§0-§f 黑色/深蓝/深绿/深青/深红/深紫/金色/灰色/深灰/蓝色/绿色/青色/红色/浅紫/黄色/白色、§g Minecoin金色）、Format Codes 格式代码（§k 乱码/§l 粗体/§m 删除线/§n 下划线/§o 斜体/§r 重置）、Input 输入（Windows Alt+Numpad 21/0167/Alt+Numpad+A7、Mac ⌥Option+6/⌥Option+00a7、Linux Compose so/Ctrl+Shift+U 00a7、文本组件 \u00A7）、Java 兼容性（仅标志牌可输入§ 通过粘贴 §§技巧）、Usage in Files 文件使用（server.properties motd/pack.mcmeta 使用 \u00A7 不是§、语言文件格式代码 应用到字符串、世界名称 level.dat LevelName 标签、服务器名称 servers.dat Name）。"
whenToUse: "Use when applying legacy § formatting to text, motd, world names, or language files (deprecated in favor of text components)."

---

# Formatting Codes

This article covers the older §-based formatting system (see text components for the newer system). It is deprecated in Minecraft — still usable, but not recommended; the Java text system and Bedrock Ore UI no longer support formatting codes.

Formatting codes (color codes) add style (color, bold, italic, underline, etc.) to text via the section sign `§`. In Bedrock, `§` can be typed into signs, world names, rename fields, and chat.

## Usage

Append a character after `§` to format text; hexadecimal digits switch colors. In Java, a color code resets prior format codes — `§cX§nY` shows XY underlined, `§nX§cY` shows plain XY. Use color first and repeat format codes after color changes. In Bedrock, format codes after color codes remain effective. `§r` resets the style (e.g. `§nXXX§rYYY` → XXXYYY).

### Color codes

`§0`–`§f` (black, dark blue, dark green, dark aqua, dark red, dark purple, gold, gray, dark gray, blue, green, aqua, red, light purple, yellow, white), plus `§g` (Minecoin gold; renders incorrectly on PlayStation).

### Format codes

- `§k` obfuscated (random characters keep the original character width)
- `§l` bold, `§m` strikethrough, `§n` underline, `§o` italic, `§r` reset

## Input

- Windows: Alt+Numpad 21 (CP437) or Alt+Numpad 0167; with `EnableHexNumpad`: Alt+Numpad+A7.
- Mac: ⌥ Option+6 (US); other layouts ⌥ Option+00a7.
- Linux: Compose `s` `o` or Ctrl+Shift+U 00a7.
- Mobile/consoles: various keypad paths to the `§` symbol (see wiki).
- In text components write `\u00A7` (or `\u00a7`).

Compatibility: In Java the only in-game place to enter `§` is signs, via pasting — the filter deletes `§`+one character unless the `§§` trick is used (paste `§§` then the code so `§§-a` becomes `§a` after filtering). In Bedrock, codes work in nearly all non-Ore UI text inputs.

## Usage in files

- `server.properties` `motd` and `pack.mcmeta`: use `\u00A7` instead of `§` (e.g. `\u00A75`); raw `§` gets converted to `\u00C2\u00A7` (Â§) which displays as an error.
- Language files: format codes apply to any string, e.g. `{"item.minecraft.diamond":"§dDiamond§r"}`.
- World names: edit `level.dat` `LevelName` tag (e.g. `§1R§2e§3d...`), or use a resource pack.
- Server names: edit `Name` in `servers.dat` (e.g. `§4§lMinecraft §6§l Server`).

## Trivia

- The 16 color codes nearly match the 1981 CGA palette (color 6 differs: #FFAA00 vs #AA5500).
- With fonts other than Mojangles on Bedrock, obfuscated `§k` shows as dots.
- In Classic, the format symbol was `&` instead of `§`.

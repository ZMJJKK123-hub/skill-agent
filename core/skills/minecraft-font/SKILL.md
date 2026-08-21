---

name: minecraft-font
description: "Minecraft Font 字体系统：Mojangles 字体（Minecraft Seven 7像素字形高度、默认UI字体 minecraft:default、字符宽度1-6点 ASCII 32-126 5点宽、支持 Latin/Greek/Cyrillic/Armenian/Georgian/Hebrew、字形文件 ascii.png/accented.png/nonlatin_european.png、Bedrock 使用 pre-1.13.6 Mojangles 旧字形）、GNU Unifont Unicode 字体（16x16 字形 更细笔画、Java Unifont v17.0.01 完整BMP+部分其他平面、minecraft:uniform 字体、Force Unicode Font 选项、Bedrock Unifont v5.1 部分BMP 0000-FFFF）、Unifont JP 日本字形（日语标准CJK字形、Japanese glyph variants 选项切换）、Private Use Area PUA（CSUR/UCSUR 构造语言字形 minecraft:include/unifont_pua）、SGA 标准银河字母（附魔台字体 26字母 无大小写 Command Keen 替换密码、minecraft:alt 字体）、Illageralt 恶魂字母（Mojang类SGA脚本 Minecraft Dungeons、26字母+数字+标点、minecraft:illageralt 字体）、Minecraft Ten 主标题字体（10像素字形高度）、Minecraft Five 5像素字体（粗体副标题字体）、Noto Sans 无衬线字体（Google/Adobe Source Han Sans Bedrock smooth、完整BMP+非BMP字符、日语使用 Noto Sans CJK JP）。"
whenToUse: "Use when choosing fonts for text components or understanding which characters each font renders."

---

# Font

Minecraft's UI and related sites use several fonts. (Custom fonts via resource packs: see the custom-font skill.)

## Mojangles

The signature Minecraft font ("Minecraft Seven" — 7-pixel glyph height) and the default for most UIs (Java: `minecraft:default`). Character widths 1–6 points; ASCII 32–126 are 5 points wide except a few; 1-point inter-character spacing. Supports Latin, Greek, Cyrillic, Armenian, Georgian, Hebrew consonants; other characters (e.g. Tamil, CJK) fall back to GNU Unifont. Glyphs in `ascii.png`, `accented.png`, `nonlatin_european.png`. Bedrock uses the pre-1.13.6 Mojangles (old glyphs; Ore UI's "Minecraft Seven v2" adds Greek/Cyrillic).

## GNU Unifont

The "Unicode font" for characters Mojangles lacks (CJK, full-width punctuation); 16×16 glyphs, thinner strokes. Java: Unifont v17.0.01 (more complete BMP + some other planes), font `minecraft:uniform`; the "Force Unicode Font" option renders everything in Unifont (useful for overflowing signs). Bedrock: Unifont v5.1 (partial BMP 0000–FFFF only). OpenType-dependent scripts (Tibetan, Devanagari conjuncts) can't render properly. Java files are hashed resources (`assets/minecraft/font/unifont.zip` in `.minecraft/assets/objects`); Bedrock stores glyph sheets under `resource_packs/vanilla/font/glyph_NN.png`.

### Unifont JP (Java)

Unifont JP provides Japanese-standard CJK glyphs (Unifont itself uses mainland-Chinese standard forms). Not auto-switched by language — the "Japanese glyph variants" option (default from the system locale) toggles it. v17.0.01, hashed at `assets/minecraft/font/unifont_jp.zip`.

### Private Use Area (Java)

Unifont's PUA glyphs (constructed-language characters per CSUR/UCSUR) are bundled separately: font `minecraft:include/unifont_pua` (`assets/minecraft/font/unifont_pua.zip`, v17.0.01).

## SGA

Standard Galactic Alphabet — the mysterious enchantment-table font (letters fly from bookshelves; enchantment options use it). A simple substitution cipher from Commander Keen, redesigned as a pixel font. 26 letters, no case. Glyphs in `ascii_sga.png`; Java font `minecraft:alt`.

## Illageralt

Mojang's SGA-like script (from Minecraft Dungeons; associated with illagers). 26 letters, digits, and `! ? , .`; no case. Glyphs in `asciillager.png`; Java font `minecraft:illageralt`.

## Minecraft Ten

The main-title font (10-pixel glyph height); its C is narrower and E/F middle bars shorter than the actual logo. Used by Bedrock, the launcher, and the website. 26 letters, digits, Western punctuation, some Latin; no case (all caps). 

## Minecraft Five

The 5-pixel font; its bold variant is the subtitle font.

## Noto Sans

Google/Adobe sans-serif (CJK: Source Han Sans); used in Bedrock (game files call it `smooth`). Supports the full BMP plus some non-BMP characters; used for heavy text to ease reading; Japanese language uses Noto Sans CJK JP. Ore UI falls back to Noto Sans for unsupported Mojangles characters.

## Trivia

Bedrock renders colored icon characters from the PUA (colon-wrapped source codes usable in chat/`/tellraw`). Java renders Arabic conjuncts via Arabic Presentation Forms-B (U+FE70–U+FEFF) instead of Arabic letters. Bedrock auto-strips glyph whitespace (full-width punctuation issues); the China Bedrock edition uses Unifont almost everywhere.

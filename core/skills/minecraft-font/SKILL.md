---

name: minecraft-font
description: "Fonts — Mojangles, GNU Unifont (JP, PUA), SGA, Illageralt, Minecraft Ten/Five."
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

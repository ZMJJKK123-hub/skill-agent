---
name: minecraft-custom-font
description: Custom font format — glyph providers (bitmap, reference, space, ttf, unihex).
whenToUse: Use when creating or modifying fonts via resource packs (assets/<ns>/font/*.json).
---

# Custom Font

Fonts render game text. Java Edition only.

## Font Rendering

Two storage kinds:

- **Bitmap fonts** — glyphs in bitmaps laid out on a grid; the bitmap must have a grayscale or alpha channel (pure RGB fails to load).
- **Vector fonts** — glyphs as mathematical outlines (TrueType); baked to bitmaps with FreeType.

Both are rasterized into a **256×256 font texture atlas** — glyphs must never exceed 256×256 px. Two render categories: **grayscale** (single-channel bitmaps + vector fonts; `rendertype_text*` shaders) and **color** (multi-channel bitmaps; `rendertype_text_intensity*` shaders).

Fragment handling: alpha (grayscale value for grayscale fonts) < 0.1 is discarded; < 1/255 renders fully opaque; semi-transparent fragments blend. Visual effects: bold = each glyph rendered twice (1 or 0.5 px horizontal offset); italic = top vertices skewed 25% right; underline/strikethrough = a line rendered above the text; shadow = the whole text rendered twice (offset down-right 1/0.5 px, 25% brightness, same alpha); glow = 9 renders (8 offsets forming a border + the normal text).

## Custom Fonts

Font description files: `assets/<namespace>/font/*.json`:

```json
{ "providers": [ ... ] }
```

### Glyph Providers

Common: `filter` — enable/disable by options: `jp` (matches the "Japanese glyph variants" font option) and `uniform` (matches "Force Unicode Font"); both optional, absent = always enabled.

#### Codepoint Strings

- BMP codepoints: the literal character or `\uXXXX` (4 hex digits).
- Supplementary-plane codepoints: the literal string or a surrogate pair `\uXXXX\uYYYY` (high = ⌊c/1024⌋+55232, low = c mod 1024 + 56320).

#### bitmap

`file` (required; → `assets/<ns>/textures/<path>.png`), `chars` (required — grid rows; every row must have the same codepoint count x; a w×h bitmap becomes an x×y grid of ⌊w/x⌋×⌊h/y⌋ cells, top-left aligned), `height` (default 8 — rendered glyph height; scales the source), `ascent` (required, ≤ height — baseline to glyph top; vertical offset).

Glyph edges: the right edge is found by scanning from the cell's right to left for the first non-zero grayscale/alpha pixel; the left edge is the cell edge. Rendering size = height/h0 scale; both dimensions must stay ≤256.

#### reference

`id` (required; → `assets/<ns>/font/<id>.json`): includes another font's providers (loaded once regardless of inclusion count).

#### space

`advances` (required): codepoint string → advance width in pixels (positive moves the render origin right, negative left).

#### ttf

`file` (required; → `assets/<ns>/font/<path>`), `oversample` (default 1 — resolution), `size` (default 11 — bake size; baked w/h = ⌊size×oversample⌋), `shift` (two floats −512..512: left/below offsets relative to size), `skip` (codepoint string or array — codepoints not provided by this provider).

#### unihex

`hex_file` (required — a zip containing `.hex` files), `size_overrides` (list of `{from, to, left, right}` — override glyph widths). Each `.hex` line: `<hex codepoint (4–6 digits)>:<hex glyph data (32/64/96/128 chars)>`; glyph pixel height is always 16, width = length/4; each hex digit pair = 8 pixels, 1 = opaque, 0 = transparent, row-major. Example: `0041:0000000018242442427E424242420000` (letter A, 8 px wide). The baseline sits between the second- and third-last rows; rendered glyphs are scaled down 50%.

## Built-in Glyphs

Every font has two un-replaceable built-in glyphs, always first (atlas top-left): the **missing glyph** (hollow outline, 8×5 px; used for unknown codepoints) and the **white glyph** (solid white 8×5; used for underline/strikethrough).

---

name: minecraft-text-component
description: "Minecraft Text Component 文本组件格式：Context and Parsing 上下文和解析（Static context 静态上下文 语言/键绑定、Dynamic context 动态上下文 记分板/实体/方块实体/命令存储/实体位置朝向；Pre-parse dynamic components 预解析动态组件 读取世界数据 score/selector/nbt 服务器端预解析→静态快照→不跟踪后续变化；Parse static components 解析静态组件 客户端解析静态上下文）、Basic Structure 基本结构（String form 字符串形式 {text:} 简写、List form 列表形式 拼接简写 第一个元素成为根 其余追加到extra、Compound form 复合形式 type+extra+Style tags；Inheritance 继承 树结构 extra非空为父 子继承样式标签 渲染深度优先）、Pre-parse Triggers 预解析触发器（/tellraw /title 每接收者预解析、/title 命令立即预解析、written book lectern无触发实体、sign text 立即预解析、text display entity 显示实体触发、item modifier set_lore/set_name entity触发）、Component Types 组件类型（7种：text 纯文本静态、translatable 本地化文本静态 translate+fallback+with、keybind 键绑定静态、score 记分板数据动态 name+objective、selector 实体名称动态 separator+团队前缀后缀/颜色、nbt NBT数据动态 interpret/plain+source entity/block/storage、object 精灵组件 atlas sprite/player head）、Component Styles 组件样式（color 颜色 #RRGGBB/格式化代码颜色名、shadow_color 阴影颜色 ARGB、font 字体命名空间ID、bold/italic/underlined/strikethrough/obfuscated 布尔、insertion 插入文本 Shift点击）、Click Events 点击事件（change_page 翻页、copy_to_clipboard 复制、custom 自定义网络负载、open_file 打开文件、open_url 打开URL、run_command 执行命令、show_dialog 打开对话、suggest_command 替换聊天栏）、Hover Events 悬停事件（show_entity 显示实体 名称/类型/UUID F3+H、show_item 显示物品 工具提示、show_text 显示文本）、Bedrock Edition 基岩版（仅文本显示 无交互、rawtext 列表、text/translate/score/selector 内容组件）。"
whenToUse: "Use when composing text components in commands, data packs, or resource packs (tellraw, books, signs, item names)."

---

# Text Component

Text Components (formerly "Raw JSON Text") are how Minecraft sends and displays rich text to players. They exist in NBT (serialization/persistence), SNBT (command input), and JSON (data pack registries) forms; JSON and SNBT are equivalent except for syntax.

## Context and Parsing

Components are parsed against a context into formatted text before rendering:

- **Static context** — current language, keybinds.
- **Dynamic context** — world scoreboard, entities, block entities, command storage, and the entity/position/facing triggering pre-parsing.

Parsing happens in two steps:

1. **Pre-parse dynamic components** — components reading world data (score, selector, nbt) are pre-parsed server-side into static components before sending to the client. They become a **snapshot** of the dynamic context and do not follow later changes.
2. **Parse static components** — the client resolves static components against the static context; results can re-resolve when the static context changes.

## Basic Structure (Java Edition)

Three base forms:

- **String form** — shorthand for `{text: <string>}`. Used in serialization whenever a component is a plain text component with default styles and no children.
- **List form** — shorthand for concatenation: the first element becomes the root, all remaining elements are appended to its `extra` (after any existing `extra`). Elements may mix all three forms; children are preserved verbatim. Insert `""` as the first element to prevent the first element's styles from becoming the global style.
- **Compound form** — the base format:
  - `type` — component type (usually omittable; see Component Types).
  - `extra` — child components (see Inheritance).
  - Style tags — see Component Styles.

The game only serializes/stores string and compound forms.

### Inheritance

Components form a tree; a component with non-empty `extra` is a parent. Children inherit style tags from parents (not the type or type-specific data); a child's own definition of a tag overrides the inherited value; otherwise the render environment's defaults apply. Rendering is depth-first: `{text: 'A', extra: ['B', {text: 'C', extra:['E', 'F']}, {text: 'D', extra: ['G']}]}` renders `ABCEFDG`.

### Pre-parse Triggers

- Commands: `/tellraw` and `/title` pre-parse per recipient (trigger entity = the receiving player); all other commands pre-parse immediately (trigger entity = the executing player).
- Opening a written book without `resolved` (or `resolved: false`): lectern has no trigger entity (some dynamic components misbehave); a player opening it provides the trigger entity.
- Loading/setting sign text pre-parses immediately (no trigger entity).
- Loading/setting a text display entity's `text` pre-parses with the display entity as trigger. `CustomName` is not pre-parsed on load; `selector` components create their own copy for pre-parsing.
- Item modifier `set_lore` / `set_name` with an existing `entity` uses that entity as trigger.

During pre-parsing the game walks the whole tree; depth beyond 100 is not pre-parsed. In MOTD, depth beyond 16 is replaced with `...` (parse failure → empty string).

## Component Types

Seven types (`type` values; tag name in parentheses):

- `text` (tag `text`) — plain text. Static.
- `translatable` (tag `translate`) — localized text. Static.
- `keybind` (tag `keybind`) — key binding name. Static.
- `score` (tag `score`) — scoreboard data. Dynamic.
- `selector` (tag `selector`) — entity names. Dynamic.
- `nbt` (tag `nbt`) — NBT data. Dynamic.
- `object` — sprite component. Static.

When `type` is absent, the game tries the tags in the order above (text, translate, keybind, score, selector, nbt, then sprite tags) and uses the first whose value type matches. `type` is only a strictness check — it is never saved on serialization.

### Plain Text (`text`)

`text` (required) — the string to render.

### Translatable (`translatable`)

- `translate` (required) — localization key; looked up in the current language, then `en_us`, then `fallback` if defined, else the key itself is used as the text.
- `fallback` — fallback text.
- `with` — arguments replacing `%s`/`%d`/`%f`-style placeholders (components, strings, numbers, booleans; not `null` in JSON). Non-component arguments become plain components; they inherit the parent's styles but may override them.

`%%` renders as literal `%`. If the resolved text uses unsupported format characters (when falling back), or `with` provides fewer arguments than needed, parsing fails and the found localized text is used as-is.

### Keybind (`keybind`)

`keybind` (required) — binding identifier, displayed as the current key name (e.g. `{keybind: "key.inventory"}` shows "E"). Unknown identifiers fall back to their translation name.

### Score (`score`)

- `score` (required):
  - `name` (required) — score holder: a target selector (must match exactly one entity, else pre-parse error; if none matched, the selector text is treated as a player name/UUID), a player name/UUID, or the wildcard `*` (the triggering entity).
  - `objective` (required) — the scoreboard objective.

If the holder is empty or the objective doesn't exist, the component pre-parses to an empty plain text component; otherwise the score is formatted with the objective's number format. If not pre-parsed successfully, renders empty on the client.

### Selector (`selector`)

- `selector` (required) — target selector, player name, or UUID.
- `separator` — separator between entity names; default `{text: ', ', color: 'gray'}`.

Display names are built per entity: player name (plain component); else `CustomName` (click events stripped); else `{translate: 'entity.<type id>'}`. Then team prefix/suffix (`MemberNamePrefix`/`MemberNameSuffix`), team color (`TeamColor`, skipped if `reset`), a `show_entity` hover event (type, UUID, unformatted name), an insertion event with the dash-separated UUID, and for players a `suggest_command` click event with `/tell <name>`.

If nothing matched → empty component; one match → that component; several → empty root with names and separators as children. If not pre-parsed successfully, renders the raw `selector` string.

### NBT (`nbt`)

- `nbt` (required) — NBT path (see the nbt-path skill).
- `interpret` (default `false`; must be false if `plain` is true) — whether to parse the data as text components; false outputs syntax-highlighted SNBT like `/data get`.
- `plain` (default `false`; must be false if `interpret` is true) — when `interpret` is false, output a single plain string instead of highlighted rich text.
- `separator` — separator between multiple results (default `, `; unstyled `,` when `interpret` is false).
- `source` — exactly one of `entity` (selector/name/UUID; all entity data except ID, plus `SelectedItem` for players with a selected item), `block` (block entity data at a block position; relative/local coordinates resolve against the triggering context), `storage` (command storage by namespace ID). Source detection order: entity, block, storage.

No data found → empty component. Otherwise all found values are flattened/mapped by the NBT path (e.g. two entities with `Motion` `[1d,0d,-1d]` and `[-2d,0d,2d]`: path `Motion` → 2 items; `Motion[]` → 6 items; `Motion[0]` → 2 items). With `interpret: true`, data convertible to components are used (first result becomes root, others follow with separators); unconvertible data is dropped.

### Sprite (`object`)

Renders a sprite at the component's position (replaces the character with U+FFFC; sprites are converted to 8×8 pixels in font metrics). Forcing a font on sprite components is ignored; bold/italic/obfuscated styles are ignored.

- `atlas` (tag `sprite`) — a sprite from a texture atlas: `atlas` (default `blocks`), `sprite` (required, sprite ID in that atlas), `fallback` (default `[<sprite id>]` or `[<sprite id>@<atlas id>]`).
- `player` — a player's head front texture: `player` (a resolvable game profile; string form sets `name`), `hat` (default `true` — render the hat layer), `fallback` (default `[<player name> head]` or `[unknown player head]`). Forced to fallback in MOTD.

## Component Styles

- `color` — `#RRGGBB` hex or a formatting-code color name (e.g. `yellow`); no alpha channel.
- `shadow_color` — shadow color (ARGB; stored as integer). Shadows fail to render when alpha < 0x1A (~0.1) due to shader limits.
- `font` — font namespace ID (default `minecraft:default`; fonts defined in `assets/<ns>/font/<path>.json`; missing fonts render missing glyphs).
- `bold`, `italic`, `underlined`, `strikethrough`, `obfuscated` — booleans.
- `insertion` — text inserted when Shift-clicking (chat screen only; replaces selected text or inserts at cursor).

### Click Events (`click_event`)

`action` plus per-action data:

- `change_page` — `page` (>0): flip the written book to that page (clamped). Only in the book preview screen.
- `copy_to_clipboard` — `value`: copy string. Chat and book preview.
- `custom` — `id` (custom network payload namespace ID) + `payload` (nested ≤16 levels, serialized ≤32768 bytes): sends a `custom_click_action` packet; vanilla logs it at debug level only. Chat, book preview, signs.
- `open_file` — `path`: opens a file (client-internal only; never serialized). Windows: `rundll32 url.dll,FileProtocolHandler file:<path>`; macOS: `open file:<path>`; others: `xdg-open file://<path>`. Chat and book preview.
- `open_url` — `url` (http/https only): opens a URL. Disabled if `chatLinks` is false; asks first if `chatLinksPrompt` is true. Works in death screen, chat, book preview; platform command like open_file.
- `run_command` — `command` (no leading `/` needed; must not contain `\u00a7`, `\u007f`, or chars < `\u0020`): executes the command. Signs: server-side, permission level independent of the clicker; chat/book: client-side like the chat bar. Not effective in configuration-phase dialogs.
- `show_dialog` — `dialog`: opens a dialog (namespace ID or inline definition). Chat, book preview, signs.
- `suggest_command` — `command` (same character restrictions): replaces the chat bar content. Chat only.

Click events are only effective on: death-message components in the death screen (open_url only), signs (root component; run_command/custom/show_dialog only), chat components (not hover tooltips), and book preview components.

### Hover Events (`hover_event`)

- `show_entity` — `id` (entity type ID), `name` (display name component; cannot be pre-parsed — a `selector` name shows as `@e`), `uuid` (dashed UUID string or 4-int array). Shows name/type/UUID lines; requires `advancedItemTooltips` (F3+H). Valid: death screen, chat, book preview.
- `show_item` — `id` (item ID; air if unspecified), `components` (component patch, `!id` removes), `count` (default 1). Renders like an item tooltip; respects `advancedItemTooltips`.
- `show_text` — `value` (required): the text component to display.

## Bedrock Edition

Much simpler: text display only, no interaction. Used in `/tellraw`, `/titleraw`, NPC names, written books (except title/author), signs, most rich text. `score` and `selector` work only in flowing text (chat messages, screen titles).

Format: root is a string or an object with `rawtext` (list of content components; empty list errors). Content components are defined by their required field:

- `text` — plain text (escapes allowed; newlines via `\n`).
- `translate` — localization key or format string; falls back to `en_us.lang`, then treats the value as a format string. `with` (list of plain strings, or an object whose `rawtext` provides matches) fills `%`-placeholders.
- `score` — `name` (selector, player name, fake player (`#` prefix hides it), scoreboard ID, or `*` = reader) + `objective`. Missing score hides content; `*` always shows something.
- `selector` — target selector/name/`*`; no match hides content; multiple names joined with `, `.

Parsing: children resolve first, then parent; content components with no content are ignored ("no content" ≠ "empty content" — `{"text": ""}` shows empty content and is not ignored). Multiple required fields in one content component: priority `translate` > `text` > `score` > `selector` (later duplicates of the same field override). Format strings: `%%<type>` sequential matching (s/d types are equivalent), `%%<index>` positional matching (0-based, simultaneous), `%%<index>$<type>` seen in language files but not effective in `with`.

Writing conventions: avoid nested `rawtext` lists (use `translate` or split components), avoid multiple required fields in one content component, avoid `$s`/`$d` in content that may reach format-string parsing, avoid special escape characters, and avoid displaying empty/no-content components.

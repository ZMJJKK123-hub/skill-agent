---

name: minecraft-nbt-path
description: "Minecraft NBT Path NBT路径格式：Usage 使用（路径 node.node...node 点分隔节点、节点应用于当前标签集每个元素、选中子标签形成新集、最终集为路径结果、/data get 要求结果集恰好一个标签、/data modify 允许集大于一）、6 Node Types 6种节点类型（Root compound node {} 选择根标签、Named tag node foo 选择命名子标签 含./空白/引号时需引号 'a.b'/'a b'/\"\\\"te's't\" 引号嵌套转义、Compound matching node foo{bar:\"baz\"} 选择foo子标签仅当复合标签bar等于baz、List index node [0] 选择索引0元素 [-1] 最后一个元素、List index range node [0..2] 选择0到2包含元素 [..2]/[1..] 开放范围、List matching node [{baz:5b}] 选择所有匹配结构的复合列表元素）、Dot Omission 省略点（[]前点可省略 tag2.[] == tag2[]）、Semantics Examples 语义示例（tag2 列表、tag2.[] 三个复合、tag2.[].foo 每个元素foo值、foo.bar[] 所有元素、foo.bar[].baz 所有复合元素的baz、foo.bar[{baz:5b}] 所有baz:5b的复合元素）、Full Example 完整示例（/data get block Items[1].components.minecraft:written_book_content.pages[3].raw 遍历路径）。"
whenToUse: "Use when writing NBT paths in /data, /execute store, or NBT component predicates."

---

# NBT Path

NBT paths specify one or more tags in an NBT tree. Java Edition only.

## Usage

A path is `node.node....node` (dots separate nodes; some dots may be omitted, see below). Each node selects child tags from the current **tag set** (initially just the root). Nodes apply to every element of the set; all selected children form the new set. The final set is the path's result.

- `/data get ...` (and similar) requires the result set to have exactly one tag.
- `/data modify ...` allows sets larger than one.

## Nodes

Six node types (the root compound node must be first; others arrange freely):

1. **Root compound node** — `{}` selects the root tag (if compound).
2. **Named tag node** — `foo` selects the child tag named `foo`. Quote the name when it contains `.`, whitespace, or quotes: `'a.b'`, `'a b'`, `'"name"'`, `"\"te's't"`. Quoting: use `'...'` or `"..."`; embedded quotes must be escaped (e.g. `"\"te's't"`).
3. **Compound matching node** — `foo{bar:"baz"}` selects the `foo` child only if it is a compound whose `bar` equals `"baz"`; a bare `{foo:4.0f}` at path start selects the root only if `foo` is `4.0f` (usable mid-path too: `foo{bar:"baz"}.bar`).
4. **List index node** — `[0]` selects the element at index 0 (0-based); `[-1]` selects the last element (negative indexes count from the end).
5. **List index range node** — `[0..2]` selects elements 0 through 2 inclusive (ranges can be open-ended: `[..2]`, `[1..]`).
6. **List matching node** — `[{baz:5b}]` selects all list elements that are compounds matching the given structure.

Dots before `[`-style nodes can be omitted: `tag2.[]` == `tag2[]`.

## Semantics Examples

Given `{tag1:1b, tag2:[{foo:0},{foo:[]},{foo:{}}]}`:

- `tag2` → the list `[{foo:0},{foo:[]},{foo:{}}]`.
- `tag2.[]` → three compounds.
- `tag2.[].foo` → `0`, `[]`, `{}` (each applied to every element).
- `foo.bar[]` — all elements of `bar`; `foo.bar[].baz` — the `baz` children of all compound elements; `foo.bar[{baz:5b}]` — all compound elements having `baz:5b`.

## Full Example

`/data get block ~ ~ ~ Items[1].components.minecraft:written_book_content.pages[3].raw` walks: `Items` → `[1]` (second item) → `components` → `minecraft:written_book_content` → `pages` → `[3]` (fourth page) → `raw`. The same path works with `/data modify ... set value ...` for editing (e.g. changing the author or prepending a page).

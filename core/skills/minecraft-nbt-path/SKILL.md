---
name: minecraft-nbt-path
description: NBT path format — the 6 node types, tag-set semantics, quoted names, mixed-path examples.
whenToUse: Use when writing NBT paths in /data, /execute store, or NBT component predicates.
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

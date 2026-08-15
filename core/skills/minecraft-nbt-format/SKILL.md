---

name: minecraft-nbt-format
description: "NBT format — tag types, storage/network formats, SNBT/JSON conversion."
whenToUse: "Use when working with NBT at the binary level, /data commands, or NBT matching in selectors."

---

# NBT Format

NBT (Named Binary Tag) is a tree data structure of named binary tags used to store and transfer game data. Java Edition unless noted.

## Structure

Each tag (except End) = tag ID byte + tag name (unsigned/signed short length + Modified UTF-8 bytes) + payload. The End tag is a single ID byte.

### Tag Types

13 types (counting End): `End` (0), `Byte` (1), `Short` (2), `Int` (3), `Long` (4), `Float` (5), `Double` (6), `Byte Array` (7), `String` (8), `List` (9, homogeneous element type), `Compound` (10), `Int Array` (11), `Long Array` (12).

### Storage Format

An NBT file is one root Compound (or List) holding a single child; may be uncompressed, GZip, or Zlib. Java: big-endian, fixed-width. Bedrock: little-endian, fixed-width, strings as raw UTF-8; `level.dat` has an 8-byte header (4-byte little-endian version + 4-byte NBT byte count) before the uncompressed root.

### Transfer Format

Streamed, uncompressed. Java: the root compound's name (length + string) is omitted — the root tag ID is followed directly by the payload. Bedrock: same tag structure as storage but with varint encodings: Int and Long use zigzag VarInt (1–5 / 1–10 bytes); Byte/Short/Float/Double unchanged; String length is an unsigned VarInt followed by raw UTF-8; ByteArray/IntArray/List length fields are zigzag VarInts, IntArray elements too. Compound internals are identical in both formats (each value encoded per the rules above).

## Conversion

### Program Objects

Runtime data lives in program objects, not NBT; conversion happens when saving/loading/transferring or when commands modify data. Conversion rules are type-specific (some data is intentionally not written to NBT).

### SNBT

SNBT is the text intermediary between NBT and players (see the snbt-format skill). SNBT→NBT: SNBT has extra tag forms (e.g. `true`/`false`, `1ub`, quoted/typed forms) that convert to NBT tags. NBT→SNBT: each tag picks a fixed representation. Chat output further converts to syntax-colored text components, truncating long lists/arrays/compounds with `<...>`.

### JSON

JSON is incompatible with NBT (different syntax/base types); embedding JSON in NBT usually means storing the JSON text in a string. Where game data is stored as JSON but needs NBT (e.g. biomes), the game converts with information loss. JSON→NBT may fail (`null` values, heterogeneous lists); NBT→JSON loses numeric type info.

## Modifying Objects via NBT (Java)

Before modifying an entity/block entity, the game converts the passed SNBT/JSON to NBT, then applies only usable properties (e.g. block entity coordinates can't be changed). Unknown properties are dropped (`nonExist` on an entity). Type coercion for properties:

- Namespace IDs: bare strings convert per string→ID rules.
- Booleans: numeric values floor to a byte (non-zero → `1b`); other types → `0b`.
- Numeric properties: mismatched numeric types convert (floats floor for integer properties); non-numeric → 0.
- Strings: non-strings → empty string.
- Lists/arrays: wrong types → empty list/array.
- Compounds: non-compounds → empty compound.

## Testing NBT Tags (Java)

When testing (e.g. `@e[nbt={...}]`), the provided NBT is checked against a re-derived NBT object of the target: **partial matching** — the target passes if it contains the provided tags; list matching ignores order and count (elements must all exist; an empty list only matches an empty list); **arrays require exact match** (same length/order). Tag names and data types must match exactly (`1d` ≠ `1`, `[L;1L,3L]` ≠ `[L;3L]`).

Examples with `Pos: [1d,2d,3d], data:{tag1:{name:test}}`:

- `{data:{}}` ✓ (the compound `data.tag1` exists)
- `{Pos:[2d,3d,1d]}` ✓ (list order ignored)
- `{Pos:[1d]}` ✓ (element exists)
- `{Pos:[]}` ✗ (empty list ≠ non-empty)

SNBT→NBT conversion still applies to the provided test value (`true`/`1ub` test as `1b`), but object-modification conversions do NOT (e.g. `{Item:{id:stone}}` won't match an item entity; you must write `"minecraft:stone"`).

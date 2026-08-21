---

name: minecraft-snbt-format
description: "Minecraft SNBT Format SNBT格式（Stringified Named Binary Tag NBT文本形式、/data get 打印语法高亮SNBT、nbt文本组件类型也可输出高亮SNBT）：Data Types 数据类型（Numbers 数字：下划线分隔数字 不能在开头/结尾；Floats 无后缀十进制为double 科学记数法 NaN/Inf不支持；Integers 无后缀为int 十六进制0x/二进制0b前缀 除0外不能以0开头；Booleans 布尔 0/1 true/false→1b/0b）、Type Suffixes 类型后缀（b byte/s short/i int/l long/f float/d double 可选前缀 s/S有符号 u/U无符号 有符号补码存储）、Strings 字符串（引号双引号/单引号 同引号内需转义、无引号 仅0-9/a-zA-Z/./_/+/- 不能以数字/.开头/+/−开头 true/false解析为布尔、转义序列 \"'/\\\/\b\f\n\r\t \uXXXX Unicode）、Arrays 数组 [B;...]/[I;...]/[L;...] 无后缀取数组类型 小类型扩展）、Lists 列表（异构元素允许 尾部逗号允许 嵌套≤512层）、Compounds 复合标签（键值映射 尾部逗号允许 嵌套≤512层）、SNBT Operations SNBT操作（函数式语法 parse时计算 不能保留或高亮：bool(arg) 布尔转换、uuid(str) UUID字符串→int数组）、Conversion 转换（SNBT永不直接存储→转换为NBT→程序对象）。"
whenToUse: "Use when writing SNBT in commands, NBT components, or .snbt files."

---

# SNBT Format

SNBT (Stringified Named Binary Tag) is the text form of NBT, used in data-modifying commands and `.snbt` files (UTF-8). It resembles NBT but is not identical to it. `/data get` prints syntax-highlighted SNBT ("pretty-printed"); the `nbt` text component type can also output highlighted SNBT.

## Data Types

### Numbers

Underscores may separate digits (`0b10_01`, `0xAB_CD`, `1_2.3_4__5f`, `1_2e3_4`) but not at the start/end.

- **Floats** (IEEE 754): no-suffix decimals are doubles (`1.2`). Fractional or integer parts may be omitted (`.1`, `1.`). Scientific notation allowed (`1.2e3`, `12000e-1` → 1200.0). Out-of-range (→ infinity) values like `1e1000` are invalid. NaN/Inf/hex floats unsupported.
- **Integers**: no-suffix integers are ints (`123`). Hex `0x` and binary `0b` prefixes allowed (`0xCAFE`, `0b101`). Integers (except 0) must not start with `0` (octal ambiguity).
- **Booleans**: SNBT booleans are bytes limited to 0/1; `true`/`false` (case-insensitive) → 1b/0b.

### Type Suffixes

First letters, case-insensitive: `b` byte, `s` short, `i` int, `l` long (floats: `f`, `d`). Optionally prefixed with `s`/`S` (signed) or `u`/`U` (unsigned) — e.g. `123sb` = signed byte 123. Signed values store as two's complement; the prefix only affects parse ranges (`240sb` fails; `240ub` == `-16sb`). Decimal numbers default to signed; hex/binary default to unsigned. Because `b` is a valid hex digit, hex bytes need the explicit prefix (`0x11ub`, `0x11sb`).

### Strings

- Quoted: `"test"` or `'test'`; the same quote inside must be escaped (`"\"test"` valid, `""test"` invalid).
- Unquoted: `test` — only `0-9`, `a-zA-Z`, `.`, `_`, `+`, `-`; must not start with a digit, `.`, `+`, or `-` (numeric conflicts); `true`/`false` parse as booleans.
- Escape sequences in quoted strings: `\"`, `\'`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\uXXXX` (Unicode escapes).

### Arrays

`[B;...]`, `[I;...]`, `[L;...]`: values without suffixes take the array's type (`[B;1,2]` == `[B;1b,2b]`); smaller types are widened (`[I;1b,2s,3]` == `[I;1i,2i,3i]`).

### Lists

Heterogeneous elements allowed (`['', {text:"hello"}, 123]`; some contexts still require homogeneity). One trailing comma allowed after a valid element (`[1,2,]`; `[,]`, `[1,,]` invalid). Nesting ≤ 512 levels.

### Compounds

Key-value maps (`{a:b}`). One trailing comma allowed (`{a:b,}`; `{,}`, `{a:b,,}` invalid). Nesting ≤ 512 levels.

## SNBT Operations

Function-like syntax `<name>(<arg1>, ...)` evaluated at parse time (cannot be preserved or syntax-highlighted):

- `bool(arg)` — exactly one numeric or boolean argument: booleans pass through; numbers → true if non-zero. `bool(true)` → true; `bool(0)` → false; `bool("foo")` → error.
- `uuid(str)` — one dash-formatted UUID hex string → int array: `uuid("f81d4fae-7dec-11d0-a765-00a0c91e6bf6")` → `[I; -132296786, 2112623056, -1486552928, -920753162]`.

## Conversion

SNBT is never stored directly — it converts to NBT, then to program objects (see the nbt-format skill).

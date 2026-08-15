---
name: minecraft-uuid
description: UUID representations in Minecraft: formats, int-array, version 4 usage.
whenToUse: Use when reading or writing UUIDs in commands, NBT, or datapacks.
---

# UUIDs in Minecraft

A Universally Unique Identifier (UUID) is a 128-bit number used by Minecraft to distinguish object instances.

## Representations

- **Hyphenated hexadecimal** (RFC 9562): `8-4-4-4-12` groups, e.g. `f81d4fae-7dec-11d0-a765-00a0c91e6bf6`. Leading zeros per group may be omitted (`00000001-0002-0003-0004-000000000005` = `1-2-3-4-5`).
- **Hexadecimal**: same without hyphens; zeros cannot be omitted.
- **Most/Least**: high/low 64 bits as two longs (e.g. `UUIDMost`/`UUIDLeast`); pre-1.16 only, fully replaced by the int-array format.
- **Int array**: 4 32-bit numbers, e.g. `[I;-132296786,2112623056,-1486552928,-920753162]`.

## Versions and variants

UUIDs have 5 versions (1/2: time + MAC; 3/5: string hashes; 4: fully random). The version nibble sits at position A in `xxxxxxxx-xxxx-Axxx-Bxxx-xxxxxxxxxxxx`. The B position is the variant: `0xx` (Apollo NCS), `10x` (RFC 4122, "variant 1"; Java "variant 2"), `110` (old Microsoft, Java "variant 6"), `111` (reserved, Java "variant 7").

## In Minecraft

Java Edition uses version 4, variant 1 (RFC) UUIDs — fully random except the metadata — generated via `UUID.randomUUID()`.

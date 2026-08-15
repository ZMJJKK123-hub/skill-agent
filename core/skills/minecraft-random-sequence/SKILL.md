---

name: minecraft-random-sequence
description: "Random sequences save format, seeding (Xoroshiro128++), /random reset."
whenToUse: "Use when understanding random sequence seeding, loot randomness, or /random reset."

---

# Random Sequences

This content applies only to Java Edition.

Random sequences provide controllable randomization via random number generator sequences.

## Storage format

File: `<save root>/data/minecraft/random_sequences.dat` (GZip NBT):

- Root tag
  - `data` (compound, required):
    - `include_sequence_id` (bool): whether the sequence namespace ID participates in seeding; modifiable by `/random reset *`; absent = `true`.
    - `include_world_seed` (bool): whether the world seed participates; absent = `true`.
    - `salt` (int): salt for initialization; absent = 0.
    - `sequences` (compound, required): created sequences.
      - `<namespace ID>` (compound): one sequence with `source` (long array, required): seed low 64 bits + high 64 bits.
  - `DataVersion` (int): absent = 1343 (Java 1.12.2).

## Creating sequences

Parameters: identifier, worldSeed, salt. The game uses Xoroshiro128++ with a 128-bit seed:

```java
long initialSeed = salt;
if (include_world_seed) initialSeed ^= worldSeed;
long unmixedLo64 = initialSeed ^ 0x6A09E667F3BCC909L;
long unmixedHi64 = unmixedLo64 + 0x9E3779B97F4A7C15L;
```

If `include_sequence_id`, the MD5 of the identifier is XORed into both halves. Then both halves are mixed with `mixStafford13` (`(l ^ l>>>30) * 0xBF58476D1CE4E5B9L`, then `(l ^ l>>>27) * 0x94D049BB133111EBL`, then `l ^ l>>>31`). A zero seed is replaced with low −7046029254386353131L / high 7640891576956012809L.

## Behavior

Missing/incomplete files initialize with `include_sequence_id=true`, `include_world_seed=true`, `salt=0`. Each use consumes and updates the sequence. Most loot table calculations use random sequences (block drops, mob drops, fishing, piglin bartering); world-gen loot chests are directly seed-controlled instead.

`/random reset` resets a sequence with the given parameters; `/random reset *` resets all and syncs parameters into the file.

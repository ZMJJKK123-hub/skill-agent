---
name: minecraft-damage-type
description: Damage type definition JSON: DAMAGE_TYPE registry, death messages, scaling, sounds.
whenToUse: Use when writing datapack damage_type definitions or custom death messages and damage scaling.
---

# Damage Types

This content applies only to Java Edition.

Damage type definition files are the data-driven definitions of damage types in datapacks.

## Definition format

Damage types use the `DAMAGE_TYPE` registry; the datapack path is `damage_type` (definitions in `data/<namespace>/damage_type`, tags in `data/<namespace>/tags/damage_type`).

Definition files use JSON with the following structure:

- JSON file root object
  - `death_message_type` (string, default `default`): death message behavior (see below).
  - `effects` (string, default `hurt`): sound played when a player takes this damage (see below).
  - `exhaustion` (float, required): hunger exhaustion added to players who actually lose health.
  - `message_id` (string, required): death message translation key (see below).
  - `scaling` (string, required): difficulty scaling behavior (see below).

## Definition behavior

Damage type data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. Built-in `DAMAGE_TYPE` entries cannot be removed, or the game crashes.

### Death messages

With `death_message_type: default` (the default):

- With an entity source (e.g. mob attack or its arrow): check whether the mob's main hand holds a named item (with `custom_name`).
  - If the source is not a mob, or the mob holds no named item: `death.attack.<msgId>` with parameters [victim name, direct damage dealer name].
  - Otherwise: `death.attack.<msgId>.item` with a third parameter [item name].
- Without an entity source, but the victim was hurt by a mob within 100 ticks (5 s): `death.attack.<msgId>.player` with [victim name, last attacker name].
- Otherwise: `death.attack.<msgId>` with [victim name].

With `fall_variants`: fall death messages are used, independent of `msgId`.

With `intentional_game_design`: `death.attack.<msgId>.message` with [victim name, `death.attack.<msgId>.link` styled as a link].

### Damage scaling

`scaling` values:

- `always`: damage is always affected by difficulty.
- `never`: damage is never affected by difficulty.
- `when_caused_by_living_non_player`: affected only when the source is a mob.

When affected (base damage d):

- Peaceful: 0.
- Easy: min{0.5d+1, d}.
- Normal: d.
- Hard: 1.5d.

### Hurt sounds

When a player takes damage without post-hit immunity, the sound determined by `effects` plays at the player's position.

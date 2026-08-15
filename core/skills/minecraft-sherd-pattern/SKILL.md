---
name: minecraft-sherd-pattern
description: Decorated pot pattern definition JSON: DECORATED_POT_PATTERN registry.
whenToUse: Use when writing datapack decorated_pot_pattern definitions or custom pot patterns.
---

# Decorated Pot Pattern Definitions

This content applies only to Java Edition. This page contains content from an upcoming update (Java Edition 26.3 development versions).

Decorated pot patterns define the pattern types usable on decorated pots. Definition files are their data-driven definitions in datapacks.

## Definition format

Decorated pot patterns use the `DECORATED_POT_PATTERN` registry; the datapack path is `decorated_pot_pattern`, so definitions live in `data/<namespace>/decorated_pot_pattern`, and tags in `data/<namespace>/tags/decorated_pot_pattern`.

Definition files use JSON with the following structure:

- JSON file root object
  - `asset_id` (string, required): (namespace ID) texture used by the pattern, rendered from `assets/<namespace>/textures/entity/decorated_pot/<path>.png`.

## Definition behavior

Decorated pot pattern data is loaded only once at server startup; `/reload` does not reload it — a server restart is required.

When rendering a pot's sides, the game reads each face's item: if absent or without a `provides_pottery_pattern` component, the face renders plain (`minecraft:decorated_pot_side`); otherwise it renders the sprite of the pattern specified by the component.

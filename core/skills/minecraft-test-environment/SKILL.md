---
name: minecraft-test-environment
description: Test environment definition format — environment types and batch behavior.
whenToUse: Use when authoring test environment JSON files for game tests.
---

# Test Environment

Test environments are the world test environments in which test instances run. Java Edition only.

## Definition Format

Registry `TEST_ENVIRONMENT`, data pack path `test_environment` (files in `data/<namespace>/test_environment/`; tags in `tags/test_environment/`).

`type` one of:

- `all_of` — runs all `definitions` (recursive list, by ID or inline) on enter/exit in order.
- `clock_time` — sets a world `clock` to `time` (≥0) on enter, restores on exit.
- `difficulty` — sets the world `difficulty` (`peaceful`/`easy`/`normal`/`hard`) on enter, restores on exit (even when locked).
- `function` — runs `setup` / `teardown` functions on enter/exit.
- `game_rules` — sets `rules` (game rule ID → value) on enter, restores on exit.
- `timeline_attributes` — adds `timelines` (IDs) to the server environment attributes on enter, removes on exit.
- `weather` — sets `weather` (`clear`/`rain`/`thunder`, each 100000 ticks) on enter, restores the cycle on exit.

## Behavior

Definitions load once at server startup (restart required). Every test instance must run inside its environment. Tests run in batches; a batch shares one environment. When a batch finishes, the game checks whether the next batch's environment is identical (same environment object, not equal contents): if not, it exits the old and enters the new; if identical, it continues without switching. After the last batch, the game exits the last-entered environment.

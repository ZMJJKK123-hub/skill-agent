---

name: minecraft-test-instance
description: "Test instance definition format: environment types, test flow (block-based and function tests), multi-run behavior with max_attempts and required_successes, structure placement, and rotation options."
whenToUse: "Use when authoring test instance JSON files for automated game tests."

---

# Test Instance Definition

Test instances are runnable tests defining a single test's basic info (the block that runs them is the test instance block). Java Edition only.

## Definition Format

Registry `TEST_INSTANCE`, data pack path `test_instance` (files in `data/<namespace>/test_instance/`; tags in `tags/test_instance/`).

- `environment` (required) — the test environment (a definition or inline): `type` one of:
  - `all_of` — runs all `definitions` (recursive) on enter/exit in order.
  - `clock_time` — sets a world `clock` to `time` (≥0) on enter, restores on exit.
  - `difficulty` — sets the world `difficulty` (`peaceful`/`easy`/`normal`/`hard`) on enter, restores on exit (works even when locked).
  - `function` — runs `setup` and `teardown` functions (IDs).
  - `game_rules` — sets `rules` (game rule ID → value) on enter, restores on exit.
  - `timeline_attributes` — adds `timelines` (IDs) to the server environment attributes on enter, removes on exit (other timeline properties ignored).
  - `weather` — sets `weather` (`clear`/`rain`/`thunder`, each 100000 ticks) on enter, restores the weather cycle on exit.
- `manual_only` (default false) — manual tests can't run in the test server.
- `max_attempts` (>0, default 1) — max single-test runs (see multi-run behavior).
- `max_ticks` (required, >0) — per-run timeout (fails on exceeding).
- `padding` (0–128, default 0) — structure placement offset (test block origin at `[padding, padding+1, padding+1]`).
- `required` (default true) — whether the whole test suite must pass this instance.
- `required_successes` (>0, default 1) — passes required for the instance to pass.
- `rotation` (default `none`) — structure rotation (`none`/`clockwise_90`/`180`/`counterclockwise_90`).
- `setup_ticks` (≥0, default 0) — ticks to wait after structure placement before the test starts.
- `sky_access` (default false) — if false, a barrier ceiling covers the structure.
- `structure` (required) — the structure template used (re-placed before every run).
- `type` (required) — `block_based` (test with the structure's test blocks) or `function` (calls a built-in test function; `function` field = TEST_FUNCTION registry ID; vanilla ships only `always_pass`, which passes immediately).

## Behavior

Definitions load once at server startup (restart required).

### Single Test

From structure placement to result: place the test instance block, force-load the area, clear all entities in the structure bounds, place the structure in strict mode, wrap it in barriers (unless sky_access), clear scheduled ticks/block events, then verify the environment. Wait `setup_ticks`, then run: exceeding `max_ticks` → timeout failure; any exception → failure without further actions; clean completion → pass (non-player entities in the bounds are removed).

### Block-Based Tests

Exactly one start-mode test block is required (else immediate failure). On start it fires a first-order NC update core and logs. Each tick, in order: (1) an accept-mode test block triggered → pass; (2) any fail-mode test block triggered → fail with its error message; (3) log-mode test blocks triggered → log their messages.

### Function Tests

Behavior fully defined by code (`success`/`fail`).

## Multi-Run Behavior

With `max_attempts` A and `required_successes` S: the instance passes as soon as s reaches S within A runs; otherwise it fails after A runs. A < S → always fails; A == S → every run must pass.

When run via `/test` with `[<numberOfTimes>]` ≠ 1, that N replaces max_attempts/required_successes: with `[<untilFailed>]` false, run N times (N=0 = infinite); true — stop on the first failure or after N runs (N=0 = only failure stops it).

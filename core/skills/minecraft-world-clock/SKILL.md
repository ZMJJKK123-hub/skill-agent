---

name: minecraft-world-clock
description: "World clock definition format: WORLD_CLOCK registry, time markers, /time."
whenToUse: "Use when understanding world clocks, time markers, or /time command behavior."

---

# World Clocks

This content applies only to Java Edition.

World clocks (clocks) manage different world clock instances. Definition files are their data-driven definitions in datapacks.

## Definition format

World clocks use the `WORLD_CLOCK` registry; the datapack path is `world_clock` (definitions in `data/<namespace>/world_clock`, tags in `data/<namespace>/tags/world_clock`). Definition files are empty JSON objects `{}`.

## Definition behavior

World clock data is loaded only once at server startup; `/reload` does not reload it — a server restart is required.

### World clock behavior

A world clock itself carries no data; the game distinguishes clocks by ID. Each clock holds an internal time that increments every tick and can be paused; it is managed by `/time`. With the `advance_time` game rule `false`, clocks do not advance even when unpaused. Each dimension gets its world clock from its dimension type (default for `/time`, and time markers per the used timelines). Each timeline computes environment attribute tracks from its clock. Save run time (GameTime) is not managed by clocks.

### Time markers

Time markers name specific clock times. They are defined in timelines' `time_markers` and registered to the timeline's clock at startup. Usable in `/time`. Game-defined markers: `wake_up_from_sleep` (time after sleeping; absent = no time change on waking) and `roll_village_siege` (zombie siege check time; absent = no sieges).

## Built-in clocks

- `overworld`: used by the Overworld; all built-in timelines use it. Markers (from the `day` timeline): `day` 1000, `noon` 6000, `night` 13000, `midnight` 18000, `wake_up_from_sleep` 0 (hidden in `/time`), `roll_village_siege` 18000 (hidden). Also used for regional difficulty (0 without the clock) and fixed debug worlds (server crashes without it; no `noon` marker = no time changes).
- `the_end`: used by the End for end sky flash timing.

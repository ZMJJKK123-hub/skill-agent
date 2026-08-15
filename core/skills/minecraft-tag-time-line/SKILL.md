---
name: minecraft-tag-time-line
description: Timeline tags and their members, used in dimension type definitions to specify active timelines.
whenToUse: Use when querying or writing timeline tags for dimension type definitions.
---

# Timeline Tags

This content applies only to Java Edition.

Timeline tags are groups of timelines.

## Usage

In dimension type definition files, timeline tags specify which timelines are active for that dimension type. See the environment attributes tutorial for an example file.

## Tag list

### `#in_end`

Timelines active in the End:

- `#universal`

### `#in_nether`

Timelines active in the Nether:

- `#universal`

### `#in_overworld` (4 entries)

Timelines active in the Overworld:

- `#universal`
- `day`
- `moon`
- `early_game`

### `#universal`

Timelines active in all dimensions:

- `villager_schedule`

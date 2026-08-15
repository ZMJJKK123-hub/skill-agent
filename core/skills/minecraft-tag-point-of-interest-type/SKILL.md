---

name: minecraft-tag-point-of-interest-type
description: "Point of interest (POI) type tags and their members, used when writing datapacks or custom POIs."
whenToUse: "Use when referencing POI type tags (acquirable_job_site, bee_home, village etc.)."

---

# Point of Interest (POI) Type Tags

This content applies only to Java Edition.

POI tags are groups of point of interest types.

## Usage

POI tags are used internally by the game for fast location lookup, similar to POIs. They can also be located with the `/locate poi` command.

## Tag list

### `#acquirable_job_site` (13 entries)

Points where villagers can acquire a profession:

- `armorer`
- `butcher`
- `cartographer`
- `cleric`
- `farmer`
- `fisherman`
- `fletcher`
- `leatherworker`
- `librarian`
- `mason`
- `shepherd`
- `toolsmith`
- `weaponsmith`

### `#bee_home` (2 entries)

Bee habitats:

- `beehive`
- `bee_nest`

### `#village` (3 entries)

POIs a village must have:

- `#acquirable_job_site`
- `home`
- `meeting`

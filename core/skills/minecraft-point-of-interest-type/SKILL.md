---
name: minecraft-point-of-interest-type
description: POI mechanism: POI types, claiming, retrieval, and vanilla usages.
whenToUse: Use when understanding POI mechanics for villages, job sites, or bee behavior.
---

# Points of Interest (POI)

This content applies only to Java Edition.

Points of interest (POIs) are the game's mechanism for quickly finding specific block categories and counting claimed blocks. POI types are hardcoded (modifiable only via mods).

Each POI type has: matched block states (which blocks create/remove the POI), a max claim count, and a claim range. POI types can carry tags; most lookups actually use POI type tags.

## Mechanics

Placing/breaking a matching block creates/removes the POI. Retrieval is efficient because POIs are stored per sub-chunk (16×16×16) and only rare blocks carry types.

Claiming: a POI's claimable count is set to the type's max at creation; claiming/unclaiming adjusts it; at 0 it cannot be claimed. POIs do not record their claimer. Villagers claim `home` POIs when breeding (for babies) and claim job sites.

## Usages

- **Villages**: a position is in a village iff a claimed POI with the `village` tag exists within a 3×3×3 sub-chunk range. Cats need >4 claimed `home` POIs within 48 blocks; wandering traders spawn near `meeting` POIs within 48 blocks; raids compute their center from claimed `village`-tagged POIs within 64 blocks.
- **Nether portals**: create `nether_portal` POIs; teleporting checks for the nearest one within Chebyshev distance 128 and reuses it.
- **Bees**: home to `bee_home`-tagged POIs.
- **Lightning rods**: create `lightning_rod` POIs; lightning bolts spawn at the nearest within 128 blocks.
- **Lodestones**: create `lodestone` POIs; lodestone compasses check the bound position's POI each tick.

## Storage

POI files are region files under `<dimension root>/poi`.

---

name: minecraft-jukebox-song
description: "Jukebox song definition JSON fields and playback behavior for datapack-custom music discs."
whenToUse: "Use when writing jukebox_song definitions or understanding jukebox playback."

---

# Jukebox Songs

This content applies only to Java Edition.

A jukebox song determines the music played when an item is inserted into a jukebox. Jukebox song definition files are their data-driven definitions in datapacks.

## Definition format

Jukebox songs use the `JUKEBOX_SONG` registry; the datapack path is `jukebox_song`, so all definitions must be in `data/<namespace>/jukebox_song`, and tags in `data/<namespace>/tags/jukebox_song`.

Definition files use JSON with the following structure:

- JSON file root object
  - `comparator_output` (integer): (0≤value≤15) the redstone comparator signal strength emitted while the jukebox plays this song.
  - `description` (string or compound tag or array): (text component) the song name shown in tooltips.
  - `length_in_seconds` (single-precision float): (value>0) the song duration in seconds. The game converts this at TPS 20 into game ticks and adds 20 extra ticks as the final duration. This value may differ from the sound event's length; only this value controls when the jukebox stops.
  - `sound_event` (string or compound tag or array): the sound event played. This sound ignores client-side propagation distance.

## Definition behavior

Jukebox song data is loaded only once at server startup; `/reload` does not reload it — a server restart is required.

When a jukebox receives an item stack with the `jukebox_playable` item stack component, the game reads the jukebox song from the component and plays it. If the referenced song does not exist, nothing happens.

The music belongs to the `record` (jukebox/note block) sound category: volume 4, pitch 1, plays immediately with linear volume attenuation. The furthest distance a player can hear a music disc is the referenced `sound_id`'s `attenuation_distance` multiplied by the volume of 4 (64 blocks by default); the sound event's `range` does not participate in sound calculation. The jukebox sends playback as a world event, so sound event propagation distance is ignored.

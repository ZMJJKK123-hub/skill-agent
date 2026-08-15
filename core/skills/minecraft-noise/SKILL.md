---
name: minecraft-noise
description: Noise definition JSON: NOISE registry, octaves/amplitudes/normalize, vanilla usages.
whenToUse: Use when writing datapack worldgen noise definitions.
---

# Noise

This content applies only to Java Edition.

Noise is the technical concept the game uses to convert coordinates into values. Noise definition files are their data-driven definitions in datapacks.

## Definition format

Noise uses the `NOISE` registry; the datapack path is `worldgen/noise` (definitions in `data/<namespace>/worldgen/noise`, tags in `data/<namespace>/tags/worldgen/noise`).

Definition files use JSON with the following structure:

- JSON file root object
  - `firstOctave` / `base_octave` (int, required): the main octave. With `legacy_random_source` in noise settings, must be ≤1; otherwise unrestricted.
  - `amplitudes` / `amplitude_modifiers` (list, required): amplitude list `{a0,a1,...,an}`; sub-noise i has frequency 2^(i+o) (o = firstOctave) and amplitude 2^(n−i)·ai/(2^(n+1)−1); the sum yields total noise. With `legacy_random_source`, the list length must be ≤1−o. If `amplitude_modifiers` is used instead, its length must equal `octave_count` (default `1.0` per octave).
  - `base_amplitude` (float, required): scale factor for the noise output; cannot be negative.
  - `octave_count` (int, required): octaves to sample, 1–32 inclusive.
  - `normalize` (bool/string, default `true`): output normalization. `true`: `base_amplitude` is the expected amplitude (99.7% of samples within ±base_amplitude). `false`: base amplitude is the first octave's amplitude. `"legacy"`: previous format behavior.

## Definition behavior

Noise data is loaded only once at server startup; `/reload` does not reload it — a server restart is required. Noise can be referenced by density functions or surface rules for coordinate-based random values.

Hardcoded vanilla usages:

- `minecraft:surface` / `minecraft:surface_secondary`: surface rule thickness
- `minecraft:clay_bands_offset`: badlands terracotta bands
- `minecraft:badlands_pillar` / `_roof` / `minecraft:badlands_surface`: eroded badlands pillars
- `minecraft:iceberg_pillar` / `_roof` / `minecraft:iceberg_surface`: icebergs in frozen oceans

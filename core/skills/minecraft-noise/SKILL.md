---

name: minecraft-noise
description: "Minecraft Noise 噪声定义：NOISE 注册表、data/<namespace>/worldgen/noise/ 数据包路径、tags/worldgen/noise/ 标签、JSON 格式（firstOctave/base_octave 主八度 int、amplitudes/amplitude_modifiers 振幅列表 子噪声频率 2^(i+o) 振幅 2^(n-i)·ai/(2^(n+1)-1）、base_amplitude 基础振幅缩放因子 float、octave_count 采样八度数 1-32、normalize 输出归一化 true/false/"legacy"）、Definition Behavior 定义行为（服务器启动加载一次、/reload 不重新加载、噪声可被密度函数或表面规则引用 坐标依赖随机值）、Hardcoded Vanilla Usages 硬编码原版用途（minecraft:surface/surface_secondary 表面规则厚度、minecraft:clay_bands_offset 恶地陶瓦条带、minecraft:badlands_pillar/_roof/badlands_surface 侵蚀恶地柱、minecraft:iceberg_pillar/_roof/iceberg_surface 冰冻海洋冰山）。"
whenToUse: "Use when writing datapack worldgen noise definitions."

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

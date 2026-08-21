---

name: minecraft-jukebox-song
description: "Minecraft Jukebox Song 唱片盒歌曲定义：JUKEBOX_SONG 注册表、data/<namespace>/jukebox_song/ 数据包路径、tags/jukebox_song/ 标签、JSON 格式（comparator_output 红石比较器信号强度 0-15、description 歌曲名称文本组件、length_in_seconds 歌曲持续时间秒>0 TPS20转换为游戏刻+20额外刻、sound_event 播放音效事件 忽略客户端传播距离）、Definition Behavior 定义行为（服务器启动加载一次、/reload 不重新加载）、Playback Behavior 播放行为（读取 jukebox_playable 物品栈组件 获取唱片盒歌曲 播放、引用歌曲不存在则无事发生、record 类别 音量4 音高1 立即播放线性音量衰减、最远可听距离 sound_id attenuation_distance×音量4 默认64方块、sound event range不参与计算、作为世界事件发送 忽略传播距离）。"
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

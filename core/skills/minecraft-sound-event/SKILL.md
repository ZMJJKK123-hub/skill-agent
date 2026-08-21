---

name: minecraft-sound-event
description: "Minecraft Sound Event 声音事件（Java Edition）：Sound Events 声音事件（SOUND_EVENT 注册表、内置注册表 可使用未定义ID、播放创建声音事件实例 事件+位置+初始音高/音量、声音事件引用 命名空间ID、play range 播放范围 服务器→客户端发送距离）、Inline Format 内联格式（sound_id 事件引用 + range 最大发送距离 缺失→16×初始音量）、Definition Format 定义格式 sounds.json（assets/<namespace>/sounds.json、replace 替换/合并、sounds 可播放声音条目 列表：name 声音文件路径或事件引用、type file/event、weight 权重、attenuation_distance 线性衰减距离、pitch/volume、preload 预加载、stream 流式解码、subtitle 字幕翻译键）、Merging 合并（底部向上加载、非冲突事件直接加载、replace:true丢弃下层数据 replace:false合并、解析错误丢弃整个资源包、直接/间接自引用导致非致命栈溢出 卸载所有资源包）、Empty References 空引用（minecraft:intentionally_empty 不可替换 无声音无警告、minecraft:empty 占位符 sounds为空 首次播放警告）、Sound Playback 声音播放（Logical Sides 逻辑侧面：Server sounds 服务器声音 范围range或max{16v,16}、Client sounds 客户端声音 仅一个客户端；Categories 类别 master/music/record/weather/block/hostile/neutral/player/ambient/voice/ui；Instance Types 实例类型：Normal 即时非循环线性衰减、Bee flying 蜜蜂飞行、Elytra flying 鞘翅飞行、Entity-bound 实体绑定、Guardian attack 守卫者攻击、Biome ambient 生物群系环境、Minecart 矿车、Minecart riding 矿车骑乘、Sniffer digging 嗅探者挖掘、Underwater ambient 水下环境、Underwater ambient additions 水下环境附加、End flash 末地闪光）、Playback Steps 播放步骤（跳过Silent:true实体→按权重选择声音条目→空引用不播放→最终音量=类别×实例×条目音量0-1→最终音高=实例×条目音高0.5-2→音量0不播放→衰减距离=最终音量×条目衰减距离→静态缓冲 vs 流式）。"
whenToUse: "Use when defining or referencing sound events in data packs/resource packs (sounds.json, playable events)."

---

# Sound Event (Java Edition)

Sound events are the base objects the game plays. (Bedrock has its own sound events.)

## Sound Events

Registry `SOUND_EVENT`, data pack path `sound_event` — a built-in registry, yet undefined IDs can be used. Playing creates a **sound event instance** (event + position + initial pitch/volume). A sound event has:

- a **sound event reference** (namespace ID; for built-in events the registration name equals the reference), and
- a **play range**: server→client send distance for the instance.

Inline format (usable anywhere in data packs):

```json
{ "sound_id": "<event ID>", "range": 16.0 }
```

`range` — max distance sent to players (absent → 16 × initial volume). `sound_id` (required) — the event reference.

## Definition Format (sounds.json)

Sound event definitions live in `assets/<namespace>/sounds.json` (vanilla's is a hashed resource file). Root object mapping event names (e.g. `entity.enderman.stare` → ID `<ns>:<name>`) to:

- `replace` (default false) — replace lower-priority packs' data instead of merging.
- `sounds` — the playable sound entries (string = name with defaults, or object):
  - `name` (required) — a sound file (`assets/<ns>/sounds/<path>.ogg`) or another event reference.
  - `type` (default `file`) — `file` or `event`.
  - `weight` (>0, default 1; ignored for `event`) — random selection weight (events use the referenced event's own weights).
  - `attenuation_distance` (default 16) — linear attenuation max distance (mono audio only; ignored by some instance types).
  - `pitch` (>0, default 1), `volume` (>0, default 1).
  - `preload` (default false; ignored for `event`) — load into memory right after all definitions load.
  - `stream` (default false) — stream-decode progressively (then no looping and preload is moot).
  - `subtitle` — localization key for the subtitle when this event plays.

### Merging

Packs load bottom-up: non-conflicting events load directly; on conflict, `replace: true` in the upper pack discards all lower data; `replace: false` merges. Parse errors in any sound data discard that whole resource pack. Direct/indirect self-references (type `event` cycles) cause a non-fatal stack overflow and unload ALL resource packs. After merging, `preload: true` files load.

Example merge (top to bottom): A: sounds AB (replace false) → C,D (replace true) → G,H (replace false) ⇒ final A = ABCD; B: E,F (false) → I,J (true) ⇒ final B = EFIJ.

### Empty References

- `minecraft:intentionally_empty` — un-replaceable; plays nothing, no warnings.
- `minecraft:empty` — placeholder for events with empty `sounds`; warns on first play.

## Sound Playback

### Logical Sides

- **Server sounds** — created server-side, sent over the network to nearby players (blocks, entities, commands like `/playsound`). Radius: `range` if present, else max{16v, 16} from initial volume v (players within 16 blocks always receive it).
- **Client sounds** — created client-side, only on one client (e.g. biome ambient music).

### Categories

`master` (base for all), `music`, `record` (note blocks/jukeboxes), `weather`, `block`, `hostile`, `neutral`, `player`, `ambient` (fireworks, XP orbs, item entities), `voice` (narrator), `ui`.

### Instance Types

- **Normal** — instant, non-looping, linear falloff; most sounds.
- **Bee flying** — client sound on world join; `entity.bee.loop`/`loop_aggressive`; volume/pitch scale with horizontal speed.
- **Elytra flying** — client sound while gliding (`item.elytra.flying`); loops; volume 0 for the first second, ramps up over the next second and with speed; louder = higher pitch.
- **Entity-bound** — follows the entity's position; non-looping.
- **Guardian attack** — `entity.guardian.attack`; loops, no attenuation; volume ∝ attack progress², pitch linear.
- **Biome ambient** — client, loops, follows the player, fades across biome borders.
- **Minecart** — `entity.minecart.riding` on join; loops; volume/pitch linear with speed.
- **Minecart riding** — `entity.minecart.inside` / `inside.underwater`; loops, no attenuation; louder with speed.
- **Sniffer digging** — `entity.sniffer.digging`; non-looping, follows the sniffer.
- **Underwater ambient** — client on entering water (`ambient.underwater.loop`); loops, follows player; volume ramps up over 2 s, fades over 1 s after leaving.
- **Underwater ambient additions** — client on entering water; 0.01% ultra_rare / 0.09% rare / 0.9% normal `ambient.underwater.loop.additions*`, else nothing; non-looping, stops on leaving water.
- **End flash** — `weather.end_flash`; position = 10 blocks along the flash's pitch/yaw direction.

### Playback Steps

1. Skip if a related entity has `Silent: true`.
2. Pick a sound entry by weight (volume v0, pitch p0, attenuation d0). Event references multiply their referenced entry's volume/pitch into their own (v0 = v·v'); attenuation always comes from the current entry only.
3. Empty reference → don't play.
4. Final volume: normal instances = category × instance × entry volumes, clamped 0–1; other types ignore the entry volume.
5. Final pitch: normal instances = instance × entry pitch, clamped 0.5–2; others use instance pitch only.
6. Volume 0 → don't play.
7. Attenuation distance = final volume × entry attenuation (ignored for no-attenuation models).
8. Static buffering (whole file; allows looping) vs streaming (no looping even if requested).

Trivia: `music.nether.warped_forest` is defined and `/playsound`-selectable but has no actual sound; stereo audio cannot use linear attenuation in OpenAL.

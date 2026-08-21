---

name: forge-gameeffects-sounds
description: "Forge 声音系统：sounds.json 定义（assets/<namespace>/sounds.json、声音事件、声音文件路径、stream 流式播放、volume/pitch/weight 配置）、SoundEvent 注册（RegistryObject、注册名 = ResourceLocation）、SoundSource 声音类别、声音播放方法矩阵（Level#playSound BlockPos/x,y,z、Level#playLocalSound 客户端本地播放、ClientLevel#playLocalSound、Entity#playSound 实体声音、Player#playSound 玩家声音、LocalPlayer#playLocalSound 客户端玩家声音）、逻辑客户端/服务端行为差异、SoundEvent 服务端引用、sounds.json 数据生成、.ogg 文件格式。"
whenToUse: "Use when creating sound events or playing sounds in a Forge mod."

---

# Sounds

## Terminology

- **Sound event**: something that triggers a sound effect (e.g. `minecraft:block.anvil.hit`).
- **Sound category**: the category (player/block/master...) represented by the sound settings sliders.
- **Sound file**: the literal `.ogg` file played.

## sounds.json

Located at `assets/<namespace>/sounds.json`; defines sound events in that namespace:

```js
{
  "open_chest": {
    "subtitle": "mymod.subtitle.open_chest",
    "sounds": [ "mymod:open_chest_sound_file" ]
  },
  "epic_music": {
    "sounds": [ { "name": "mymod:music/epic_music", "stream": true } ]
  }
}
```

Each key is a sound event (namespace from the JSON); `sounds` is an array — the game picks randomly. Long files (music) should use the object form with `stream: true` (streams from disk; can also set volume, pitch, weight). Sound file paths: `assets/<namespace>/sounds/<path>.ogg`. Can be data generated.

## Creating sound events

Create and register a `SoundEvent` (registry name = its location) to reference sounds on the server; expose them in an API if the mod has one. Any sound in `sounds.json` can be referenced on the logical client even without a `SoundEvent`.

## Playing sounds

"Server Behavior"/"Client Behavior" refer to logical sides.

- `Level#playSound(Player, BlockPos, SoundEvent, SoundSource, volume, pitch)` → forwards to the x/y/z overload (+0.5 per coordinate).
- `Level#playSound(Player, x, y, z, ...)`: client plays to the client player if the passed player is them; server plays to everyone nearby **except** the passed player (null = everyone). Use for player-initiated sound on both sides, or server-side general sounds with null.
- `Level#playLocalSound(x, y, z, ...)`: client only (with distance delay option); does nothing on the server. Used for thunder / custom-packet sounds.
- `ClientLevel#playLocalSound(BlockPos, ...)`: forwards to the Level overload.
- `Entity#playSound(...)`: forwards with null player; server plays to everyone at the entity's position; client does nothing. For non-player entity sounds.
- `Player#playSound(...)`: server plays to everyone except this player; client delegates to `LocalPlayer`.
- `LocalPlayer#playSound(...)`: client-only; plays the sound. Together with `Player`, handles user + everyone-else playback.

---
name: minecraft-sound-event
description: Sound event — registry usage, sounds.json format, merging, playback.
whenToUse: Use when defining or referencing sound events in data packs/resource packs (sounds.json, playable events).
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

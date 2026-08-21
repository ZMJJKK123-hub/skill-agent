---

name: forge-gameeffects-particles
description: "Forge 粒子系统：ParticleType 注册（overrideLimiter、ParticleOptions$Deserializer、#codec、SimpleParticleType）、ParticleOptions 数据持有（#getType、#writeToNetwork、#writeToString、#fromCommand、#fromNetwork）、Particle 渲染（#render、#getRenderType、TextureSheetParticle、ParticleRenderType TERRAIN_SHEET/PARTICLE_SHEET_OPAQUE/PARTICLE_SHEET_TRANSLUCENT/PARTICLE_SHEET_LIT/CUSTOM/NO_RENDER）、ParticleProvider 工厂（#createParticle、RegisterParticleProvidersEvent 注册、#registerSpecial）、ParticleDescription JSON 纹理定义（assets/<modid>/particles/<name>.json）、SpriteSet 粹子集（#setSpriteFromAge、#pickSprite、#registerSpriteSet）、粒子生成（ClientLevel#addParticle/#addAlwaysVisibleParticle、ServerLevel#sendParticles 网络包）、客户端/服务端分离。"
whenToUse: "Use when creating custom particles in a Forge mod."

---

# Particles

Particles are client-side polish effects. A particle is split into the **client-only** implementation (display) and the common implementation (reference/sync).

| Class | Side | Description |
|---|---|---|
| `ParticleType` | BOTH | Registry object referencing the particle type. |
| `ParticleOptions` | BOTH | Data holder syncing info from network/commands to clients. |
| `ParticleProvider` | CLIENT | Factory (registered per `ParticleType`) constructing a `Particle` from options. |
| `Particle` | CLIENT | Renderable display logic. |

## ParticleType

Must be registered. Constructor takes an `overrideLimiter` (render regardless of distance) and a `ParticleOptions$Deserializer`; implement `#codec` (only used in the biome codec for vanilla). For particles with no custom data, use `SimpleParticleType` (implements both `ParticleType` and `ParticleOptions`).

A `ParticleType` is not required for client-only spawning, but is required for `ParticleEngine` logic or server-spawned particles.

## ParticleOptions

Carries per-particle data; all spawn methods take one. Three methods: `getType` (the `ParticleType`), `writeToNetwork` (encode to buffer), `writeToString` (encode to string). `ParticleOptions$Deserializer` provides parity decoders `fromCommand` (from string) and `fromNetwork` (from buffer); pass it to the `ParticleType` constructor for custom data.

## Particle

Implement `render` and `getRenderType`. Common subclass: `TextureSheetParticle` (renders a sprite). `ParticleRenderType` options: `TERRAIN_SHEET`, `PARTICLE_SHEET_OPAQUE`, `PARTICLE_SHEET_TRANSLUCENT`, `PARTICLE_SHEET_LIT`, `CUSTOM`, `NO_RENDER`.

## ParticleProvider

Factory with `#createParticle(options, level, x, y, z, dx, dy, dz)`. Register via `RegisterParticleProvidersEvent` (mod event bus, **client only** — isolate in a client class with `DistExecutor` or `@EventBusSubscriber`) using `#registerSpecial`.

For sheet render types (opaque/translucent/lit), textures come from a `ParticleDescription` JSON at `assets/<modid>/particles/<registry name>.json`:

```js
{ "textures": [ "mymod:particle_texture", "mymod:particle_texture2" ] }
```

Textures resolve to `assets/<modid>/textures/particle/<path>.png`, ordered by drawing order. Reference them via `SpriteSet` (age-based via `#setSpriteFromAge` or random via `#pickSprite`); register with `#registerSpriteSet` (or `#registerSprite` with `ParticleProvider$Sprite` for single textures).

## Spawning

- `ClientLevel`: `#addParticle` or `#addAlwaysVisibleParticle` (visible from any distance).
- `ServerLevel`: `#sendParticles` (sends a packet to clients). Calling the client methods on the server does nothing.

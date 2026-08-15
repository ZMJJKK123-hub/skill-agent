---
name: minecraft-wolf
description: Wolf — variants, sound variants, taming, breeding, teleporting, armor, NBT.
whenToUse: Use when working with wolves (taming, breeding, wolf armor, variant/sound-variant data).
---

# Wolf

Wolves are tameable friendly mobs. ("Dog" redirects here.)

## Spawning

Untamed wolves spawn with biome-dependent variants (on grass/dirt/podzol/snow blocks):

- Jungle, bamboo jungle, sparse jungle → **rusty wolf**
- Savanna, savanna plateau, windswept savanna → **spotted wolf**
- Badlands, wooded badlands, eroded badlands → **striped wolf**
- Forest, wooded forest (mangrove?) → **woods wolf**
- Snowy taiga → **ashen wolf**
- Old growth pine taiga → **black wolf**
- Old growth spruce taiga → **chestnut wolf**
- Snowy slopes? / grove → **snowy wolf**
- All other biomes → **pale wolf**

10% of wolves spawn as babies. Spawn eggs and `/summon` also pick variants by biome.

### Sound Variants

7 sound variants: Big Dog, Classic, Cute, Puglin, Angry, Grumpy, Sad — personality-flavored, no behavioral effect. Assigned independently of biome variant, 14.2% each; used for barking, panting, whining, howling, death and hurt sounds.

## Drops

1–3 XP when killed by a player or tamed wolf (babies drop none). Bedrock: tamed wolves drop XP only when killed by a player (not the owner) or another tamed wolf.

## Behavior

Three states:

- **Wild** — one white + one black pixel per eye; tail up 36°. (Bedrock: babies can ride wild wolves.)
- **Angry** — wild wolves with a target; red eyes, angry howling; tail up 88.2°, not wagging; cannot be leashed (leashes don't break when a leashed wolf turns angry); cannot be tamed with bones, but meat still heals/ages it.
- **Tamed** — gentle eyes, collar; tail angle 99° − (hmax−hcur)/hmax × 72° (full health → 99°).

Babies have big heads; they don't follow adults unless a wolf nearby is fighting. Holding meat/bones within 8 blocks makes wolves tilt their heads (begging). Wolves shake off water with splash particles after leaving water/rain (Java: darkened texture while wet).

### Attacks

- Wild wolves hunt skeletons, wither skeletons, strays, bogged, charred, the Wither, rabbits, foxes, sheep, baby turtles. Tamed wolves standing also hunt the skeletal types + Wither. Sitting tamed wolves don't attack.
- Skeletons/strays/etc., foxes, rabbits, baby turtles flee wolves; the skeletal mobs fight back. Killer rabbits attack wolves (Java). Llamas/wandering traders spit at wild wolves; wolves always flee from Strength 4–5 llamas.
- Wolves never attack creepers or ghasts. Tamed wolves never attack their owner, owner's team, same-owner wolves, tamed cats/parrots/horses/donkeys/mules/skeleton horses/zombie horses/llamas/traders/nautiluses/zonbies and item-holding allays (Bedrock exception: retaliate when the owner is attacked by tamed llamas).
- Wolves anger at attackers (tamed wolves also anger at attackers of their owner); nearby wolves (33×21×33 box) join unless the victim was one-shot. Tamed wolves anger at anything the owner attacks (if attackable). Damage: wild 3 (×5.5 hearts?), tamed 4; only player-inflicted damage scales with difficulty (Java).
- Mobs killed by tamed wolves drop XP/rare drops even without player involvement.

### Damage Behavior

Wolf armor absorbs most damage as durability (ceil), showing cracking textures. `#bypasses_wolf_armor` damage passes through: magic, cramming, drowning, dehydration, freezing, suffocation, out-of-world, starvation, thorns, wither, void, `/kill`, mace smash attacks.

### Movement and Sitting

Interacting (not feeding) makes a tamed wolf sit/stand. Sitting wolves stand when pushed into water or hurt (Java: stay sitting forever if the owner leaves the server). Standing tamed wolves wander-follow the owner; within 10 blocks they walk directly; beyond 12 they teleport.

### Teleporting

Tamed wolves teleport to the owner when >12 blocks away. Teleporting resets their attack — a wolf teleporting mid-fight resumes following. Wolves may teleport into a bad position and suffocate. No teleport when: sitting (but standing from being hurt can trigger it), attacking an entity (Java; teleports after the target dies), riding in a minecart/boat, leashed to a fence, chunk unloaded, no valid spot in the 5×3×5 area around the player, or the owner is in another dimension (Bedrock: wolves do follow through portals).

### Taming

Bones: each use has 1/3 chance to tame (≈3 bones average). Tamed wolves get a red collar and ignore further bones; unlimited tames. Dyes recolor the collar. Wolf armor gives 11 armor points; armadillo scutes repair it; shears remove it. Tamed wolves with ≥20 HP pant; below 20 HP they whine. Tamed wolf death shows a death message to the owner/all players.

### Feeding

Meat restores twice its hunger value as health; no side effects (rotten flesh/raw chicken don't poison). Java: rabbit stew returns a bowl.

### Breeding

Feed two full-health tamed adult wolves any food except pufferfish, tropical fish, raw/cooked cod and salmon, and rabbit stew → love mode (hearts) when both are standing; 1–7 XP; 5-minute (1-minute in newer versions?) cooldown. Java: feeding wild wolves shows hearts but no love mode. Baby inherits a random coat color of the parents, collar = a valid mix of the parents' collar colors (else random parent), and the owner is chosen by the rules (same owner; different owners → the later-loaded wolf's owner unless one was sitting/lost its owner → the other's). Feed babies (same exclusions) to grow ~10% faster per feed. Golden dandelions halt baby growth (toggle; growth-stopped babies accept only golden dandelions).

## Sounds

Common sounds exist for adults/babies plus per-variant sounds for angry/big/classic/cute/grumpy/puglin/sad (Java & Bedrock tables on the wiki).

## Data Values

- ID: `minecraft:wolf`.
- NBT: entity/living/mob/breedable/animal/tameable/angerable common tags plus:
  - `CollarColor` (0–15, default 14 red; out of range → 0 white; wild wolves have it but no collar rendered; → component `wolf/collar`).
  - `sound_variant` (namespace ID; invalid → `classic`; → component `wolf/sound_variant`).
  - `variant` (namespace ID; invalid → `pale`; → component `wolf/variant`).

## Trivia

Wolves can teleport onto incomplete blocks; anger can persist after the player moves far away (Java, without pursuit); they chase flying mobs (except ghasts); tamed wolves take two Warden melee hits to kill; wolf variants resemble real canids (ashen = husky-like, black = melanistic, rusty = Ethiopian wolf/jackal, spotted = African wild dog, striped = coyote/striped hyena, snowy = Arctic wolf); sound variants were recorded at a dog daycare.

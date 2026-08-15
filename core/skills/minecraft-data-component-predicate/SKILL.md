---

name: minecraft-data-component-predicate
description: "Data component predicate format — existence checks and value predicates."
whenToUse: "Use when testing item/block entity/entity data components in advancements, loot predicates, item predicates, or item models."

---

# Data Component Predicate

Data component predicates (component predicates) test whether data components satisfy conditions. Java Edition only.

## Usage Formats

- **Advancements/predicates**: a map of `<component predicate ID>: <test content>` inside `predicates`:

```json
{ "predicates": { "minecraft:damage": { "durability": { "min": 5 } } } }
```

- **Commands**: the `minecraft:item_predicate` argument type accepts `<predicate ID>~<test content>`.
- **Item models**: `{ "predicate": "<predicate ID>", "value": <test content> }` in `condition`/`component` property (see the item-model-mapping skill).

## Existence Checks

An empty object `{ "<component ID>": {} }` tests that the component exists. Because predicate IDs overlap with component IDs, the game first tries to interpret the key as a value-testing predicate type; only if that interpretation is invalid does it fall back to an existence check. E.g. `{"minecraft:instrument": {}}` tests existence, but `{"minecraft:potion_contents": {}}` is invalid because `potion_contents` is a real predicate type that doesn't accept this format.

## Value Predicates

- `attribute_modifiers` — modifiers in the component. Collection predicate: `size` (int bounds on modifier count), `count` (list of `{count, test}` — number of modifiers matching a test), `contains` (list of tests; each test must match ≥1 modifier, one modifier may satisfy several). Modifier test: `amount` (double bounds), `attribute` (ID/tag/list), `id`, `operation` (`add_value`/`add_multiplied_base`/`add_multiplied_total`), `slot`.
- `bundle_contents` / `container` — item stacks in the component (collection predicate over item stack predicates: `count` (int bounds), `items` (ID/tag/list), `components` (exact match of the given components), `predicates` (nested component predicates)).
- `custom_data` — matches the custom data (JSON object, NBT compound, or SNBT string converted at parse time).
- `damage` — `damage` (damage value int bounds; from the `damage` component) and/or `durability` (int bounds; `max_damage` − `damage`; `max_damage` absent = 0).
- `enchantments` / `stored_enchantments` — array of conditions (all must pass): `enchantments` (ID/list/tag; any one present passes), `levels` (int bounds on that enchantment's level; without `enchantments`, any enchantment of a matching level passes).
- `firework_explosion` — collection predicate over explosions: `has_trail`, `has_twinkle` (bools), `shape` (`small_ball`/`large_ball`/`star`/`creeper`/`burst`).
- `fireworks` — `flight_duration` (int bounds, in gunpowder units) + `explosions` collection predicate (same firework tests).
- `jukebox_playable` — `song` (jukebox song ID/list/tag).
- `potion_contents` — only the `potion` and `custom_effects` fields are tested. Pre-26.3: `potion` ID/list/tag. From 26.3: `potions` (ID/list/tag; any present passes) and `effects` (collection predicate over status effects: mob effect predicates with `size`/`count`/`contains`).
- `trim` — checks IDs only (inline data always fails): `material` (trim material ID/list/tag), `pattern` (trim pattern ID/list/tag).
- `villager/variant` — `villager` type ID/list/tag.
- `writable_book_content` — `pages` collection predicate (each page test is a string exactly matching a page's unfiltered raw text).
- `written_book_content` — `pages` collection predicate (each test is a text component exactly matching a page's unfiltered raw text), plus `author`, `title` (unfiltered raw), `generation` (0–3 int bounds), `resolved` (bool).

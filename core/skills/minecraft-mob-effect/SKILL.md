---

name: minecraft-mob-effect
description: "Potion effects: base data for potions, splash/lingering, tipped arrows, clouds."
whenToUse: "Use when understanding potion effect data, potion colors, names, and their linked status effects."

---

# Potion Effects

This content applies only to Java Edition.

Potion effects are the base data used by potions, splash potions, lingering potions, tipped arrows, and area effect clouds. Potion items and the splash potion / lingering potion / arrow / area effect cloud entities store a potion effect in their data. If no potion effect is specified, or the ID is unrecognized, the uncraftable potion or water bottle effect is used.

A potion effect determines the potion's name, color, the status effects it applies (with level and duration), and other behaviors. Some effect names differ from their status effect names; a few potion effects have no status effect (e.g. the Turtle Master potion applies several).

## Potion effect list

Duration notes: splash potions apply duration scaled down with distance from the break point; lingering potions and area effect clouds apply 1⁄4 duration; tipped arrows apply 1⁄8 duration. The "potion color" column is computed by the Java mixing algorithm, not predefined. Bedrock numeric IDs are the data values of potions (arrows +1 each).

For the full effect list (name, ID, color, linked status effects), see Minecraft Wiki.

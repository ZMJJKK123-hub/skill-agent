---

name: minecraft-tag-fluid
description: "Java Edition fluid tags: #water (2 entries) controlling coral survival, farmland moisture, sponge absorption, underwater fog, swimming behavior, and more; #lava (2 entries) controlling cactus breaking, lava texture effects, smoke particles, entity burning, and stone formation; plus #bubble_column_can_occupy, #supports_frogspawn, #supports_lily_pad."
whenToUse: "Use when querying fluid tags (water, lava etc.) or judging which fluid tag controls a game behavior."

---

# Fluid Tags

This content applies only to Java Edition.

Fluid tags are groups of fluids.

## Usage

The game uses fluid tags to control various fluid-related behaviors. Fluid tags can also be used in block predicates and advancement predicates to test whether a position contains a specified fluid.

## Tag list

### `#bubble_column_can_occupy` (1 entry)

Fluids that can be occupied by bubble columns:

- `water`

### `#lava` (2 entries)

- This fluid breaks adjacent cacti.
- Used to render the lava texture effect on fluids.
- Used to spawn smoke particles instead of normal rain particles while raining.
- Used for fog effects similar to lava fog.
- Items and experience orbs burn when touching this fluid.
- Using a bucket of this fluid plays the lava sound effect.
- Represents a LAVA pathfinding node.
- Used to form stone, cobblestone, or basalt.
- Used in various strider pathfinding processes.
- Striders cannot be ridden while immersed in these fluids.

Members:

- `lava`
- `flowing_lava`

### `#supports_frogspawn` (1 entry)

Fluids on which frogspawn can be placed:

- `water`

### `#supports_lily_pad` (1 entry)

Fluids on which lily pads can be placed and survive:

- `water`

### `#supports_sugar_cane_adjacently` (1 entry)

Fluids adjacent to blocks on which sugar cane can be placed and survive:

- `#water`

### `#water` (2 entries)

- Coral requires at least one side touching this fluid, otherwise it may deactivate.
- Coral fans must be placed in this fluid.
- Farmland determines its moisture via this fluid.
- Sponges absorb this fluid.
- Some particles use it to decide whether they should persist (`bubble`, `bubble_column_up`, `current_down`, `underwater`).
- Dripping particles internally use this fluid to determine their color.
- Used to enable underwater fog.
- Determines whether entity movement behaves like swimming.
- Represents a WATER pathfinding node; some mobs move toward it.
- Boats check this fluid.
- Concrete solidifies in this fluid.
- Items and experience orbs float in this fluid.
- Guardians, squids, and turtles check for this fluid.
- Fishing bobbers bob up and down in this liquid.
- Glass bottles can be filled from this liquid.
- Cannot be placed with a bucket in the Nether.

Members:

- `water`
- `flowing_water`

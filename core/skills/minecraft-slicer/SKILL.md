---

name: minecraft-slicer
description: "The Slicer utility: splits texture atlases for resource pack upgrades."
whenToUse: "Use when upgrading resource packs or understanding the Slicer/Unstitcher/Texture Ender utility family."

---

# Slicer

Slicer is a Java utility pack containing 3 programs, designed to help upgrade resource packs to newer versions by splitting certain texture collections into individual textures.

Currently 4 versions exist:

- Java 1.14 format: splits `particles.png`, `paintings_kristoffer_zetterstrand.png`, and `inventory.png` into separate textures.
- Java 1.20.2 format: splits most UI textures into separate textures.
- Java 1.20.5 format: splits `map_icons.png` into separate textures.
- Java 26.2 format: splits and rearranges bed, sign, and hanging sign textures. This version's automation is incomplete and requires manual work.

## Related tools

- **Unstitcher**: converts texture packs to Java 1.5 format
- **Texture Ender**: converts texture packs to resource packs

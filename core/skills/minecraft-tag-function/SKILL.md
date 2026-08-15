---

name: minecraft-tag-function
description: "Function tags (#load, #tick) usage and a JSON example, for organizing datapack functions."
whenToUse: "Use when organizing datapack functions with function tags (#load, #tick)."

---

# Function Tags

This content applies only to Java Edition.

Function tags are groups of functions.

## Usage

Function tags can be used with the `/function` command, which runs all functions in the tag in the order they first appear. If a function is referenced multiple times in a tag and its subtags, it runs only once.

The game provides two special tags:

- Functions listed in `#load` run when the world loads or the server starts. They also run on every datapack reload.
- Functions listed in `#tick` run at the start of every game tick, repeating continuously.

Vanilla datapacks do not use these tags.

## Example

The following example defines the `#load` tag in the `minecraft` namespace and adds the `example:test` function.

`data/minecraft/tags/function/load.json`:

```json
{
  "values": [
    "example:test"
  ]
}
```

The game runs `example:test` once when the datapack loads.

---

name: minecraft-tag-dialogue
description: "Dialogue tags: #pause_screen_additions (replaces pause menu buttons with custom dialogues) and #quick_actions (opened via G key binding for quick actions), used for custom dialogue systems in data packs."
whenToUse: "Use when defining or invoking datapack dialogue tags (dialog_list etc.)."

---

# Dialogue Tags

This content applies only to Java Edition.

Dialogue tags are groups of dialogues.

## Usage

The game uses dialogue tags to define dialogues that can be invoked without commands. Otherwise, dialogue tags can currently only be referenced by `dialog_list`-type dialogues.

## Tag list

### `#pause_screen_additions`

- Dialogues holding this tag can be entered directly from the pause menu.
- With more than one dialogue in the tag, the `custom_options` dialogue list is entered.

No members.

### `#quick_actions`

- Dialogues holding this tag can be entered directly via the quick action key binding (G by default).
- With more than one dialogue in the tag, the `quick_actions` dialogue list is entered.

No members.

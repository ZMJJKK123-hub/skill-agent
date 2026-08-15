---

name: minecraft-chat-type
description: "Chat type definition JSON: CHAT_TYPE registry, chat/narration decorations, params."
whenToUse: "Use when overriding the 7 vanilla chat types in datapacks to control chat display style and narration."

---

# Chat Types

This content applies only to Java Edition.

Chat types are metadata identifying the purpose of chat messages (e.g. system messages vs. player chat). They control the display style in the chat box and the narration text.

The game only uses the following 7 chat types; datapack-defined types cannot be invoked, but datapacks can override these 7 to control display and narration. Chat type tags have no effect. Placeholder parameters: `sender` (sender's name), `target` (receiver player/team name), `content` (chat message).

## Definition format

Chat types use the `CHAT_TYPE` registry; the datapack path is `chat_type` (definitions in `data/<namespace>/chat_type`, tags in `data/<namespace>/tags/chat_type`).

Definition files use JSON with the following structure:

- JSON file root object
  - `chat` (compound, required): display style in the chat box (see Decoration below).
  - `narration` (compound, required): narration text (see Decoration below).

### Chat type decoration

- `translation_key` (string, required): a translation key.
- `parameters` (list, required): parameters passed into the translated text, in order (`sender`/`target`/`content`; may repeat).
- `style` (compound, default none): text component style; does not affect narration.

## Definition behavior

Chat type data is loaded only once at server startup; `/reload` does not reload it — a server restart is required.

When displaying or narrating a message, the game reads the type's decoration and replaces parameters with text components. Example: `parameters: ["sender", "content", "sender"]` with translation `%s: %s (%s)` and sender A / content B produces `A: B (A)`.

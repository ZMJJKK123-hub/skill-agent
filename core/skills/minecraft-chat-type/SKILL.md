---

name: minecraft-chat-type
description: "Minecraft Chat Type 聊天类型定义：CHAT_TYPE 注册表、data/<namespace>/chat_type/ 数据包路径、tags/<namespace>/tags/chat_type/ 标签、JSON 格式（chat 聊天框显示样式、narration 旁白文本）、Decoration 装饰格式（translation_key 翻译键、parameters 参数列表 sender/target/content、style 文本样式 不影响旁白）、7种原版聊天类型（data pack 可覆盖但不能调用新类型）、Placeholder Parameters 占位符参数（sender 发送者名称、target 接收者玩家/队伍名称、content 聊天消息）、服务器启动加载（/reload 不重新加载）、聊天类型标签无效果、装饰参数替换文本组件。"
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

---

name: forge-concept-internationalization
description: "Forge 国际化（i18n）与本地化机制：翻译键（translation keys）、语言文件（assets/[namespace]/lang/[locale].json）、Block/Item 翻译键生成（getDescriptionId、registry name 转换）、客户端/服务端本地化差异、I18n 客户端本地化、TranslatableContents 惰性本地化、TextComponentHelper#createComponentTranslation、Component#translatable、语言文件格式、翻译键与注册名分离原则。"
whenToUse: "Use when localizing Forge mod text or sending translatable text to players."

---

# Internationalization and Localization

Internationalization (i18n) designs code so it needs no changes for various languages; localization adapts displayed text to the user's language. i18n uses translation keys (language-neutral identifiers, e.g. `block.minecraft.dirt`).

Localization happens in the game's locale: the client uses its language setting; a dedicated server only supports `en_us`.

## Language files

Located at `assets/[namespace]/lang/[locale].json` (UTF-8), a JSON map of keys to values:

```js
{
  "item.examplemod.example_item": "Example Item Name",
  "block.examplemod.example_block": "Example Block Name",
  "commands.examplemod.examplecommand.error": "Example Command Errored!"
}
```

## Usage with blocks and items

Block/Item names use translation keys from `#getDescriptionId` (Item also has `#getDescriptionId(ItemStack)`). The default is `block.`/`item.` + registry name with the colon replaced by a dot; `BlockItem`s inherit their block's key. Example: item `examplemod:example_item` needs `"item.examplemod.example_item": "..."`.

> Translation keys are only for i18n — never use them for logic; use registry names.

## Localization methods

> **Warning**: the server can only localize in its own locale. To respect client language settings, send `TranslatableComponent` (or similar language-neutral keys) so clients localize in their own locale.

- `net.minecraft.client.resources.language.I18n` (client only!): `get(String, Object...)` localizes in the client's locale with `String.format` arguments. Using it on a server crashes.
- `TranslatableContents`: lazily localized/formatted `ComponentContents`; parameters after the key are formatting args, only `%s`, `%1$s`, `%2$s`... supported; `Component`s keep their attributes. Create via `Component#translatable` or `MutableComponent#create`.
- `TextComponentHelper#createComponentTranslation(CommandSource, String, Object...)`: localized eagerly for vanilla clients, lazily via `TranslatableContents` otherwise; useful when servers allow vanilla clients.

---
name: minecraft-dialogue
description: Dialog definition format — invocation, dialog types, body, inputs, actions.
whenToUse: Use when authoring dialog JSON files for data packs (menus, forms, confirmations).
---

# Dialog Definition

Dialogs are a data-driven way to present interactive UIs to players: fixed information, events, and input submission to the server. Java Edition only.

## Invocation

Dialogs open via `/dialog`, text component click events, server messages, or other dialogs. Two special dialog tags control built-in entry points:

- `#pause_screen_additions` — replaces the pause screen's "Report Bugs" / "Provide Feedback" buttons. With exactly one registered dialog: the "Custom Options…" button becomes its display name and opens it directly. With several: the report-bug button opens the `custom_options` dialog listing jump buttons. With none, but with server link data (from the `server_links` packet): the `server_links` dialog replaces the button. Otherwise unchanged.
- `#quick_actions` — opened by the quick-actions key (default G); multiple entries open the `quick_actions` dialog with jump buttons.

## Layout

Dialogs have a header (33 px: title + a fixed warning button with a disconnect/exit option, 10 px apart), content (body elements + input panel; scrolls if too tall), and a footer (≥33 px, type-dependent). Everything is centered.

## Definition Format

Registry `DIALOG`, data pack path `dialog` (files in `data/<namespace>/dialog/`; tags in `tags/dialog/`).

Common fields:

- `after_action` (default `close`) — see below.
- `pause` (default true) — pause the game in single-player; must be false when `after_action` is `none`.
- `can_close_with_escape` (default true).
- `body` (default empty) — body elements (element or list).
- `inputs` (default empty) — input controls.
- `external_title` (default `title`) — text for buttons opening this dialog elsewhere.
- `title` (required) — dialog title text component.
- `type` (required) — dialog type.

Definitions load once at server startup; `/reload` does not reload them.

### After-action Behavior

- `none` — nothing; player stays in the dialog (requires `pause: false`).
- `close` — closes the dialog (always the behavior when exiting with Esc).
- `wait_for_response` — closes and shows the "waiting for server response" screen (does not pause; a return button appears after 5 s).

Effective click events inside dialogs: `copy_to_clipboard`, `custom`, `open_url`, `run_command`, `show_dialog` (`run_command` unavailable in configuration-phase dialogs).

## Dialog Types

- `confirmation` — yes/no confirmation: `yes` / `no` actions (the `no` action is also the Esc default).
- `dialog_list` — jump buttons to other dialogs: `button_width` (1–1024, default 150), `columns` (default 2), `dialogs` (required: tag/ID/inline/list), `exit_action` (return button; absent = no button).
- `multi_action` — multiple actions in a grid: `columns` (default 2), `actions` (required, non-empty), `exit_action`.
- `notice` — announcement with one confirm button: `action` (default: 150 px wide, closes the dialog).
- `server_links` — buttons from the `server_links` packet (text fixed by link `type`, click opens `url`; vanilla: empty or one `report_bug` link from `bug-report-link` in server.properties): `button_width`, `columns`, `exit_action`.

## Body Elements

Between the header and input panel (10 px gaps). Their text's click/hover events work normally.

- `item` — renders an item stack and optional description: `item` (item template), `description` (text component; item on the left, 4-px-padded centered multiline text on the right, 2 px apart), `show_decorations` (default true — durability bar/cooldown/count), `show_tooltip` (default true), `width`/`height` (1–256, default 16 — layout only), and a text `width` (default 200).
- `plain_message` — text: `contents` (text component), `width` (1–1024, default 200); 4 px padding, centered, wraps.

## Input Controls

Common: `key` (required; letters/digits/underscore only) + `type`. Types:

- `boolean` — checkbox + label (4 px apart): `label`, `initial` (default false), `on_false` / `on_true` (default "false"/"true"; string form submits these, NBT form submits `0b`/`1b`).
- `number_range` — slider (20 px high): `label`, `label_format` (default `options.generic_value`; first arg = label, second = current value), `width` (default 200), `start`/`end` (required doubles; end may be < start), `step` (>0; discrete values `initial + n×step` only), `initial` (default middle). String submission emits integers as integers ("5" not "5.0"); NBT submission appends `f`.
- `single_option` — selection button (20 px): `label`, `label_visible` (default true), `options` (non-empty list of `{id (real value), display (default id), initial}`; shorthand strings = id only; at most one initial, first option default), `width` (default 200).
- `text` — text box (20 px, label above with 4 px gap): `label`, `label_visible`, `initial` (default ""), `max_length` (default 32), `multiline` ({max_lines, height (1–512, default from max_lines)})`, `width` (default 200). Special characters are escaped on submission.

## Actions

Common: `label` (required text component), `tooltip`, `width` (1–1024, default 150), `action` object.

### Static Actions

- `open_url` — `url` (http/https only).
- `run_command` — `command`.
- `suggest_command` — has no effect in dialogs.
- `change_page` — has no effect in dialogs.
- `copy_to_clipboard` — `value`.
- `show_dialog` — `dialog` (ID or inline).
- `custom` — `id` (payload namespace ID), `payload` (≤16 nesting levels, ≤32768 bytes); no effect on the vanilla server.

### Dynamic Actions

- `dynamic/custom` — builds a `custom` payload from input values: `id`, optional `additions` (static compound merged first), then one key-value pair per input control (key = control `key`, value = input content), sent via the `custom_click_action` packet. Over-limit payloads cause a disconnect (or world exit in single-player).
- `dynamic/run_command` — builds a command from a `template`: `$(name)` placeholders (letters/digits/underscore; unknown names → empty string; at least one placeholder required). No `/` or `$` prefix allowed (parse failure if present). The executor defaults to the submitting player. Checks before sending: configuration-phase dialogs never send (log warning); unparseable → warning dialog; signature-requiring arguments (chat messages) → confirmation screen; permission level > 0 → permission warning dialog.

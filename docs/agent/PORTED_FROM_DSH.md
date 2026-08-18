# DSH Architecture Study & Ports

This document records what was studied from the official `deepseek-harness` (dsh) source and what was ported/adapted into `skill-agent`.

## Key files studied (deepseek-harness)

- `packages/core/agent-loop/src/agent.ts` — turn/step loop, inbox, pre-step, concluded-turn
- `packages/core/agent-loop/src/runtime-context.ts` — replaceable runtime-context snapshot
- `packages/core/agent-loop/src/tool-calls.ts` — tool execution, `concludesTurn`
- `packages/compaction/compaction-basic/src/index.ts` — automatic compaction on pressure and context overflow
- `packages/compaction/compaction-basic/src/summarizer.ts` — summarizer reuses system prompt
- `packages/core/system-prompt/src/index.ts` — ordered sections + dynamic variables
- `packages/context/agent-instructions/src/index.ts` — durable workspace instructions
- `packages/spill/spill-policy/src/index.ts` — spill oversized tool results

## Ported mechanisms

| Mechanism | Ported location | Status |
|---|---|---|
| Ordered prompt sections + variables | `core/promptkit.py`, `core/config.py` | ✅ already existed |
| Automatic compaction with structured summary | `core/compact.py` | ✅ already existed |
| Tool-pairing compaction boundary | `core/compact.py` | ✅ already existed |
| Runtime-context snapshot (single replaceable user message) | `core/agent.py`, `core/agent_hooks.py` | ✅ new |
| Pre-step hook infrastructure | `core/agent_hooks.py`, `core/agent.py` | ✅ new |
| Max tool-call rounds guard | `core/agent.py` | ✅ new |
| `[CONCLUDED]` tool ends turn | `core/agent.py` | ✅ new |
| Context-overflow auto-compact + retry (create + streaming) | `core/agent.py` | ✅ new |
| Spill oversized tool results to `.spill/*.txt` | `core/agent.py` | ✅ new |
| Summarizer receives system prompt | `core/compact.py` | ✅ new |
| Per-model context-window defaults | `core/compact.py` | ✅ new |
| Preserve initial task anchor across compaction | `core/compact.py` | ✅ new |
| Workspace docs (`docs/agent`) copied into session | `server_app/server.py` | ✅ new |
| AGENTS.md baseline instructions loader | `core/agent.py`, `mod_templates/.../AGENTS.md` | ✅ new |
| Auto error sink (`NEW_ERROR:` -> ERROR_LIST) | `server_app/run_task.py` | ✅ new |
| Supervisor can read workspace docs | `core/supervisor.py` | ✅ new |

## Key differences identified between dsh and skill-agent

1. dsh derives every request from a durable session event log; skill-agent uses an in-memory `messages` list (persisted as JSON lines but not event-sourced).
2. dsh has a plugin/waterfall system (`agent/pre-step`, `system-prompt/assemble`) for extensibility; skill-agent has a simpler registry.
3. dsh `compaction` runs between steps based on token-meter pressure; skill-agent compacts per round when estimated tokens exceed threshold.
4. dsh tool results can `concludesTurn`; skill-agent now supports a `[CONCLUDED]` marker.
5. dsh spills oversized results; skill-agent now spills to `.spill/`.

## Remaining possible future work

- Event-sourced session log with `deriveMessages()` (large refactor)
- Pre-step plugin/waterfall equivalent
- Workspace `AGENTS.md` instruction loader
- Per-model context-window policies in compaction
# Agent Variants

Part of [[Project Overview]] · builds on [[Agent Toolkit]] and [[Agent Knowledge]].

Each arena directory **is** a tournament entry: a self-contained agent configuration. Opening a Claude session in the directory instantiates that agent.

| Directory | Name | Prompt | Knowledge | Notebook | Toolkit |
|-----------|------|--------|-----------|----------|---------|
| `agent_arena/` | Claude | Full protocol + toolkit triggers | Full vault (openings, middlegame, endgames, strategy, calculation) | 4-file game notes | `chess-toolkit` |
| `agent_arena_weak/` | Claude-Lite | Same protocol, mental-only | How-to-think notes (strategy + calculation) | 4-file game notes | none |
| `agent_arena_vanilla/` | Claude-Vanilla | Context/strategy/continuity habits only | none | single md file per game | none |

The ladder measures what each layer adds: vanilla (raw model + habits + one memory file) → lite (+ teaching + structured notebook) → full (+ full vault + toolkit).

## Rules for variants

1. **Self-contained** — a variant directory carries its own `.mcp.json`, `CLAUDE.md`, knowledge copy, and `bug_report/` + `suggestion/` folders. No references into other variants' folders.
2. **Frozen copies, not links** — knowledge is copied so variants don't drift when the main vault evolves mid-experiment. Provenance noted here.
3. **Same table for everyone** — every variant uses the identical interaction MCP (`chess`). Only agent-side equipment varies ([[Agent Toolkit]] principle).
4. **Distinct player names** — so games and chat are attributable in spectator mode and analysis ("Claude" vs "Claude-Lite").

## The first experiment this enables

Claude vs Claude-Lite, same model, multiple games (colors alternating):
- Does the knowledge vault + toolkit measurably reduce blunders ([[Post-Game Analysis]] ACPL/blunder counts)?
- Watch live via [[Spectator Mode]] — both agents narrate reasoning in chat.

Future variants (Phase 4): no-knowledge baseline, toolkit-only, different models, different board representations.

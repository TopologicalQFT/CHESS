# Phase 3: Agent Knowledge

Part of [[Project Overview]]. Goal: make the agent play *better chess* purely through context — no engine assistance (Stockfish is reserved for [[Post-Game Analysis]] on the website, never available to the agent).

## Design

Knowledge lives as **markdown files the agent reads on demand** with its Read tool:

```
agent_arena/
├── CLAUDE.md              # Standing prompt: game loop + WHEN to read what
└── knowledge/
    ├── openings.md        # Repertoire: 1.e4/1.d4 lines, defenses, traps to avoid
    ├── principles.md      # Opening/middlegame principles, per-move tactics checklist
    └── endgames.md        # Basic mates, K+P technique, rook endgame rules
```

Why files instead of inlining everything in CLAUDE.md:
- CLAUDE.md loads every turn — keep it lean (the game loop + strategy checklist)
- The agent reads `openings.md` only during the opening, `endgames.md` only when material thins out
- **This is the tournament's "context" dimension**: a tournament entry = CLAUDE.md variant + knowledge set. Comparing "no knowledge" vs "principles only" vs "full knowledge" agents is a Phase 4 experiment.

## Reading triggers (encoded in CLAUDE.md)

| Game state | Agent should read |
|------------|-------------------|
| Moves 1–10 | `knowledge/openings.md` — follow the repertoire while the opponent stays in book |
| Any time | `knowledge/principles.md` — the per-move checklist lives in CLAUDE.md; the file has deeper explanations |
| ≤ 12 pieces or queens off | `knowledge/endgames.md` |

## Content principles

- Lines in SAN, short and memorizable — the agent must *apply* them, not recite them
- Every opening line says **why** (the plan behind it), because the opponent will deviate
- Traps section: name, moves, and the tell-tale pattern to recognize
- Checklists over prose: LLMs follow numbered steps more reliably than paragraphs

## Measuring improvement

The feedback loop closes with [[Post-Game Analysis]]: after an agent game, the website's Stockfish analysis counts blunders/mistakes/inaccuracies. Iterate on the knowledge files, replay, compare counts. (Manually now; automated in Phase 4 — see [[LLM Tournament]].)

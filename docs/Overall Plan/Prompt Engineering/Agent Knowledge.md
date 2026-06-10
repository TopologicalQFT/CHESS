# Phase 3: Agent Knowledge

Part of [[Project Overview]]. Goal: make the agent play *better chess* purely through context — no engine assistance (Stockfish is reserved for [[Post-Game Analysis]] on the website, never available to the agent).

## Design

Knowledge lives as an **Obsidian-style vault of atomic notes** the agent reads on demand — one concept per file, `[[wikilinks]]` between related notes, folders per topic:

```
agent_arena/knowledge/
├── Knowledge Index.md           # Entry point, links by game phase
├── openings/
│   ├── Openings Index.md        # Routing table: opponent's move → which note
│   ├── Opening Principles.md · Opening Traps.md
│   └── Italian Game.md · Sicilian Defense.md · French Defense.md ·
│       Caro-Kann Defense.md · Ruy Lopez as Black.md · Queens Gambit Declined.md
├── middlegame/
│   ├── Middlegame Index.md
│   ├── Move Selection Checklist.md   # the core per-move routine
│   ├── Tactical Patterns.md · Position Evaluation.md
│   └── Plans by Position Type.md · LLM Blunder Modes.md
└── endgames/
    ├── Endgames Index.md
    ├── Endgame Golden Rules.md
    ├── K+Q vs K.md · K+R vs K.md · Minor Piece Mates.md · Rook Endgames.md
    └── king-and-pawn/
        ├── King and Pawn Index.md
        └── The Square Rule.md · Opposition.md · Rook Pawn Draws.md
```

Why atomic notes instead of big files:
- The agent reads exactly what the position demands (one opening note, one endgame note) — minimal context per turn
- `[[wikilinks]]` let notes route to each other (Traps ↔ Italian Game, Rook Endgames → King and Pawn) and render as a graph in Obsidian
- Easy to iterate per-concept: a bad K+R technique fix touches one small file
- **This is the tournament's "context" dimension**: a tournament entry = CLAUDE.md variant + knowledge set. Comparing "no knowledge" vs "principles only" vs "full vault" agents is a Phase 4 experiment.

The agent resolves `[[Name]]` → `knowledge/**/Name.md` via Glob (instructions in arena CLAUDE.md).

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

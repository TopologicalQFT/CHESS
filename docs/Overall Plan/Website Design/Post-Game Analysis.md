# Post-Game Analysis

Website feature for [[Chess Webpage]]: after a game ends, either player can run a Stockfish analysis of the full game. The engine is **server-side only** — agents can never call it (see [[Agent Knowledge]]).

## Flow

```
Game ends → GameOverOverlay shows "Analyze game"
  → client POSTs the game PGN to /analyze
  → server replays the game, Stockfish evaluates every position
  → client switches to Review view:
      eval graph + annotated move list + steppable board
```

## Server

- `server/analysis.py` — wraps `chess.engine` (UCI):
  - Engine binary path from `STOCKFISH_PATH` env; default `engines/stockfish.exe` (local, git-ignored) / `/usr/games/stockfish` (Docker: `apt-get install stockfish`)
  - Per-position budget: `movetime` ~80 ms (configurable) — a 60-move game analyzes in ~10 s even on Render's free tier
- `POST /analyze` body `{ "pgn": "1. e4 e5 ..." }` → response:

```json
{
  "moves": [
    {
      "san": "e4", "uci": "e2e4", "ply": 1,
      "eval_after": 35,            // centipawns, White's POV, mate capped ±1000
      "best_san": "e4",            // engine's preference in the position before
      "cp_loss": 0,                // how much this move lost vs best
      "class": "good"              // good | inaccuracy | mistake | blunder
    }
  ],
  "fens": ["rnbq.../start", "...after each ply"],
  "summary": { "w": {"blunders": 1, "mistakes": 2, "inaccuracies": 3, "acpl": 45},
               "b": { ... } }
}
```

- Classification by centipawn loss: ≥300 blunder, ≥100 mistake, ≥50 inaccuracy
- `acpl` = average centipawn loss (the headline "how well did you play" number)

## Client (Review view)

```
GameOverOverlay
└── "Analyze game" button → AnalysisView (replaces board area)
    ├── ReviewBoard          # read-only SVG board at the selected ply
    ├── EvalGraph            # SVG area chart of eval_after over plies, clickable
    ├── AnnotatedMoveList    # moves with ?! ? ?? marks, colored; click to jump
    ├── SummaryRow           # per-player: blunders / mistakes / inaccuracies / ACPL
    └── ◀ ▶ navigation       # step through plies (also arrow keys)
```

- Blunders highlighted red in both the graph and the list; clicking jumps the board there
- "Best was Nf3" hint shown for any move classified mistake or worse

## Constraints

- Free-tier Render: single shared CPU — analysis is sequential, keep movetime low; show a progress state in the UI while waiting
- Engine version doesn't matter much at 80 ms/move (Debian's apt Stockfish is fine)
- Analysis is stateless: PGN in, JSON out — no DB needed yet

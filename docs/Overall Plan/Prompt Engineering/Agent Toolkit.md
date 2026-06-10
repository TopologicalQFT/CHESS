# Agent Toolkit

Part of [[Agent Knowledge]] / [[Project Overview]]. The "upgrading the agent" half of the player-vs-table principle.

## The principle: player vs table

> **The interaction MCP is the table, not the player.** It serves rules-level state (position, legal moves, history, result) identically to every agent — formatting allowed, analysis forbidden. Anything that helps *thinking* is part of the **agent**: a declared, swappable component like its prompt and knowledge vault.

An agent (tournament entry) is therefore:

```
Agent = Model + CLAUDE.md + Knowledge vault + Agent Toolkit config
Shared = Interaction MCP (chess) + Chess server        ← same for everyone
```

## Design: stateless, FEN-in

Toolkit tools take the **FEN as a parameter** — the toolkit has no connection to the chess server and no game state. Consequences:
- It analyzes the position the agent *gives it* (its honest current understanding), not a privileged live feed
- Pure functions over python-chess — trivially testable, no lifecycle
- Per-agent equipment: a tournament entry's `.mcp.json` declares which toolkit (if any) it gets

## The hard line inside the toolkit

**Board geometry: yes. Judgment: no.** "Is b5 defended?" is a fact. "Is Qxb5 good?" is an evaluation — forbidden. No Stockfish, no scoring, no move recommendations, no ranking.

## Tools

### Tier 1 (built)
| Tool | Returns | Targets blunder mode |
|------|---------|---------------------|
| `preview_move(fen, move)` | Resulting position; YOUR pieces left attacked-and-undefended; opponent's checks & captures in reply | #8 self-opened lines, #2 miscounted exchange |
| `inspect_square(fen, square)` | Occupant; attackers and defenders by color, listed by piece | #9 phantom trade, the "(defended)?" question |
| `list_loose_pieces(fen)` | Both sides' pieces that are attacked with no defenders, or attacked by a cheaper piece | #4 forgotten hanging piece |
| `opponent_replies(fen)` | If you passed: every check and capture the opponent could play | #3 missing their threat |
| `pinned_pieces(fen)` | Absolutely pinned pieces, both colors, with the pinning piece | #1 moving a pinned piece |
| `imagine_start` / `imagine_move` / `imagine_undo` / `imagine_show` | **The imagination board** (user idea): a stateful virtual board seeded from any FEN — walk lines forward with per-move validation and danger facts at each stop, undo to branch | #12 combinations built on illegal moves; replaces error-prone prose calculation |

Note on statefulness: the imagination board is the one stateful part of the toolkit — deliberate, since the toolkit is per-agent equipment (the agent's own head), not the shared table. It's seeded explicitly from a FEN each calculation, so it never has privileged access to the live game.

### Tier 2 (candidates — not built yet)
- `exchange_count(fen, square)` — full capture-sequence material count on one square (static exchange). Deterministic but it *is* the calculation skill itself; the strongest crutch. Should be its own tournament dimension if added.
- `square_rule(fen, pawn_square)` — can the defending king catch this passed pawn ([[The Square Rule]] as a function)
- `repetition_status(fen + history)` — threefold/fifty-move proximity (needs history, not just FEN)

### Banned forever
Engine evaluation, best-move hints, threat *ranking*, plans. That's the player's job — or the website's, after the game ([[Post-Game Analysis]]).

## Why per-agent toolkits matter (Phase 4)

Entries become honestly labeled configurations:
- *Claude / full vault / no toolkit* — pure calculation test
- *Claude / full vault / Tier 1* — does cheap fact-checking reduce blunders?
- *Claude / no vault / Tier 1* — tools without knowledge?

Whether tool access compensates for weaker models becomes a measurable question. Tool-call counts per move are also a free metric (does a stronger prompt *reduce* tool dependence?).

## Origin

Every Tier 1 tool maps to a blunder the agents actually committed and documented in `agent_arena/suggestion/` (queen lost to a self-opened e-file; "trades" without a recapturing piece; repeated queen-grab bait). The toolkit is the granted form of their `(defended)` annotation request — granted as agent equipment, rejected as interaction-side help, per the principle above.

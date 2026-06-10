# Token Efficiency

Ways to cut tokens per move and per game. Context grows with every tool round-trip,
so the levers are: fewer round-trips, smaller reports, less re-reading.

> ✅ **Implemented 2026-06-10 (dev session):** per-move history truncated to recent plies (full PGN via `get_board`); CLAUDE.md now states the wait report is authoritative (no follow-up `get_board`) and sets the one-line-commentary-per-move policy. "Still waiting" replies stay minimal as requested.

## 2026-06-10 — Truncate `History:` in the per-move report

The move history is repeated in full in *every* `wait_for_my_turn` board report, so
its cost grows quadratically with game length. A 60-move game replays the whole PGN
~60 times. Suggestion: show only the last 6–10 plies in the per-move report
(`History (last 8): ... 7. Bb3 Bg4 8. h3 Bh5`) and keep the full PGN available via
`get_board` for when the agent actually wants it.

## 2026-06-10 — Keep "still waiting" replies minimal (works well today)

`wait_for_my_turn` timing out returns one short line, not a board. That's exactly
right — a human thinking for 5 minutes costs ~6 cheap round-trips, not 6 board
diagrams. Preserve this property in any bridge rewrite.

## 2026-06-10 — Don't make the agent call `get_board` after `wait_for_my_turn`

The wait already returns the full report, so `get_board` is only for recovery
(rejected move, lost context). CLAUDE.md could state this explicitly: "the report
from `wait_for_my_turn` is authoritative; don't follow it with `get_board`."

## 2026-06-10 — Agent-side: one line of commentary per move

User-facing narration each move ("You replied e5, I'll develop...") is nice but adds
up. The standing prompt could set the policy: at most one short line per move,
detailed commentary only at game end (or when the user asks). Cheap games by default.

## 2026-06-10 — Keep knowledge notes small and read-once

The `knowledge/` indexes already say "read the note for the opening on the board,
don't read them all" — good. Keep each note under ~80 lines so a game reads at most
one opening note + maybe one endgame note. Avoid an "everything" note the agent is
tempted to load every game.

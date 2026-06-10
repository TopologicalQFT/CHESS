# Board Report Improvements

Changes to the report returned by `wait_for_my_turn` / `get_board` that would reduce
agent mistakes. (See [[Token Efficiency]] for size-related changes.)

> ✅ **All three implemented 2026-06-10 (dev session):** "Opponent played: <san>" line with CAPTURE/CHECK callouts; legal moves grouped into Captures/Checks/Quiet; "Material:" balance line. The material line doubles as the Phase 3 experiment hook suggested below.

## 2026-06-10 — Call out the opponent's last move explicitly

Today the report only shows the last move implicitly, as the tail of `History:`. The
strategy checklist starts with "why did the opponent make their last move?", so make
it impossible to miss:

```
Opponent played: 9...Bxe3 (captured your bishop on e3)
```

One line, near the top. Flagging captures/checks ("captured your X", "you are in
check") is the high-value part — misreading whether a move was a capture is a classic
blunder source.

## 2026-06-10 — Annotate the legal move list

The flat SAN list (`Ng5, Nxe5, Nh4, ...`) is correct but unstructured. Grouping it
makes candidate selection faster and cheaper:

```
Captures: Nxe5, Bxf7+
Checks:   Bxf7+
Quiet:    (rest, grouped by piece)
```

SAN already encodes `x` and `+`, but surfacing the buckets saves the agent from
re-deriving them every move.

## 2026-06-10 — Show material balance

A single line like `Material: even` or `Material: you are up a knight for two pawns`
prevents slow drift into "I think I'm winning?" hallucinations, and is cheap to
compute server-side. Could be a Phase 3 experiment: does it measurably reduce
blunders?

> ⚖️ **Defended-targets annotation: REJECTED interaction-side, GRANTED as agent equipment (2026-06-10 dev session).** Principle: the interaction MCP is the table, not the player — it serves rules-level state identically to everyone; analysis (attack/defense relations) is the agent's job. The information you asked for is now available via your own `chess-toolkit` MCP: `inspect_square(fen, square)` and `preview_move(fen, move)`. Spending a tool call on it is your decision and part of your measured behavior. See docs/Overall Plan/Prompt Engineering/Agent Toolkit.md.

## 2026-06-10 — Mark defended targets in the Captures list (game 2 observation)

The new grouped `Captures:` line is great, but it baits material grabs: in game 2
the report kept listing `Qxb5` and `Qxd5` for many consecutive moves while both
pawns/pieces were defended (`Qxb5 axb5` / `cxb5` just loses the queen). The agent
must re-derive "is the target defended?" every single move, and twice I nearly
didn't. Cheap fix: annotate captures of defended targets:

```
Captures: Rxa7 (free), Qxb5 (defended by a6), Nxe5 (defended by Nc6, Qe6)
```

Even just `(defended)` vs `(undefended)` would kill the most common one-move
queen-grab blunder, while leaving real calculation to the agent.

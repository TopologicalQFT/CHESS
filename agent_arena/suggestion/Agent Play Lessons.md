# Agent Play Lessons

Self-review after games: near-blunders the agent caught (or didn't), the reasoning
failure behind each, and what prompt/knowledge change would prevent it. Candidate
material for `knowledge/middlegame/LLM Blunder Modes.md` and the CLAUDE.md strategy
section.

## 2026-06-10 — Game 2 (W vs agent Claude, won Q-for-R then a piece, +7 by move 30)

Play was clean on the board, but **three near-blunders happened in calculation** and
were only caught by explicitly checking the resulting square. Each is a recurring
LLM failure shape worth naming:

### 1. Disappearing defender (almost played 24. g4??)
With my knight on f3 and rook attacked on f5, `g4` looked like a free tempo — but
g2 was the *only* defender of f3, and g2→g4 un-defends it: 24. g4?? Rxf3 and
nothing recaptures (queen's 3rd-rank path was blocked by my own bishop). A move
earlier the identical push was fine. **Rule:** before any pawn push near the king,
list what the pawn defended from its *old* square; re-verify, don't reuse, last
move's safety conclusions.

### 2. Phantom fork (almost played 29. Nb6??)
Nb6 "forks rook and knight" — except the enemy knight on d5 *defends* b6, and I had
no recapture: Nb6?? Nxb6 just drops a piece. I had even mislabeled it "trades
knights" — a trade requires a recapture. **Rule:** a fork/outpost square must pass
two checks: (a) is the destination attacked, and (b) if it's attacked, does any of
my pieces recapture? "Forking" from an undefended square is just hanging a piece
with tempo.

### 3. Legal-capture bait (Qxb5 / Qxd5, several moves running)
The report's `Captures:` list faithfully includes captures that lose the queen to a
pawn recapture. Legal ≠ safe; suggested a `(defended)` annotation in
[[Board Report Improvements]].

### What went right (keep doing)
- E-file alertness: 16. Rxe6! (queen for rook) came from scanning *my* captures
  after the opponent opened the file — the checks/captures/threats step works.
- Open-file follow-through: 21. axb5 → 22. Rxa7 won the loose a7 bishop; "what did
  their recapture stop defending?" is a question worth asking every exchange.
- Conversion discipline: up +7, declined two tempting sacrifices (Bxh6, Qh7+ raid)
  after finding the refutation (...Nf4+ fork resource); chose Kg2/b3 consolidation
  instead. Boring wins convert.

### Suggested knowledge edit
Add "disappearing defender" and "phantom fork" as named entries in
`knowledge/middlegame/LLM Blunder Modes.md` with the two-check rule from #2 —
they're more specific than the generic "verify your move" advice and match how the
mistakes actually almost happened.

> ✅ **Implemented 2026-06-10 (dev session):** added as modes 10 and 11 in
> `knowledge/strategy/LLM Blunder Modes.md` (note: the file moved to strategy/),
> with your near-miss examples. The legal-capture-bait item (#3) was resolved via
> the new `chess-toolkit` MCP — see the note in [[Board Report Improvements]].

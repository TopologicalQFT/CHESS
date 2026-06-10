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

> ✅ **All three implemented 2026-06-10 (dev session):** (1) chained-preview combination rule added to the CLAUDE.md routine + blunder mode 12 in both variants' vaults (with your knight-geometry corollary — Nb6 and Nxf6+ are cited); (2) [[Blitz Protocol]] adopted as a standing CLAUDE.md section, and the clock is now visible in board reports (shipped minutes before your note); (3) narration policy now states: only played-and-verified moves, never calculated futures.

## 2026-06-10 — Game 4 (W vs human, 5-min blitz, LOST: flag fall + queen blunder)

Two independent failures, both mine. User's words: "why do you use so much time
every move? its a blitz"; "you halucinate too much on taktics".

### 1. The blunder: a combination built on an impossible move (8. Nxe5??)
I played 8. Nxe5 having "calculated" 8...Bxd1 9. Nxf6+ regaining the queen.
**e5→f6 is not a knight move** (it's a one-step diagonal). The combination's
linchpin was geometrically impossible, and I even announced the line in chat
before the opponent refuted it by simply playing 8...Bxd1.

Failure shape: **I verified move 1 of my combination with `preview_move`, but
never verified move 2 — the move the whole line depended on.** The toolkit
accepts ANY fen: I could have called
`preview_move(<fen after 8...Bxd1>, "Nxf6+")` — taking the FEN from the first
preview's output — and it would have answered "not legal". One extra call,
queen saved.

**Rule: in any forced line, the regaining/punchline move must be
toolkit-verified on the projected FEN before playing move 1.** A combination is
only as legal as its least-checked move. Corollary for knight geometry
specifically: a knight move is valid iff (file-diff, rank-diff) is (1,2) or
(2,1) — e5→f6 is (1,1). Compute this explicitly for every knight move in a
calculated line; knight-move hallucination is now my single most repeated error
(see also game 2's Nb6 "fork" — same piece, same failure).

### 2. Time management: I played a 5-minute game like a correspondence game
What ate the clock, in order of cost:
- **Long calculation monologues** on non-critical moves — multi-branch trees,
  written out, with errors that then needed re-derivation. Minutes per move.
- **A chat message after nearly every move.** Each `send_chat` is a tool
  round-trip on MY clock once it's my turn.
- **Toolkit calls on moves that didn't need them** (book recaptures).
The triage table (GREEN ≈ 10s) exists in CLAUDE.md, but nothing in my behavior
actually changed when the room had a clock — I never even knew how much time I
had left, because the board report doesn't show the clock (see
[[Board Report Improvements]]).

Proposed blitz protocol → [[Blitz Protocol]].

### 3. Don't announce unverified lines in chat
The chat bragging "if Bxd1, Nxf6+ regains the queen" published a hallucination.
Narration is for moves already played and verified, never for calculated
futures — which CLAUDE.md already says, and I violated by explaining my
combination's intent. If the reasoning for a move IS a forced line, verify the
line before narrating it.

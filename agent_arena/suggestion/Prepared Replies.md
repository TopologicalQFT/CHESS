# Prepared Replies

> ✅ **Adopted 2026-06-10 (dev session):** both variants' CLAUDE.md now have a "Continuity" section — PLAN/PREP committed as compact lines at the end of every turn's reasoning, PREP-hit check as step 0 of the routine (verified preps play in seconds; surprises void the prep), quiet-reply-to-quiet-move plan persistence, and think-on-the-opponent's-clock for timed sharp positions. This addresses the user's core observation that "continuity of policy" was the missing ingredient behind slow moves.

User observation (2026-06-10, after game 4): a player who calculated "if he plays X,
I answer Y" should answer Y in ~3 seconds when X actually appears. The agent doesn't
do this — every turn restarts analysis from scratch, even when the opponent played
exactly the predicted move.

## Why the behavior is missing (diagnosis)

1. **Prior analysis is distrusted by default.** The agent's own last-turn
   calculation is in context but error-prone, so it re-derives rather than reuses —
   paying full thinking cost for positions it already solved.
2. **Predictions are never committed in a retrievable form.** "If X then Y" is
   buried in prose; there is no compact artifact next-turn-me can read and act on.
3. **The routine mandates from-scratch thinking.** The five-step per-move routine
   has no step 0: "did they play what you prepared for?" So even book recaptures
   re-enter the full loop.
4. **Idle on opponent time.** Between `wait_for_my_turn` calls the agent does no
   thinking; a human calculates on the opponent's clock for free.

## Proposed protocol (CLAUDE.md candidate)

**When committing a move, also commit the prep.** After choosing a move via
calculation, end the turn's reasoning with one compact line:

```
PREP: if exd5 → Rxe2+ (verified) | if e5 → Nd7 | else → full routine
```

**Next turn, step 0 of the routine:** compare "Opponent played:" against the PREP
line. On a hit — and if the report shows no new CAPTURE/CHECK flag beyond what the
prep assumed, and the prepared move is in the legal list — play it immediately.
That's the ~3-second followup move. On a miss, run the normal routine.

Rules to keep it honest:
- A prepared reply may only be played fast if it was **verified when prepared**
  (previewed on the projected FEN — see the combination rule in
  [[Agent Play Lessons]]). Unverified preps must say "(check first)".
- Any surprise in the report (unexpected capture flag, material change) voids the
  prep entirely.

**Think on the opponent's clock.** When `wait_for_my_turn` times out and the
position is sharp, spend the next interval predicting their top 2 replies and
preparing answers — then the PREP line already exists when the report lands. Costs
tokens; in timed games it converts to clock time saved, which is the scarcer
resource.

Related: [[Blitz Protocol]] (prep-hits are the natural GREEN moves of blitz),
[[Board Report Improvements]] (the clock line makes the tradeoff visible).

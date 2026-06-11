# Counting Exchanges — numbers, never prose

"I take, they take, I take — wins material" is how queens get donated. Exchange counting is ARITHMETIC, and arithmetic done in prose hallucinates. Do it like an accountant.

## The method (for captures on one square)
1. **List the attackers of the square, both sides, by value ascending.** Yours: "P(1), N(3), R(5)". Theirs: "P(1), Q(9)". Derive the list square by square from the diagram in the report, writing each attacker explicitly — never from memory.
2. **Simulate cheapest-first**: each side recaptures with its LEAST valuable attacker (capturing with the queen first is how queens die to pawn recaptures).
3. **Write the running tally as numbers after every capture**: "PxN: +3. pxP: +3−1=+2. NxP: +2+1=+3. qxN: +3−3=0." No words like "winning" until the sequence ENDS.
4. **Either side may STOP recapturing** the moment continuing loses material — check at each step: "would I/they recapture here, or stand pat?" The sequence ends at the best stopping point, not at the last possible capture.
5. The final number is the verdict. "+1" is the answer; "wins a pawn I think" is not an answer.

## Overlapping trades — the ledger poison
If a NEW capture sequence starts while a previous exchange is still open (recapture pending), incremental tallies double-count the pending recapture (blunder mode 14 — it cost a knight). **Rule: settle the verdict on the FINAL position's TOTAL material**, never by adding deltas across trades. And X-RAY pieces (R/Q behind your own attacker on the line) are full attackers — count batteries back-to-front (mode 15).

## Three mandatory cross-checks
- **Every defender's line must be CLEAR**: trace each slider-defender's path to the square piece by piece — your own pieces block it too (mode 16, the phantom defender).
- **The recapturer must exist and be legal**: name the exact piece making each capture, verify its geometry (a "defender" that's king-pinned doesn't count — check the king's lines yourself).
- **After the dust settles, run the hanging scan on the FINAL position** (from your final written stepping stone): winning the exchange while leaving your back rank open is not winning.

Related: [[Stepping Stones]] · [[Forcing Moves First]]

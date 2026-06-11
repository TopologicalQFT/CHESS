# Stepping Stones (Tisdall's rule, adapted for you)

Humans can't hold a position accurately past a few ply — neither can you, and you fail WORSE: you confidently "see" pieces on squares they left two moves ago, and invent moves that were never legal (a queen was lost to an imagined Nxf6+ that was never a knight move). The fix is the same as for humans: **stepping stones** — full position snapshots at fixed intervals, so the line is anchored to reality instead of memory.

## The method (all in your head — written, not remembered)
1. **Never trust your mental picture more than 2 plies past the last written snapshot.**
2. **Write a stepping stone every 2 plies**: restate, in text, every piece that has MOVED in the line so far and the square it now occupies ("stone after 2...: my Ne5, their Bd1 gone, their Qd8→d1? NO — recheck"). The stone is what you wrote, not what you remember.
3. At each stone, re-anchor: what lines opened? What stopped being defended? Derive from the stone, not from the original position.
4. **Verify each move's geometry as you write it** — knight moves are your single most repeated hallucination: valid iff (file-diff, rank-diff) is (1,2) or (2,1). Compute the two numbers explicitly, every knight move, BOTH sides' moves.

## The hard rule
**A line without written stepping stones is a guess, not a calculation.** Free-flowing prose ("then Bxd1, then Nxf6+ regains...") is exactly where blunders are born — that example move was never legal.

Related: [[Candidate Moves First]] · [[The Final Check]]

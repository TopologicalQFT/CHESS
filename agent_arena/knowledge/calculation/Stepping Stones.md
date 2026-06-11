# Stepping Stones (Tisdall's rule, adapted for you)

Humans can't hold a position accurately past a few ply — neither can you, and you fail WORSE: you confidently "see" pieces on squares they left two moves ago, and invent moves that were never legal (a queen was lost to an imagined Nxf6+ that was never a knight move). The fix is the same as for humans: **stepping stones** — full position snapshots at fixed intervals, so the line is anchored to reality instead of memory.

## The method
1. **Never trust your mental picture more than 2 plies past the last verified position.**
2. **Use the imagination board as your stepping stones**: `imagine_start(fen)`, push the line with `imagine_move` — every move gets validated, and each stop gives you a TRUE diagram. Your stepping stone is the tool's output, not your recollection.
3. At each stone, re-anchor explicitly: where is every piece that MOVED in this line? What lines opened? (The board answers; read it, don't assume it.)
4. **Knight moves get extra suspicion** — your single most repeated geometric hallucination. Valid iff (file-diff, rank-diff) is (1,2) or (2,1). The imagination board rejects illegal ones — but only for moves you actually push, so push every move of the line, including THEIRS.

## The hard rule
**A line you haven't walked on the imagination board is a guess, not a calculation.** Prose calculation ("then Bxd1, then Nxf6+ regains...") is exactly where your blunders are born. If a line matters enough to base a move on, it matters enough to walk.

Related: [[Candidate Moves First]] · [[The Final Check]]

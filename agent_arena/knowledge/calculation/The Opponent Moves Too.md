# The Opponent Moves Too (refutation-first)

The deepest calculation bias: lines continue with the reply you HOPE for. You calculate your idea three moves deep against an opponent who cooperates — while their actual best move refutes you at ply one.

## The method
1. For every candidate move, **search for the refutation FIRST** — before admiring what the move achieves. Ask: "if I were them, how would I punish this?" Their checks, their captures, their counter-threats ([[Forcing Moves First]], from their side).
2. **Assume they see everything.** Calculate against their best, not their plausible. A trap that "they might fall for" is a bonus, never a justification.
3. **The verdict of a line is its WORST position for you**, not its happiest end. If your combination wins a pawn but allows one drawing resource, the verdict is "drawish", not "+1".
4. When their best reply is unclear, that's RED-flag information by itself: a move whose consequences you can't pin down is a gamble, and gambles need either a winning floor ("worst case I'm equal") or desperation to justify them.

## Mirror duty
Run this same refutation-first search on THEIR last move in Step 1: "what was their best idea behind it?" — not "what's the laziest reading of it?" A quiet move analyzed lazily is how mating attacks get labeled "routine regrouping" (game 5).

Related: [[Candidate Moves First]] · [[The Final Check]]

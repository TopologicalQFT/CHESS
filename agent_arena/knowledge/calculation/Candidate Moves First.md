# Candidate Moves First (Kotov's discipline)

The #1 calculation error is diving into the first attractive move, calculating deep, finding a problem, jumping to another move, half-calculating, jumping back. That wastes time AND produces hallucinations — by the third jump, your mental position has drifted.

## The method
1. **Before calculating ANYTHING, write the candidate list.** 2–4 moves, drawn from: your captures/checks that the hanging scan makes interesting, moves serving your plan, moves answering their idea. Write them down explicitly: "Candidates: Nf5, d4, a4."
2. **Calculate each candidate ONCE, completely, then verdict it.** One line at a time, to a quiet position, verdict in numbers/facts ("d4: leads to = position, my e-file pressure persists").
3. **Never re-enter a calculated branch.** If you verified it once, trust the written verdict. Re-calculating the same line twice is how clocks die (game 5) — and the second pass is usually WORSE than the first because position drift has set in.
4. Compare verdicts; play the best; the runner-up's verdict becomes a scenario note.

## LLM adaptation
Your "tree" lives in tokens, and tokens drift. The written candidate list is your anchor: after finishing each branch, return to the LIST, not to your memory of where you were.

Related: [[Forcing Moves First]] (what order within a branch) · [[Stepping Stones]] (keeping the position honest while deep)

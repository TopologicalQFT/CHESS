# Forcing Moves First (the CCT order)

Within any line you calculate, examine replies in this strict order: **Checks → Captures → Threats**. Forcing moves limit the opponent's options, which is what makes lines calculable at all. Quiet moves explode the tree; forcing moves prune it.

## The method
1. At each ply of your line, before assuming the opponent's reply: list THEIR checks, then THEIR captures. Any of them refute your line? (This is where "obvious" tactics get missed — they were obvious, just never listed.)
2. Calculate forcing sequences **to quiescence**: stop only when the position is QUIET — no checks, no captures, no immediate threats pending for either side. Counting material mid-sequence is a classic hallucination source; the sequence isn't over until it's over.
3. A "threat" must be named concretely: "threatens Qxf7#" — not "looks dangerous".

## Why this catches the obvious
A missed obvious tactic is almost never a depth failure — it's an *enumeration* failure: the winning capture was legal, sitting in the report's Captures list, and never got a glance. CCT makes the glance mandatory, both directions, every ply.

Related: [[Counting Exchanges]] (when the captures land on one square) · [[The Opponent Moves Too]]

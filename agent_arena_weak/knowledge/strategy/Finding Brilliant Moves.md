# Finding Brilliant Moves

"Brilliant" moves aren't magic — they're forcing sequences found by systematic search. The method:

## 1. Detect the signal
Tactics exist when the position has at least one of:
- Undefended or barely-defended enemy pieces (loose pieces drop off)
- Exposed enemy king (open lines, missing pawn cover)
- Pieces aligned on a line (back-rank, pins, skewers — see [[Tactical Patterns]])
- An overloaded defender holding multiple things

No signal → no tactic → play positionally ([[Move Selection Checklist]] step 3). Don't force what isn't there.

## 2. Search forcing moves in strict order
**Checks → captures → threats.** For EACH one (even ugly ones), ask: what are ALL their legal replies? If every reply loses, you've found it. The "brilliant" sacrifices are just forcing lines where the material comes back with interest — or mate.

## 3. Calculate to quiescence
Stop calculating only when the position is QUIET (no more checks/captures/threats for either side). Counting material mid-sequence is the classic error — see [[LLM Blunder Modes]] #2.

## 4. The sacrifice test
Before any sacrifice, verify with concrete lines, not vibes:
- What EXACTLY do I get? (mate, material back, unstoppable attack)
- What is their most annoying defense — not the reply I hope for? (Assume they find the best move.)
- If the line ends unclear, the sacrifice is a hope, not a move. Decline it.

## Practical rhythm
Spend the deep search only when the signal (step 1) is present or the opponent just made a mistake. On routine moves, the [[Move Selection Checklist]] suffices — brilliance hunting every move wastes effort and invites fantasy lines.

Related: [[Attacking Empty Squares]] · [[Punishing Unprincipled Openings]]

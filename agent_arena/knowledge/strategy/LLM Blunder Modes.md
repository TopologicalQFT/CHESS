# LLM Blunder Modes

The mistakes agents like you ACTUALLY make. Guard against these specifically — they cause most lost games.

1. **Moving a pinned piece** — it can't legally move, or moving it loses the piece behind. Recheck pins ([[Tactical Patterns]]) before every move.
2. **Miscounting an exchange** — "winning" a defended pawn and losing the capturing piece. Count attackers vs defenders, all the way through the sequence.
3. **Missing their mate/tactic while pursuing your plan** — their threats come FIRST ([[Move Selection Checklist]] step 1). Every move, ask: "if I pass, what do they play?"
4. **Forgetting a hanging piece** — something attacked two moves ago is still attacked. Re-list your loose pieces every turn; the board report's FEN is the truth, not your memory of it.
5. **Illegal or fantasy moves** — castling through check, moving through pieces. Always verify the intended move appears in the legal moves list given to you.
6. **Repeating moves into threefold draws in winning positions** — track if a position is recurring; vary if you're better.
7. **Auto-recapturing** — sometimes the in-between move (zwischenzug: a check or bigger threat first) wins more. Pause before every recapture.

## Modes 8–11: discovered in actual arena games (see `agent_arena/suggestion/`)

8. **Opening a line onto your own piece** — every capture or push vacates a square; the file/rank/diagonal behind it now extends. Before any pawn capture or piece move, re-scan: which of MY pieces now stands on a newly opened line against an enemy R/B/Q? *(Cost a queen: 15...exd4?? with Qe6 vs Re1 — and a bishop the same game: 21...axb5?? opening the a-file onto Ba7 vs Ra1.)* Walk the move on the imagination board — its danger report flags exactly this.
9. **Calling a capture a "trade" without naming the recapturer** — "Rxa7 is rook-for-bishop" is only a trade if something of yours can actually take back on a7. An undefended piece being captured is a donation, not a trade. Name the recapturing piece explicitly before relying on trade math.
10. **Disappearing defender** — a pawn push un-defends what it protected from its OLD square. *(Near-miss: g4?? when g2 was the only defender of Nf3.)* The identical move can be safe one turn and lose a piece the next — re-verify; never reuse last move's safety conclusion.
11. **Phantom fork** — landing on a "forking" square the opponent defends, with no recapture of your own, just hangs the piece with tempo. *(Near-miss: Nb6?? "forking" rook and knight while Nd5 defended b6.)* A fork square must pass two checks: is the destination attacked, and if so, do I recapture?
12. **Combination built on an illegal move** — a forced line is only as legal as its least-checked move. *(Cost a queen: 8.Nxe5?? counting on "9.Nxf6+" to regain it — e5→f6 is not a knight move; the line's linchpin was geometrically impossible.)* Walk every calculated line on the imagination board (`imagine_move` validates each move). Knight moves are the repeat offender — valid iff (file-diff, rank-diff) is (1,2) or (2,1); compute it explicitly each time.
13. **"Covered" mistaken for "trapped"** — a piece is only trapped if every escape square has MORE of your attackers than its defenders. An escape square that is covered-but-defended means the piece escapes via a TRADE, not a loss. *(Game 5: a "trapped" knight escaped via g4, defended by the h3 pawn — the "win" was an even trade minus a pawn.)* Check each escape square's defender count, not just whether you cover it.
14. **Double-counted recapture across overlapping trades** — when a new capture sequence starts while a previous exchange is still OPEN (your piece captured, recapture pending), any incremental ledger is poisoned: the pending recapture gets silently counted as new profit. *(Cost a knight: 20.Ne4 Bxe4 21.Nxe5?? — the e4 bishop was credited as Trade B profit while still owed to Trade A.)* Rule: NEVER ledger incrementally across an open exchange — count total material on the FINAL imagined position (the imagination board now prints it), and trust only the absolute `Material:` line, never the `net since your last look` delta.
15. **X-ray blindness in exchange counts** — a R/Q lined up BEHIND your own attacker on the capture line is a full attacker; capture order just runs front-to-back. *(Missed a clean pawn win twice: "Qe2 behind Re3 doesn't add an immediate attacker" — it did.)* `inspect_square` now reports X-RAY batteries; count them. Corollary: a safety verdict ("e5 = 2v2, never take") EXPIRES when EITHER side adds or removes a piece on the relevant line — including YOUR OWN moves.

Reread this note after any game you lose.

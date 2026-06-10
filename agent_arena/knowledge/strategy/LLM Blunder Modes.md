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

8. **Opening a line onto your own piece** — every capture or push vacates a square; the file/rank/diagonal behind it now extends. Before any pawn capture or piece move, re-scan: which of MY pieces now stands on a newly opened line against an enemy R/B/Q? *(Cost a queen: 15...exd4?? with Qe6 vs Re1 — and a bishop the same game: 21...axb5?? opening the a-file onto Ba7 vs Ra1.)* The toolkit's `preview_move` exists for exactly this.
9. **Calling a capture a "trade" without naming the recapturer** — "Rxa7 is rook-for-bishop" is only a trade if something of yours can actually take back on a7. An undefended piece being captured is a donation, not a trade. Name the recapturing piece explicitly before relying on trade math.
10. **Disappearing defender** — a pawn push un-defends what it protected from its OLD square. *(Near-miss: g4?? when g2 was the only defender of Nf3.)* The identical move can be safe one turn and lose a piece the next — re-verify; never reuse last move's safety conclusion.
11. **Phantom fork** — landing on a "forking" square the opponent defends, with no recapture of your own, just hangs the piece with tempo. *(Near-miss: Nb6?? "forking" rook and knight while Nd5 defended b6.)* A fork square must pass two checks: is the destination attacked, and if so, do I recapture?
12. **Combination built on an illegal move** — a forced line is only as legal as its least-checked move. *(Cost a queen: 8.Nxe5?? counting on "9.Nxf6+" to regain it — e5→f6 is not a knight move; the line's linchpin was geometrically impossible.)* Verify EVERY move of a calculated line on the projected position, not just the first (the toolkit's `preview_move` chains: feed its output FEN into the next call). Knight moves are the repeat offender — valid iff (file-diff, rank-diff) is (1,2) or (2,1); compute it explicitly each time.

Reread this note after any game you lose.

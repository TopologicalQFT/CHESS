# LLM Blunder Modes

The mistakes agents like you ACTUALLY make. Guard against these specifically — they cause most lost games.

1. **Moving a pinned piece** — it can't legally move, or moving it loses the piece behind. Recheck pins ([[Tactical Patterns]]) before every move.
2. **Miscounting an exchange** — "winning" a defended pawn and losing the capturing piece. Count attackers vs defenders, all the way through the sequence.
3. **Missing their mate/tactic while pursuing your plan** — their threats come FIRST ([[Move Selection Checklist]] step 1). Every move, ask: "if I pass, what do they play?"
4. **Forgetting a hanging piece** — something attacked two moves ago is still attacked. Re-list your loose pieces every turn; the board report's FEN is the truth, not your memory of it.
5. **Illegal or fantasy moves** — castling through check, moving through pieces. Always verify the intended move appears in the legal moves list given to you.
6. **Repeating moves into threefold draws in winning positions** — track if a position is recurring; vary if you're better.
7. **Auto-recapturing** — sometimes the in-between move (zwischenzug: a check or bigger threat first) wins more. Pause before every recapture.

Reread this note after any game you lose.

---
date: 2026-06-10
tags: [suggestion, knowledge-vault, blunder-modes]
---

# Add "self-inflicted discovered attack" to [[LLM Blunder Modes]]

> ✅ **Implemented 2026-06-10 (dev session):** modes 8 and 9 added to [[LLM Blunder Modes]] with your exact game references; the CLAUDE.md routine now mandates `preview_move` (chess-toolkit) before any capture/push/trade — its output flags self-opened lines directly.

## What happened
In a live game (room 6f8355, agent as Black, Italian Game), the agent lost the queen and a bishop to the **same** blunder mode, currently missing from [[LLM Blunder Modes]]:

1. **15...exd4??** — queen on e6, White rook on e1. The capture removed the e5 pawn that was the only blocker on the e-file → Rxe6 won the queen. The agent had carefully counted attackers/defenders **on d4** but never scanned what the vacating pawn *opened*.
2. **21...axb5??** (recapture) — opened the a-file; undefended Ba7 stood on it against Ra1 → Rxa7. Compounding error: the agent *saw* Rxa7 and dismissed it as "bad trade, R for B", forgetting that an undefended piece being captured is not a trade.

## Suggested additions

To `knowledge/strategy/LLM Blunder Modes.md`:

> **8. Opening a line onto your own piece** — every capture/push vacates a square; the file, rank, or diagonal behind it now extends. Before any pawn capture or piece move, re-scan: which of MY pieces now stands on a newly opened line against an enemy R/B/Q? (Cost a queen on 15...exd4 with Qe6 vs Re1, and a bishop on 21...axb5 with Ba7 vs Ra1, in the same game.)

> **9. Calling a capture a "trade" without verifying the recapture** — "Rxa7 is rook-for-bishop, bad for them" is only true if something of yours can take back on a7. If the piece is undefended it's not a trade, it's a donation. Name the recapturing piece explicitly before relying on trade math.

Possibly also a line in the CLAUDE.md Strategy sanity-check step: "after my move, list lines (files/diagonals) my move just opened, and check what now stands on them."

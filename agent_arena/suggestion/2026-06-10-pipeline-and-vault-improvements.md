---
date: 2026-06-10
tags: [suggestion, pipeline, mcp, vault, phase-3]
---

# Pipeline & vault improvements (from the 6f8355 post-mortem)

> ✅/⚖️ **Dev session response 2026-06-10:**
> 1. `preview_move` — **GRANTED as agent equipment**, not interaction-side: it lives in your new `chess-toolkit` MCP (with `inspect_square`, `list_loose_pieces`, `opponent_replies`, `pinned_pieces`). Principle: the interaction MCP is the table; anything that helps thinking is part of the agent and declared per tournament entry.
> 2. Checklist inlined into CLAUDE.md ✅ (with mandatory `preview_move` before captures/pushes/trades).
> 3. Blunder modes 8–9 added (plus 10–11 from Agent Play Lessons) ✅.
> 4. Measurement loop — agreed; will be designed as the Phase 4 entry point.
> 5. `make_move` now echoes the resulting FEN + material ✅; piece-list representation logged as a Phase 3 experiment.

Context: agent blundered Q and B in one game via self-opened lines ([[2026-06-10-self-discovered-attack-blunder-mode]]). Vault fixed what reading can fix (opening, defensive doctrine); execution failures need tooling/prompt enforcement.

## 1. MCP: `preview_move(move)` — highest payoff
Server-side (python-chess) dry run of a candidate move, returning:
- resulting diagram/FEN
- agent's pieces left attacked & undefended ("after exd4: Qe6 attacked by Re1, no defenders")
- opponent's checks and captures available in reply

Deterministic board facts, not engine advice — keeps the experiment honest. Would have prevented both blunders this game. Passive alternative (weaker): add "your loose pieces / opponent's available captures" to `wait_for_my_turn` reports — but that audits the *current* position, not the post-move one where the blunders lived.

## 2. CLAUDE.md: inline the per-move routine
[[Move Selection Checklist]] is labeled "every move" but lives behind a read the agent skips under play pressure (it skipped it all game). Per-move material belongs in the standing prompt; the vault is for occasional reads (openings, endgames, doctrine). Add the missing step:
> Simulate your chosen move. List the lines the moving piece vacates and what now stands on them. For any "trade", name the recapturing piece.

## 3. Vault: patch [[LLM Blunder Modes]]
Add modes 8 (self-opened lines) and 9 (trade-without-recapturer) — drafted in the linked note. Principle: grow the vault from observed agent failures, not generic chess content; the repertoire-shaped notes ("play exactly this") outperform encyclopedic ones.

## 4. Phase 3 measurement loop
Post-hoc engine analysis of finished games (dev-side, not in-play): count eval-swing blunders, tag by game phase. A/B prompt/vault variants over ~10 games vs a fixed opponent. Without this, prompt iteration is anecdote-driven.

## 5. Minor
- `make_move` response echoes the new position (catch misimagined boards one move sooner).
- Experiment: piece-list representation ("White: Qc2, Ra7, Nc4, ...") alongside the ASCII grid — flat lists make alignments (Ra1/Ba7 on the a-file) easier for an LLM to spot.

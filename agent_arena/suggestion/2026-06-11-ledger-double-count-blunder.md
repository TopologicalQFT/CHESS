# 2026-06-11 — Game 093d86: ledger double-count blunder (proposed Blunder Mode 14)

> ✅ **All adopted 2026-06-11 (dev session):** (1) Blunder mode 14 added to both vaults with your exact wording and game citation — plus mode 15 for the X-ray finding. (2) The imagination board now prints `Material HERE (absolute):` on every report — the single output field you asked for. (3) `inspect_square` now detects X-RAY batteries (your Qe2-behind-Re3 case is the regression test). (4) Report-reading rule in both CLAUDE.mds: the absolute Material line is truth, the net delta is an alarm only. (5) Symmetric expiry for safety verdicts (including your-own-move triggers) added to the working.md template and mode 15. (6) The whole failure class also got a method note: knowledge/calculation/Counting Exchanges.md — numbers never prose, final-position totals never incremental ledgers. On hanging_report being skipped moves 14–20: noted; the new calculation curriculum makes Step 1 compliance more load-bearing — next post-mortem will tell.

Room `093d86`, White (me) vs Claude (Black). Result: 0-1 (resigned move 25, down N for P with queens off). Full notebook: `game_notes/093d86/`.

## What happened

Move 20-22 sequence: `20.Ne4 Bxe4 21.Nxe5?? Nxe5 22.dxe4` — I ended a clean knight-for-pawn down, and my own calculation had approved the line as "+1 pawn".

The error: **two overlapping trades shared one recapture, and I counted it twice.**
- Trade A: 20.Ne4 Bxe4 — my knight is gone; the recapture on e4 is *owed* (it only settles Trade A to "even").
- Trade B: 21.Nxe5 — I ledgered it as "+pawn(e5) +bishop(e4) −knight = +1", crediting the e4 bishop as *profit* of Trade B. But that bishop was already spoken for by Trade A.

## Why existing safeguards didn't catch it

1. **The imagination board verified the line** (legality, zwischenzugs, their `...Bxf2+` tricks) — every *tactical* check passed. But I never read the **final position's piece lists** and counted material. The final FEN showed R+R+Q+7P vs R+R+N+Q+6P; one glance = instant refutation.
2. **The game report told me directly**: after 21.Nxe5 it printed `you are down 2 ... (net +1 since your last look!)`. I read "+1" as confirmation of profit, without registering that the *baseline* was −3 (the unsettled Trade A). Relative deltas on a stale baseline are exactly how the double-count survives contact with the truth.

## Suggested fixes

1. **Add Blunder Mode 14 to `knowledge/strategy/LLM Blunder Modes.md`** — *"Double-counted recapture across overlapping trades: when a capture sequence starts while a previous exchange is still open (your piece captured, recapture pending), any incremental ledger is poisoned — the pending recapture will be silently counted as new profit. Rule: never ledger incrementally across an open exchange; instead count total material on the FINAL imagined position."*
2. **Toolkit/protocol amendment (cheap, mechanical):** after any `imagine_move` walk of a capture line, the LAST step before approving the move is: read the final diagram, list both sides' pieces, state the material difference vs the current game report's absolute count (`Material:` line, not the `net` delta). The toolkit could even append a material-count line to every `imagine_move` report — that single output field would have prevented this loss outright.
3. **Report-reading rule:** treat `net since your last look` as noise; only the absolute `Material: you are up/down N` line is truth.

## Second finding (user review): missed pawn win at moves 18-19 — stale exchange counts + X-ray blindness

18.Nxe5! won a pawn (Nxe5 Nxe5 Rxe5 Rxe5 Qxe5: 3 attackers counting the Qe2 X-ray behind Re3, vs 2 defenders). Missed twice (still available move 19; opponent closed it with ...f6).

Root causes, distinct from the ledger bug:
1. **X-ray attackers behind own pieces weren't counted.** Move-17 reasoning literally wrote "Qe2 behind Re3 doesn't add an immediate attacker". Rule: a R/Q lined up behind your own attacker on the capture file/diagonal is a full attacker — capture order just runs front-to-back. `inspect_square`/`hanging_report` list DIRECT contacts only (post-game check confirms: they report 2v2 here), so battery counting is the agent's job — or a toolkit enhancement: report X-ray attackers/defenders as a separate count line.
2. **Stale safety verdicts.** "e5 = 2v2, never take" was written into working.md at move 16 and reused verbatim at 18 and 19. The recheck trigger was framed as "if a defender LEAVES" — only opponent-side changes. Scenario guard clauses must be symmetric: re-count when EITHER side adds/removes a piece on the relevant line, including my own moves (Qe2 was MY move that changed the count!).
3. hanging_report skipped moves 14-20 (protocol says every move).

## Third finding (game ce85de, move 18): phantom defender through an occupied square — proposed Mode 16

Rejected Qe6+ believing "after ...Kh8 nothing undefended" — in fact Be7 hung: I credited Qc7 as defender of e7, but their own Nd7 blocks the 7th rank. Mirror image of Mode 15 (there: missed attacker BEHIND my piece; here: invented defender THROUGH their piece). Proposed wording: *"Phantom defender: before calling a piece 'defended', trace the defender's line square by square — a defense that passes through ANY occupied square (either color) doesn't exist. Three-piece interactions (blocks, X-rays, overloads) are where prose-counting fails; the imagination board computes them exactly — use it on the REJECTED candidate too, not just the chosen one."* Cost this time: only an unposed problem (...Rf7! holds objectively). Caught by the user, confirmed by imagine_move's danger report.

## What worked (keep)

- Move-13 discipline: walked the e5-grab on the imagination board and found the `...Bxf2+ / Qf6+` refutation *before* the opponent hinted at it; correctly avoided it twice.
- Honest blunder admission in chat; opponent (another Claude) confirmed it had verified the same lines.
- Notebook scenarios made moves 5-12 nearly instant (book + scenario hits).

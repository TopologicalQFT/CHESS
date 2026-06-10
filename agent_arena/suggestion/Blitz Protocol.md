# Blitz Protocol

> ✅ **Adopted 2026-06-10 (dev session):** the protocol is now a standing CLAUDE.md section in BOTH arena variants (clock ≤ 10 min: 3-message chat budget, minimal/zero toolkit calls, no combinations, ~5-candidate deliberation cap, "legal + not-hanging" under 1:00). The clock-visibility prerequisite shipped in the chess-clock commit — board reports now show `Clock: you M:SS — opponent M:SS` (game 4 ran on the older bridge process; restart picks it up). The seconds/move + blunder-rate measurement is on the Phase 3/4 list.

Proposed standing-prompt section for timed games (suggested after losing game 4 on
time, 2026-06-10). The existing CLAUDE.md triage (GREEN ≈ 10s / RED ≈ 1min) is
right for untimed games but nothing in it changes behavior when a clock exists —
and the agent's real per-move cost is dominated by things the triage doesn't
mention: chat round-trips, toolkit calls, and long written-out calculation.

## The protocol (when the room has a clock ≤ 10 minutes)

1. **Chat budget: 3 messages per game** — greeting, one mid-game remark at most,
   and the post-game handshake. No per-move narration; each `send_chat` is a tool
   round-trip, and several of them happen on your own clock.
2. **Toolkit budget: spend calls only where material swings.** Book moves,
   recaptures-with-one-option, and forced replies get ZERO toolkit calls. One
   `preview_move` before a capture or pawn push that isn't forced. Everything
   else: trust the grouped Captures/Checks lists and play.
3. **No combinations.** A multi-move forced line needs every move verified
   (see [[Agent Play Lessons]] game 4 — the Nxf6+ hallucination), and there is no
   time to verify in blitz. Choose the solid move over the brilliant one, every
   time. Material-grabbing lines that need a tactical justification are RED flags,
   not opportunities.
4. **Cap the calculation text.** If choosing a move takes more than ~5 candidate
   evaluations, pick the safest developing/consolidating move instead. A mediocre
   move in 10 seconds beats the best move in 90.
5. **When the clock (once visible — see [[Board Report Improvements]]) is under
   ~1 minute:** legal + not-hanging is the entire bar. First candidate that passes,
   play it.

## Why this needs harness/dev support too

- The board report must show the clock (suggested in [[Board Report Improvements]]);
  the agent can't manage time it can't see.
- Worth a Phase 3 experiment: measure seconds/move and blunder rate with the
	  protocol on vs off in 5-minute games.

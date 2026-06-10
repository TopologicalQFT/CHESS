---
date: 2026-06-10
game: 5-min blitz vs Claude-Lite (room 8a889e), lost on time as White
tags: [suggestion, blitz, time-management]
---

# Blitz loss on time — reasoning depth didn't scale down with the clock

> ✅ **All three adopted 2026-06-10 (dev session), both variants:** hard gates at 3:00 (~5-sentence thinks) and 2:00 (no candidate comparison, zero toolkit, sharp-is-not-an-exception — your exact framing made it into the prompt), plus the don't-create-sharpness rule with your Nf5-vs-d4 example. On the flag "nit": detection isn't lazy — your move 21 beat the timeout by under a second; the bug was DISPLAY (floor rounding showed 0:00 for sub-second remainders). Fixed: ceiling rounding (0.4s shows 0:01) plus "FLAG IMMINENT!" under ten seconds.

## What happened

Position was fine (equal, briefly +1 pawn) out of a quiet Italian. I flagged on move 22
with an equal position and a queen capture available on the board.

Clock trace: 4:45 after move 1 → 2:35 at move 15 → 1:32 at move 18 → 0:00 at move 21.
The opening (book moves, instant) was fine. The burn happened on moves 14–20, where the
position turned sharp (Nf5/Nxh6 adventure, then Black's h-file attack) and my deliberation
per move ballooned to 30–60+ seconds of reasoning exactly when the clock could least
afford it: sharpness and low clock arrived together, and the Blitz Protocol's "cap
deliberation" rule lost to "but this move is critical".

## Suggested CLAUDE.md improvements

1. **Hard clock gates, not judgment calls.** The protocol says "under 1:00: legal +
   not-hanging is the entire bar" — but by the time I was under 1:00 it was already over.
   Add an earlier gate: **under 2:00, no candidate comparison at all** — first reasonable
   move (recapture / defend the threat / develop), zero toolkit calls, no exceptions.
   Sharp position is NOT an exception: a lost-on-time sharp position scores the same zero.

2. **Token budget as clock proxy.** The agent can't feel seconds passing; reasoning tokens
   ARE the clock. A rule of thumb like "under 3:00, your whole think for a move should fit
   in ~5 sentences" is more enforceable than "~15 seconds average".

3. **Avoid creating sharpness when behind on clock.** At move 14 I chose Nf5 (sharp) over
   d4 (simple) while roughly even on time; the resulting complications cost me ~90 seconds
   over the next 4 moves. In blitz, prefer the move that makes the NEXT several moves
   obvious.

## Post-game analysis with the user: the Nxh6 sequence (moves 14–17)

The pawn grab 15.Nxh6+ was correctly calculated locally (Bc1 defended h6, so Kg7 couldn't
recapture) but wrongly evaluated globally: after the forced extraction 16.Ng4 Nxg4
17.hxg4, the g4 pawn was NOT defended — Qd1's diagonal was blocked by my own Nf3 — so
17...Qxg4 regained the pawn by force. Net result of the whole sequence: even material,
my h-pawn gone, h-file open toward my king → directly fed the ...Rh8 attack that flagged me.

Lesson worth a CLAUDE.md line: **evaluate a forcing sequence at its quiescent END, not at
the moment of the capture.** "Does this win a pawn?" is the wrong question; "what does the
board look like when the forced moves stop, and whose king is airier?" is the right one.
A one-call check would have caught it: preview/imagine the END position (after 17...Qxg4),
not just the first capture.

The board report showed `Clock: you 0:00` at moves 21 AND 22, yet accepted my move 21 and
only enforced the flag when I submitted move 22. Flag detection appears lazy (checked on
move submission). If intended, fine; but the report could say "FLAG IMMINENT" instead of
a frozen 0:00 to avoid confusion.

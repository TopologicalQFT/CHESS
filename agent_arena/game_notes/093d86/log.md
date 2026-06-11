# Log — append-only

<!-- One line per move worth remembering — decisions, warnings to future-you,
     things the opponent revealed:
       12. Bxe6 — removed the ...Bxh3 sac bishop (their plan defused)
       14. ...Rad8 — prepares ...d5. DON'T ignore.

     GAME OVER: append the result and a short post-mortem — what decided the
     game, and which notebook entry was wrong or missing ("the losing tactic
     was never in working.md tactic ideas", "plans.md was right but I
     abandoned it at move 18"). The dev session studies these to improve you. -->

13. exd5 — center resolved; verified e5-grab refutation (Bxf2+/Qf6+ fork) BEFORE opponent hinted it. Good discipline.
21. Nxe5?? — BLUNDER, -2 (N for P). Root cause: DOUBLE-COUNTED the dxe4 recapture. Be4 was payment for my FIRST knight (20.Ne4 Bxe4); I counted it again as profit in the Nxe5 zwischenzug ledger ("+P+B-N=+1" — the +B was already owed). The imagination board walk verified tactics but I never COUNTED PIECES on the final position. Lesson: after any walk, count material on the END position, don't trust the running ledger.
22. dxe4 — down N for P. Assets for the defense: passed e4 pawn, Q+R battery behind it, their b5/a6 fixed on light squares. Plan: activity, e-pawn as the drawing/winning card, avoid further trades of pawns-for-nothing, keep queens on.
23. Qe1 (declining trade) — but Qxe1+ forced it anyway: my Q was attackable with Rd8 backing; "decline the trade" needed a Q square NOT in contact, and there wasn't a good one (Qf3 fell to ...Rd3).
24. ...Rd2 — their rook reached the 2nd; a2 indefensible (Ra1 was spent on the recapture).

## RESULT: 0-1 — resigned at move 25 (user instruction; position was N-for-P down, queens off, enemy rook on the 2nd).

## Post-mortem
- THE losing moment: 21.Nxe5?? A double-counting error, not a vision error: I SAW all the tactics (their Bxf2+/Qf6+ resources, my zwischenzugs) but my material ledger credited dxe4 (the recapture OWED for 20.Ne4 Bxe4) as PROFIT of the new combination. Two overlapping trades, one recapture counted twice.
- The tool gap: the imagination board verified legality and tactics of the line, but I never COUNTED MATERIAL on the final imagined position. The walk's final FEN had me R+R+Q+7P vs R+R+N+Q+6P — one count would have killed the move instantly. The game report's "Material: you are down 2" even told me right after Nxe5 ("net +1" from a -3 baseline) and I misread the baseline.
- RULE FOR NEXT GAME (belongs in working.md template / CLAUDE.md suggestion): before playing any capture sequence, read the imagination board's FINAL position piece lists and count both sides. Never trust an incrementally-built ledger across overlapping trades.
- What went RIGHT: opening book discipline (moves 1-12 fast and sound), the move-13 verification that correctly refuted the e5 grab BEFORE the opponent hinted at it, b3/b4 positional play, honest blunder admission in chat, declining the queen trade per Defending Worse Positions (they forced it anyway — Qxe1+ was available; my 'decline' analysis missed that contact cuts both ways: attacking their queen meant mine was take-able).
- Opponent quality: strong — prepared ...Bxf2+ refutations, announced plans and followed them, instant clean conversion squeeze (Qd2 trade offer, Rd2 infiltration).

## Addendum (user review): the MISSED WIN at moves 18-19
18.Nxe5! (and again 19.Nxe5!) won a clean pawn: Nxe5 Nxe5 Rxe5 Rxe5 Qxe5 — 3 effective attackers (Nf3 + Re3 + Qe2 X-RAY BEHIND THE ROOK) vs 2 defenders (Nc6, Re8). Verified post-game on the imagination board: final position is piece-even, +1P, Qe5 untouchable (...Bxg2 Kxg2 Qd5+ fails to Qxd5 — the queen captures the forking checker).
Why missed — THREE stacked failures:
1. Move 17 reasoning explicitly said "Qe2 behind Re3 doesn't add an immediate attacker" — WRONG. Capture order on a file battery is front-to-back (N, R, then Q); an X-ray attacker behind your own piece counts fully.
2. working.md carried "e5 = 2v2, grab always loses" from move 16 and I REUSED the stale verdict at 18 and 19 verbatim. The note's recheck trigger was "if a defender leaves" — framed only around THEIR pieces changing. MY OWN Qe2 changed the count and nothing prompted a recount. Scenario notes need symmetric triggers: re-count when EITHER side's piece enters/leaves the relevant file/square.
3. hanging_report was only called at move 13 (protocol says every move) — though note its direct count also reads 2v2; X-ray battery counting is the agent's job, not the tool's.
The opponent SAW it: ...f6 (their move 19) was played exactly to add the third defender — chat: "e5 gets a pawn guard". The window was open for my moves 18 AND 19; I spent them on b3 and b4.
Bitter symmetry: my chat at move 17 announced the idea ("e-file weight on e5 — your one fixed target") and I never cashed it.
